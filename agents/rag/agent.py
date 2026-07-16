"""
RAG ReAct agent (simple tool-calling variant).

NOTE: This agent is NOT used by the main graph, which instead runs the
full Advanced RAG subgraph (graphs/rag_graph.py) as the 'rag_agent' node.
This file exists as an alternative/reference implementation and is kept
here for completeness with the correct output key schema.
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from llms.groq import fast_llm
from state.financial_state import FinancialState
from tools.rag_tools import retrieve_financial_report

logger = logging.getLogger(__name__)

rag_react_agent = create_react_agent(
    model=fast_llm,
    tools=[retrieve_financial_report],
)


def rag_agent(state: FinancialState) -> dict:
    query = state["query"]

    try:
        result = rag_react_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=f"""
You are a financial report analyst.

Answer ONLY from the uploaded annual report.

If information is missing, explicitly say it is not present in the report.

Always provide:

• Direct answer
• Supporting evidence
• Relevant financial discussion

Question:

{query}

Use your retrieval tool whenever needed.

If the report doesn't contain the answer, clearly say so.
"""
                    )
                ]
            }
        )
    except Exception as exc:
        logger.warning("RAG ReAct agent failed: %s", exc)
        return {
            "agent_outputs": {
                "rag": {"analysis": "RAG analysis unavailable."}
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

    # Output key MUST be agent_outputs.rag so it merges correctly into
    # the parent FinancialState via the operator.or_ reducer.
    return {
        "agent_outputs": {
            "rag": {"analysis": final_answer}
        },
        "messages": result["messages"],
    }
