from state.financial_state import FinancialState
from guardrails.models import CompanyExtraction
from llms.gemini import reasoning_llm

# =========================================================
# STRUCTURE MODEL
# =========================================================
extractor_llm = reasoning_llm.with_structured_output(
    CompanyExtraction
)


def entity_extractor_agent(state: FinancialState):

    query = state["query"]
    prompt = f"""
        You are a financial entity extraction agent.

        Extract ONLY the company name mentioned.

        Examples

        Input:
        Should I invest in Apple?

        Output:
        Apple

        Input:
        Analyze Microsoft stock.

        Output:
        Microsoft

        Input:
        Tell me about Tesla.

        Output:
        Tesla

        User Query:

        {query}
    """

    result = extractor_llm.invoke(prompt)
    print(f"\nCompany: {result.company}")
    return {
        "company": result.company
    }
