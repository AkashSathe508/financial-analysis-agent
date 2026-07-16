from state.rag_state import RAGState
from rag.self_rag.evaluator import (
    MAX_EVAL_ANSWER_CHARS,
    MAX_EVAL_DOC_CHARS,
    MAX_EVAL_DOCS,
    evaluate_answer,
)


def evaluation_node(state: RAGState):

    evaluation = evaluate_answer(
    question=state["rewritten_query"],
    context="\n\n".join(
        doc.page_content[:MAX_EVAL_DOC_CHARS]
        for doc in state["compressed_docs"][:MAX_EVAL_DOCS]
    ),
    answer=state["answer"][:MAX_EVAL_ANSWER_CHARS]
    )
    return {
        "evaluation": evaluation.model_dump()
    }
