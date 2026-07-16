import logging

from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from llms.groq import fast_llm

logger = logging.getLogger(__name__)

compressor = LLMChainExtractor.from_llm(fast_llm)


def compress_documents(query: str, documents: list) -> list:
    """Compress documents using LLM chain extractor.

    Falls back to the original documents if compression returns an
    empty list (e.g. the LLM considers all content irrelevant).
    """
    if not documents:
        return documents
    try:
        compressed = compressor.compress_documents(
            documents=documents,
            query=query,
        )
        return compressed if compressed else documents
    except Exception as exc:
        logger.warning(
            "Contextual compression failed; returning original documents: %s", exc
        )
        return documents
