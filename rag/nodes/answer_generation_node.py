from state.rag_state import RAGState
from llms.groq import fast_llm, invoke_with_rate_limit_retry


def answer_generation_node(state: RAGState):

    prompt = f"""
You are a Senior Financial Research Analyst.

Answer ONLY using the context.

Context:
{state["context"]}

Question:
{state["rewritten_query"]}
"""

    answer = invoke_with_rate_limit_retry(fast_llm, prompt)

    return {
        "answer": answer.content
    }
