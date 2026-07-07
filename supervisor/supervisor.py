from state.financial_state import FinancialState
from llms.gemini import reasoning_llm


def supervisor_agent(state: FinancialState):

    query = state["query"]

    prompt = f"""
You are the supervisor of a Financial Analysis Agent Crew.

Determine whether the following query is related to financial analysis.

Query:
{query}

Reply with ONLY:

YES

or

NO
"""

    answer = reasoning_llm.invoke(prompt)

    print(answer.content)

    return state
