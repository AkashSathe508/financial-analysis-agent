from state.rag_state import RAGState
from rag.fusion.reciprocal_rank_fusion import reciprocal_rank_fusion


def fusion_node(state: RAGState):

    fused = reciprocal_rank_fusion(
        [
            state["semantic_docs"],
            state["keyword_docs"]
        ]
    )

    return {
        "fused_docs": fused
    }
