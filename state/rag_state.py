from typing import TypedDict, Annotated
import operator
from langchain_core.documents import Document


class RAGState(TypedDict):
    query: str
    rewritten_query: str

    semantic_docs: list[Document]
    keyword_docs: list[Document]
    fused_docs: list[Document]
    compressed_docs: list[Document]

    context: str

    answer: str

    evaluation: dict

    retry_count: int

    # Same key + same reducer as FinancialState.agent_outputs.
    # Because the key name and reducer match the parent graph's schema,
    # LangGraph merges this subgraph's agent_outputs update into the
    # parent FinancialState automatically when the subgraph (rag_agent
    # node) returns to the main graph.
    agent_outputs: Annotated[dict, operator.or_]
