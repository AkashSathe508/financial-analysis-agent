from state.rag_state import RAGState
from rag.self_rag.rewrite_query import rewrite_query


def rewrite_query_node(state: RAGState):

    rewritten = rewrite_query(
        state["rewritten_query"],
        state["evaluation"]["reason"]
    )

    return {
        "rewritten_query": rewritten.rewritten_query,
        "retry_count":state.get("retry_count",0)+1
    }
