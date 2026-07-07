from langchain_community.retrievers import BM25Retriever
from rag.vectorstores.faiss_store import chunks

bm25_retriever = BM25Retriever.from_documents(chunks)
