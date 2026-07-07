from langchain_core.tools import tool
from rag.retrievers.semantic import retriever


@tool
def retrieve_financial_report(query: str):
    """
    Retrieve relevant information from financial reports.
    """

    docs = retriever.invoke(query)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return context
