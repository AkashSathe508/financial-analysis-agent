from state.financial_state import FinancialState
from llms.gemini import reasoning_llm


def investment_agent(state: FinancialState):

    outputs = state["agent_outputs"]

    market = outputs.get("market", {}).get("analysis", "")
    rag = outputs.get("rag", {}).get("analysis", "")
    news = outputs.get("news", {}).get("analysis", "")
    risk = outputs.get("risk", {}).get("analysis", "")

    prompt = f"""
    You are a Senior Investment Advisor.

    Based on the following analyses, provide an investment recommendation.

    =====================
    MARKET ANALYSIS
    =====================
    {market}

    =====================
    FINANCIAL REPORT ANALYSIS
    =====================
    {rag}

    =====================
    NEWS ANALYSIS
    =====================
    {news}

    =====================
    RISK ANALYSIS
    =====================
    {risk}

    Provide your response in the following format:

    1. Recommendation
    (Strong Buy / Buy / Hold / Sell / Strong Sell)

    2. Confidence
    (High / Medium / Low)

    3. Suitable For
    (Short-term / Long-term / Value Investor / Growth Investor)

    4. Key Reasons

    5. Potential Concerns

    Keep the response under 250 words.
    """

    answer = reasoning_llm.invoke(prompt)

    return {
        "agent_outputs": {
            "investment": {
                "analysis": answer.content
            }
        }
    }
