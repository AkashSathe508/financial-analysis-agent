from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from state.financial_state import FinancialState
from llms.groq import fast_llm
from tools.rag_tools import retrieve_financial_report

rag_react_agent = create_react_agent(
    model=fast_llm,
    tools=[
        retrieve_financial_report
    ]
)


def rag_agent(state: FinancialState):

    query = state["query"]

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
        "rag_result": {
            "analysis": final_answer
        },
        "messages": result["messages"]
    }
