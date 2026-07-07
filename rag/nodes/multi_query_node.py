from state.rag_state import RAGState


def multi_query_node(state: RAGState):

    query = state.get("rewritten_query")

    if not query:
        query = state["query"]

    return {
        "rewritten_query": query,
        "retry_count": state.get("retry_count", 0)
    }
