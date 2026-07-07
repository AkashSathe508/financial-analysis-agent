from state.financial_state import FinancialState
from llms.gemini import reasoning_llm


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

    answer = reasoning_llm.invoke(prompt)

    return {
        "agent_outputs": {
            "report": {
                "analysis": answer.content
            }
        },
        "final_report": answer.content
    }


def synchronization_barrier(state: FinancialState):

    print("=" * 60)
    print("All parallel agents completed.")
    print("=" * 60)

    # market_agent, news_agent, and the rag_agent subgraph each already
    # merge their own result into agent_outputs directly (via the
    # operator.or_ reducer on that field), so there is nothing left to
    # assemble here. This node is kept only as the synchronization point
    # (its incoming edges from market_agent/news_agent/rag_agent guarantee
    # all three have finished before risk_agent runs).
    return {}
