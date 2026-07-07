from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from llms.groq import fast_llm

compressor = LLMChainExtractor.from_llm(fast_llm)


def compress_documents(query, documents):

    compressed_docs = compressor.compress_documents(
        documents=documents,
        query=query
    )

    return compressed_docs
