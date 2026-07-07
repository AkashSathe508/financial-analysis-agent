from langgraph.graph import StateGraph, START, END
from state.financial_state import FinancialState
from guardrails.prompt_guard import prompt_guard_node, blocked_node
from guardrails.router import guard_router
from supervisor.supervisor import supervisor_agent
from agents.entity_extractor.agent import entity_extractor_agent
from agents.ticker_resolver.agent import ticker_resolver_agent
from agents.market.agent import market_agent
from agents.news.agent import news_agent
from agents.risk.agent import risk_agent
from agents.investment.agent import investment_agent
from agents.report.agent import report_generator, synchronization_barrier
from graphs.rag_graph import rag_graph

# =========================================================
# GRAPH BUILDING (Main Graph)
# =========================================================
builder = StateGraph(FinancialState)

#nodes
builder.add_node("prompt_guard",prompt_guard_node)
builder.add_node("blocked",blocked_node)
builder.add_node("supervisor", supervisor_agent)
builder.add_node("market_agent", market_agent)
builder.add_node("entity_extractor",entity_extractor_agent)

builder.add_node("ticker_resolver",ticker_resolver_agent)

builder.add_node("rag_agent",rag_graph)
builder.add_node("news_agent",news_agent)

builder.add_node("barrier", synchronization_barrier)

builder.add_node("risk_agent", risk_agent)
builder.add_node("investment_agent", investment_agent)

builder.add_node("report_generator", report_generator)

#edges
builder.add_edge(START,"prompt_guard")
builder.add_conditional_edges("prompt_guard",guard_router,{
        "blocked": "blocked",
        "supervisor": "supervisor"
    }
)
builder.add_edge("blocked",END)
builder.add_edge("supervisor", "entity_extractor")
builder.add_edge("entity_extractor", "ticker_resolver")
builder.add_edge("ticker_resolver", "market_agent")
builder.add_edge("ticker_resolver", "news_agent")
builder.add_edge("ticker_resolver", "rag_agent")
builder.add_edge("market_agent", "barrier")
builder.add_edge("news_agent", "barrier")
builder.add_edge("rag_agent", "barrier")
builder.add_edge("barrier", "risk_agent")
builder.add_edge("risk_agent", "investment_agent")
builder.add_edge("investment_agent", "report_generator")
builder.add_edge("report_generator", END)


graph = builder.compile()
