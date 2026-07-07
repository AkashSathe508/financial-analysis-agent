from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from state.financial_state import FinancialState
from llms.groq import fast_llm
from tools.market_tools import get_stock_data, get_company_profile, calculate_financial_ratios

# =========================================================
# REACT AGENT
# =========================================================
market_react_agent = create_react_agent(
    model=fast_llm,
    tools=[
        get_stock_data,
        get_company_profile,
        calculate_financial_ratios
    ]
)


def market_agent(state: FinancialState):

    ticker = state["ticker"]

    result = market_react_agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"""
                            You are a professional financial analyst.

                            Analyze the company using the ticker:

                            {ticker}

                            Use your available tools whenever required.

                            After retrieving the data,

                            Provide:

                            1. Company Overview
                            2. Current Stock Price
                            3. Market Capitalization
                            4. Sector
                            5. Industry
                            6. P/E Ratio
                            7. EPS
                            8. Key Business Summary
                            Keep the response under 200 words.
                        """
                )
            ]
        }
    )

    final_answer = result["messages"][-1].content

    last_message = result["messages"][-1]

    if isinstance(last_message.content, list):
        final_answer = "\n".join(
            block["text"]
            for block in last_message.content
            if block.get("type") == "text"
        )
    else:
        final_answer = last_message.content

    market_output = {
    "analysis": final_answer,
    "ticker": ticker
    }

    return {
        "agent_outputs": {
            "market": market_output
        },
        "messages": result["messages"]
    }
