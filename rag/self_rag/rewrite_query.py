from rag.self_rag.models import QueryRewrite
from llms.groq import fast_llm, invoke_with_rate_limit_retry

rewrite_llm = fast_llm.with_structured_output(QueryRewrite)


def rewrite_query(question, evaluation_reason):

    prompt = f"""
You are improving a search query for a financial RAG system.

Original Question:
{question}

The evaluator said:

{evaluation_reason}

Rewrite the query so it retrieves more relevant
information from a company's annual report.

Use financial terminology.

Return only the rewritten query.
"""

    return invoke_with_rate_limit_retry(rewrite_llm, prompt)
