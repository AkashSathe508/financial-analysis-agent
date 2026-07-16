from state.rag_state import RAGState

MAX_CONTEXT_DOCS = 4
MAX_DOC_CHARS = 1200
MAX_CONTEXT_CHARS = 4500


def context_node(state: RAGState):

    context = "\n\n".join(
        doc.page_content[:MAX_DOC_CHARS]
        for doc in state["compressed_docs"][:MAX_CONTEXT_DOCS]
    )[:MAX_CONTEXT_CHARS]

    return {
        "context": context
    }
