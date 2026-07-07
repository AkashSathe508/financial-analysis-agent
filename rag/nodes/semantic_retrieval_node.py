from state.rag_state import RAGState
from rag.retrievers.semantic import retriever


def semantic_retrieval_node(state: RAGState):

    docs = retriever.invoke(
        state["rewritten_query"]
    )

    return {
        "semantic_docs": docs
    }
