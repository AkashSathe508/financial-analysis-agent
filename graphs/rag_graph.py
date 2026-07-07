from langgraph.graph import StateGraph, START, END
from state.rag_state import RAGState
from rag.nodes.multi_query_node import multi_query_node
from rag.nodes.semantic_retrieval_node import semantic_retrieval_node
from rag.nodes.keyword_retrieval_node import keyword_retrieval_node
from rag.nodes.fusion_node import fusion_node
from rag.nodes.compression_node import compression_node
from rag.nodes.context_node import context_node
from rag.nodes.answer_generation_node import answer_generation_node
from rag.nodes.evaluation_node import evaluation_node
from rag.nodes.rewrite_query_node import rewrite_query_node
from rag.nodes.rag_output_node import rag_output_node
from rag.self_rag.evaluator import self_rag_router

# =========================================================
# GRAPH BUILDING (RAG Subgraph)
# =========================================================
builder = StateGraph(RAGState)

builder.add_node("multi_query", multi_query_node)
builder.add_node("semantic_retrieval", semantic_retrieval_node)
builder.add_node("keyword_retrieval", keyword_retrieval_node)
builder.add_node("fusion", fusion_node)
builder.add_node("compression", compression_node)
builder.add_node("context", context_node)
builder.add_node("answer_generation", answer_generation_node)
builder.add_node("evaluation", evaluation_node)
builder.add_node("rewrite_query", rewrite_query_node)
builder.add_node("rag_output",rag_output_node)

#edges

builder.add_edge(START, "multi_query")
builder.add_edge("multi_query", "semantic_retrieval")
builder.add_edge("multi_query", "keyword_retrieval")
builder.add_edge(["semantic_retrieval", "keyword_retrieval"],"fusion")
builder.add_edge("fusion", "compression")
builder.add_edge("compression", "context")
builder.add_edge("context", "answer_generation")
builder.add_edge("answer_generation", "evaluation")
builder.add_conditional_edges(
    "evaluation",
    self_rag_router,
    {
        "rewrite_query": "rewrite_query",

        "rag_output": "rag_output"
    }
)
builder.add_edge("rewrite_query","multi_query")
builder.add_edge("rag_output",END)

rag_graph = builder.compile()
