import logging

from state.financial_state import FinancialState
from llms.gemini import reasoning_llm

logger = logging.getLogger(__name__)


def _clip(text: str, limit: int = 700) -> str:
    text = (text or "").strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _fallback_investment(market: str, rag: str, news: str, risk: str) -> str:
    return f"""
1. Recommendation
Hold / Review Required

2. Confidence
Low

3. Suitable For
Long-term investors who can review the source analysis manually.

4. Key Reasons
{_clip(market) or "Market analysis was unavailable."}

5. Potential Concerns
{_clip(risk or rag or news) or "Risk, filing, and news details were limited."}
""".strip()


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

    try:
        answer = reasoning_llm.invoke(prompt)
        analysis = answer.content
    except Exception as exc:
        logger.warning("Investment agent failed; returning fallback recommendation: %s", exc)
        analysis = _fallback_investment(market, rag, news, risk)

    return {
        "agent_outputs": {
            "investment": {
                "analysis": analysis
            }
        }
    }
