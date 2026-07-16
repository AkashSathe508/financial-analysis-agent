from rag.vectorstores.session_registry import (
    SessionChunksProxy,
    SessionRetrieverProxy,
    SessionVectorStoreProxy,
)


vector_store = SessionVectorStoreProxy()
chunks = SessionChunksProxy()
base_retriever = SessionRetrieverProxy("base_retriever")
