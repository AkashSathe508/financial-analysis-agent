from state.rag_state import RAGState
from rag.retrievers.keyword import bm25_retriever


def keyword_retrieval_node(state: RAGState):

    docs = bm25_retriever.invoke(
        state["rewritten_query"]
    )

    return {
        "keyword_docs": docs
    }
