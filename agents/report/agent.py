import logging

from state.financial_state import FinancialState
from llms.gemini import reasoning_llm

logger = logging.getLogger(__name__)


def _section(title: str, content: str) -> str:
    content = (content or "").strip()
    return f"# {title}\n\n{content or 'Not available.'}"


def _fallback_report(market: str, news: str, rag: str, risk: str, investment: str) -> str:
    return "\n\n".join(
        [
            _section(
                "Executive Summary",
                "The final narrative model quota was exhausted, so this report preserves the completed agent findings in a structured format.",
            ),
            _section("Market Performance", market),
            _section("Financial Analysis", rag),
            _section("Recent News", news),
            _section("Risk Assessment", risk),
            _section("Investment Recommendation", investment),
            _section(
                "Final Conclusion",
                "Review the source sections above before making an investment decision.",
            ),
        ]
    )


def report_generator(state: FinancialState):

    outputs = state["agent_outputs"]

    market = outputs.get("market", {}).get("analysis", "")

    news = outputs.get("news", {}).get("analysis", "")

    rag = outputs.get("rag", {}).get("analysis", "")

    risk = outputs.get("risk", {}).get("analysis", "")

    investment = outputs.get("investment", {}).get("analysis", "")

    prompt = f"""
You are a Chief Financial Analyst.

Create a professional financial analysis report.

================================================
MARKET ANALYSIS
================================================

{market}

================================================
FINANCIAL REPORT ANALYSIS
================================================

{rag}

================================================
NEWS ANALYSIS
================================================

{news}

================================================
RISK ANALYSIS
================================================

{risk}

================================================
INVESTMENT RECOMMENDATION
================================================

{investment}

Create a professional report with the following sections:

# Executive Summary

# Company Overview

# Market Performance

# Financial Analysis

# Business Analysis

# Recent News

# Risk Assessment

# Investment Recommendation

# Final Conclusion

Use professional language.

Keep the report around 600-800 words.
"""

    try:
        answer = reasoning_llm.invoke(prompt)
        final_report = answer.content
    except Exception as exc:
        logger.warning("Report generator failed; returning fallback report: %s", exc)
        final_report = _fallback_report(market, news, rag, risk, investment)

    return {
        "agent_outputs": {
            "report": {
                "analysis": final_report
            }
        },
        "final_report": final_report
    }


def synchronization_barrier(state: FinancialState):

    logger.debug("All parallel agents completed (market, news, rag).")

    # market_agent, news_agent, and the rag_agent subgraph each already
    # merge their own result into agent_outputs directly (via the
    # operator.or_ reducer on that field), so there is nothing left to
    # assemble here. This node is kept only as the synchronization point
    # (its incoming edges from market_agent/news_agent/rag_agent guarantee
    # all three have finished before risk_agent runs).
    return {}
