from typing import TypedDict, Annotated, NotRequired
import operator


class FinancialState(TypedDict):
    # Backend session used to select the uploaded financial report index.
    session_id: NotRequired[str]

    # User Input
    query: str

    # Company Info
    company: str
    ticker: str

    # Combined outputs from every agent.
    # Annotated with operator.or_ so that when market_agent, news_agent,
    # and the rag_agent subgraph all run in parallel and each return a
    # partial {"agent_outputs": {...}} update, LangGraph merges (unions)
    # them instead of one overwriting another or raising a conflicting-
    # update error.
    agent_outputs: Annotated[dict, operator.or_]

    # Guardrail fields
    blocked: bool
    response: str

    # Final report
    final_report: str

    # Conversation history
    messages: Annotated[list, operator.add]
