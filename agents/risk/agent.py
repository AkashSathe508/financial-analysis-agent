import logging

from state.financial_state import FinancialState
from llms.gemini import reasoning_llm

logger = logging.getLogger(__name__)


def _clip(text: str, limit: int = 700) -> str:
    text = (text or "").strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _fallback_risk(market: str, rag: str, news: str) -> str:
    return f"""
1. Overall Risk Level
Review Required

2. Financial Risk
{_clip(rag) or "Financial filing analysis was unavailable."}

3. Business Risk
Use the market and filing sections below to review product, demand, and execution risk.

4. Market Sentiment
{_clip(news, 500) or "Recent news analysis was unavailable."}

5. Key Risk Factors
{_clip(market, 500) or "Market data was unavailable."}

6. Strengths
See the completed market and filing analysis.

7. Weaknesses
Model quota was exhausted before a full narrative risk synthesis could be generated.
""".strip()


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

    try:
        answer = reasoning_llm.invoke(prompt)
        analysis = answer.content
    except Exception as exc:
        logger.warning("Risk agent failed; returning fallback analysis: %s", exc)
        analysis = _fallback_risk(market, rag, news)

    return {
        "agent_outputs": {
            "risk": {
                "analysis": analysis
            }
        }
    }
