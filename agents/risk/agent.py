from state.financial_state import FinancialState
from llms.gemini import reasoning_llm


def risk_agent(state: FinancialState):

    market = state["agent_outputs"].get("market", {}).get("analysis", "")

    rag = state["agent_outputs"].get("rag", {}).get("analysis", "")

    news = state["agent_outputs"].get("news", {}).get("analysis", "")

    prompt = f"""
        You are a Senior Financial Risk Analyst.

        Evaluate the investment risk using the following information.

        ==========================
        MARKET ANALYSIS
        ==========================

        {market}

        ==========================
        FINANCIAL REPORT ANALYSIS
        ==========================

        {rag}

        ==========================
        LATEST NEWS
        ==========================

        {news}

        Generate a structured report containing:

        1. Overall Risk Level
        2. Financial Risk
        3. Business Risk
        4. Market Sentiment
        5. Key Risk Factors
        6. Strengths
        7. Weaknesses

        Keep the report concise.
        """

    answer = reasoning_llm.invoke(prompt)

    return {
        "agent_outputs": {
            "risk": {
                "analysis": answer.content
            }
        }
    }
