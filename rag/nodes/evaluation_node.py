from state.rag_state import RAGState
from rag.self_rag.evaluator import evaluate_answer


def evaluation_node(state: RAGState):

    evaluation = evaluate_answer(
    question=state["rewritten_query"],
    context="\n\n".join(
        doc.page_content[:400]
        for doc in state["compressed_docs"][:3]
    ),
    answer=state["answer"][:1500]
    )
    print(state.keys())
    return {
        "evaluation": evaluation.model_dump()
    }
