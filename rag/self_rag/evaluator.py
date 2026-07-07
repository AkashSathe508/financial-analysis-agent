from rag.self_rag.models import SelfRAGDecision
from llms.groq import fast_llm
from state.rag_state import RAGState

self_rag_llm = fast_llm.with_structured_output(SelfRAGDecision)


def evaluate_answer(question, context, answer):

    prompt = f"""
You are evaluating a Retrieval-Augmented Generation (RAG) answer.

Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Determine whether the retrieved context is sufficient to support the answer.

Rules:

1. If the answer is fully supported by the context,
return SUFFICIENT.

2. If important information is missing,
return INSUFFICIENT.

3. Ignore writing quality.

4. Evaluate ONLY factual support.

Provide a short reason.
"""

    return self_rag_llm.invoke(prompt)


def self_rag_router(state: RAGState):

    decision = state["evaluation"]["decision"]

    retry_count = state.get("retry_count", 0)

    if decision == "SUFFICIENT":
        return "rag_output"

    if retry_count >= 2:
        return "rag_output"

    return "rewrite_query"
