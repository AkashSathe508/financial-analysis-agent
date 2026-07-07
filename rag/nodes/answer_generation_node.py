from state.rag_state import RAGState
from llms.groq import fast_llm


def answer_generation_node(state: RAGState):

    prompt = f"""
You are a Senior Financial Research Analyst.

Answer ONLY using the context.

Context:
{state["context"]}

Question:
{state["rewritten_query"]}
"""

    answer = fast_llm.invoke(prompt)

    return {
        "answer": answer.content
    }
