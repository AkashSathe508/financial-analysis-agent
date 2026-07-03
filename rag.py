"""
Hybrid RAG pipeline over a financial PDF report.

Pipeline stages:
    1. Load & chunk the PDF.
    2. Build a FAISS (semantic) retriever and a BM25 (keyword) retriever.
    3. Fuse both result sets with Reciprocal Rank Fusion (RRF).
    4. Compress/extract only the relevant sentences from the top docs (LLMChainExtractor).
    5. Generate an answer with the LLM.
    6. Self-RAG style evaluation: judge whether the retrieved context was
       actually sufficient to support the generated answer.
"""

import os
from collections import defaultdict
from typing import List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.retrievers.multi_query import MultiQueryRetriever


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

PDF_PATH = "data/reports/Apple_2025_Annual_Report.pdf"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
LLM_MODEL_NAME = "llama-3.1-8b-instant"

RETRIEVER_TOP_K = 8
RRF_K = 60


# --------------------------------------------------------------------------- #
# Structured output schema for self-evaluation
# --------------------------------------------------------------------------- #

class SelfRAGDecision(BaseModel):
    decision: Literal["SUFFICIENT", "INSUFFICIENT"]
    reason: str


# --------------------------------------------------------------------------- #
# Document loading & chunking
# --------------------------------------------------------------------------- #

def load_financial_report(file_path: str) -> List[Document]:
    """Load a PDF report into a list of LangChain Documents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"PDF report not found at '{file_path}'. "
            "Check the path or update PDF_PATH."
        )
    loader = PyPDFLoader(file_path)
    return loader.load()


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """Split documents into overlapping chunks and tag each with a chunk_id."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    return chunks


# --------------------------------------------------------------------------- #
# Retrievers
# --------------------------------------------------------------------------- #

def build_vector_store(chunks: List[Document], embedding_model: HuggingFaceEmbeddings) -> FAISS:
    """Build a FAISS vector store from document chunks."""
    return FAISS.from_documents(documents=chunks, embedding=embedding_model)


def build_semantic_retriever(vector_store: FAISS, llm: ChatGroq, top_k: int = RETRIEVER_TOP_K):
    """Semantic retriever wrapped with multi-query expansion."""
    base_retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    return MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm,
        include_original=True,
    )


def build_keyword_retriever(chunks: List[Document], top_k: int = RETRIEVER_TOP_K) -> BM25Retriever:
    """BM25 keyword retriever, k matched to the semantic retriever for fair fusion."""
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = top_k
    return bm25_retriever


# --------------------------------------------------------------------------- #
# Fusion & compression
# --------------------------------------------------------------------------- #

def reciprocal_rank_fusion(
    retriever_results: List[List[Document]], k: int = RRF_K
) -> List[Document]:
    """
    Combine results from multiple retrievers using Reciprocal Rank Fusion (RRF).

    Args:
        retriever_results: List of lists of Documents (one list per retriever).
        k: RRF constant (default = 60).

    Returns:
        List[Document] sorted by fused score, descending.
    """
    scores = defaultdict(float)
    unique_docs = {}

    for docs in retriever_results:
        for rank, doc in enumerate(docs):
            doc_id = (
                doc.metadata.get("source", "")
                + "_"
                + str(doc.metadata.get("chunk_id", rank))
            )
            unique_docs[doc_id] = doc
            scores[doc_id] += 1 / (k + rank + 1)

    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [unique_docs[doc_id] for doc_id, _ in ranked_docs]


def compress_documents(
    query: str,
    documents: List[Document],
    compressor: LLMChainExtractor,
) -> List[Document]:
    """Extract only the query-relevant content from each document."""
    return compressor.compress_documents(documents=documents, query=query)


# --------------------------------------------------------------------------- #
# Hybrid retrieval orchestration
# --------------------------------------------------------------------------- #

def hybrid_retrieve(
    query: str,
    semantic_retriever: MultiQueryRetriever,
    bm25_retriever: BM25Retriever,
    compressor: LLMChainExtractor,
) -> List[Document]:
    """Semantic + keyword retrieval -> RRF fusion -> compression."""
    semantic_docs = semantic_retriever.invoke(query)
    keyword_docs = bm25_retriever.invoke(query)

    fused_docs = reciprocal_rank_fusion([semantic_docs, keyword_docs])
    compressed_docs = compress_documents(query, fused_docs, compressor)

    return compressed_docs


# --------------------------------------------------------------------------- #
# Answer generation & Self-RAG evaluation
# --------------------------------------------------------------------------- #

def generate_answer(llm: ChatGroq, query: str, context: str) -> str:
    """Generate a natural-language answer grounded in the retrieved context."""
    prompt = f"""Context:

{context}

Question:

{query}
"""
    response = llm.invoke(prompt)
    return response.content


def evaluate_answer(
    self_rag_llm,
    question: str,
    context: str,
    answer: str,
) -> SelfRAGDecision:
    """Judge whether the retrieved context fully supports the generated answer."""
    prompt = f"""
You are evaluating a Retrieval-Augmented Generation (RAG) response.

Your task is to determine whether the answer is fully supported by the retrieved context.

Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Rules:

1. If the retrieved context contains enough information to answer the question completely,
return SUFFICIENT.

2. If important information is missing from the retrieved context,
return INSUFFICIENT.

3. Do NOT judge writing quality.

4. Judge ONLY whether the evidence is sufficient.

Provide a short reason.
"""
    return self_rag_llm.invoke(prompt)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError(
            "GROQ_API_KEY not found. Set it in your .env file before running."
        )

    llm = ChatGroq(model=LLM_MODEL_NAME, temperature=0)
    self_rag_llm = llm.with_structured_output(SelfRAGDecision)

    # --- Load & chunk ---
    documents = load_financial_report(PDF_PATH)
    chunks = split_documents(documents)

    # --- Build retrievers ---
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = build_vector_store(chunks, embedding_model)

    semantic_retriever = build_semantic_retriever(vector_store, llm)
    bm25_retriever = build_keyword_retriever(chunks)
    compressor = LLMChainExtractor.from_llm(llm)

    # --- Retrieve ---
    query = "What are Apple's biggest business risks?"
    docs = hybrid_retrieve(query, semantic_retriever, bm25_retriever, compressor)

    print(f"Retrieved {len(docs)} compressed, relevant chunks.\n")
    for doc in docs:
        print("=" * 80)
        print(doc.metadata)
        print(doc.page_content)

    # --- Generate & self-evaluate ---
    context = "\n\n".join(doc.page_content for doc in docs)
    answer = generate_answer(llm, query, context)

    print("\n" + "=" * 80)
    print("ANSWER:\n", answer)

    evaluation = evaluate_answer(self_rag_llm, query, context, answer)

    print("\n" + "=" * 80)
    print("SELF-RAG EVALUATION:")
    print(f"  Decision: {evaluation.decision}")
    print(f"  Reason:   {evaluation.reason}")


if __name__ == "__main__":
    main()