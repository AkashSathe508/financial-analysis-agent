from state.rag_state import RAGState
from rag.compression.contextual_compression import compress_documents


def compression_node(state: RAGState):

    docs = compress_documents(
        state["rewritten_query"],
        state["fused_docs"]
    )

    return {
        "compressed_docs": docs
    }
