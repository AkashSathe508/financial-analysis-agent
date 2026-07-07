from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from rag.vectorstores.faiss_store import base_retriever
from llms.groq import fast_llm

retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=fast_llm,
    include_original=True
)
