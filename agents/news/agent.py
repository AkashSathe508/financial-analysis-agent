import logging

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from state.financial_state import FinancialState
from llms.gemini import reasoning_llm
from tools.search_tools import news_tool

logger = logging.getLogger(__name__)

#News ReAct Agent
news_react_agent = create_react_agent(
    model=reasoning_llm,
    tools=[
        news_tool
    ]
)


def news_agent(state: FinancialState):

    query = state["query"]

    try:
        result = news_react_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"""
                        You are a financial news analyst.

                        Find the latest news related to:

                        {query}

                        Use your search tool whenever required.

                        Provide:

                        1. Headlines
                        2. Summary
                        3. Possible market impact
                        4. Overall sentiment

                        Keep the answer concise.
                        """
                    )
                ]
            }
        )
    except Exception as exc:
        logger.warning("News agent failed; returning fallback analysis: %s", exc)
        return {
            "agent_outputs": {
                "news": {
                    "analysis": "News analysis unavailable because the news model or search quota was exhausted."
                }
            }
        }

    last_message = result["messages"][-1]

    if isinstance(last_message.content, list):
        final_answer = "\n".join(
            block["text"]
            for block in last_message.content
            if block.get("type") == "text"
        )
    else:
        final_answer = last_message.content

    return {
        "agent_outputs": {
            "news": {
                "analysis": final_answer
            }
        },
        "messages": result["messages"]
    }
