from langchain_community.vectorstores import FAISS
from rag.loaders.pdf_loader import load_financial_report
from rag.splitter.text_splitter import split_documents
from rag.embeddings.huggingface import embedding_model

docs = load_financial_report(
    "data/reports/Apple_2025_Annual_Report.pdf"
)

chunks = split_documents(docs)

vector_store = FAISS.from_documents(
    documents=chunks,
    embedding=embedding_model
)

base_retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}
)
