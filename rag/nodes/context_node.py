from state.rag_state import RAGState


def context_node(state: RAGState):

    context = "\n\n".join(
        doc.page_content
        for doc in state["compressed_docs"]
    )

    return {
        "context": context
    }
