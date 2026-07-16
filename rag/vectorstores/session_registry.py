from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Optional

from langchain_core.documents import Document

from rag.session_context import get_current_session_id


class RAGSessionError(RuntimeError):
    """Base error for session-aware RAG index access."""


class MissingSessionDocumentError(RAGSessionError):
    """Raised when a graph run has no processed document for its session."""


class VectorIndexLoadError(RAGSessionError):
    """Raised when a persisted vector index cannot be loaded."""


@dataclass(frozen=True)
class RAGSessionIndex:
    session_id: str
    document_id: str
    vector_path: Path
    chunks: list[Document]
    vector_store: Any
    base_retriever: Any
    semantic_retriever: Any
    bm25_retriever: Any


class LazySemanticRetriever:
    def __init__(self, base_retriever: Any):
        self.base_retriever = base_retriever
        self._retriever = None
        self._lock = RLock()

    def _get_retriever(self):
        if self._retriever is None:
            with self._lock:
                if self._retriever is None:
                    from langchain_classic.retrievers.multi_query import MultiQueryRetriever
                    from llms.groq import fast_llm

                    self._retriever = MultiQueryRetriever.from_llm(
                        retriever=self.base_retriever,
                        llm=fast_llm,
                        include_original=True,
                    )
        return self._retriever

    def invoke(self, input: Any, config: Optional[dict] = None, **kwargs):
        return self._get_retriever().invoke(input, config=config, **kwargs)

    def __getattr__(self, name: str):
        return getattr(self._get_retriever(), name)


_indexes: dict[str, RAGSessionIndex] = {}
_lock = RLock()


def persist_index(chunks: list[Document], vector_path: Path) -> None:
    if not chunks:
        raise VectorIndexLoadError("Cannot persist an empty document index.")

    from rag.embeddings.huggingface import embedding_model
    from langchain_community.vectorstores import FAISS

    vector_path.mkdir(parents=True, exist_ok=True)
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model,
    )
    vector_store.save_local(str(vector_path))

    with (vector_path / "chunks.pkl").open("wb") as handle:
        pickle.dump(chunks, handle)


def load_index(session_id: str, document_id: str, vector_path: Path) -> RAGSessionIndex:
    try:
        from rag.embeddings.huggingface import embedding_model
        from langchain_community.vectorstores import FAISS
        from langchain_community.retrievers import BM25Retriever
        with (vector_path / "chunks.pkl").open("rb") as handle:
            chunks = pickle.load(handle)

        vector_store = FAISS.load_local(
            str(vector_path),
            embedding_model,
            allow_dangerous_deserialization=True,
        )
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        semantic_retriever = LazySemanticRetriever(base_retriever)
        bm25_retriever = BM25Retriever.from_documents(chunks)
    except Exception as exc:  # pragma: no cover - exercised by runtime services
        raise VectorIndexLoadError(
            f"Failed to load vector index for session '{session_id}'."
        ) from exc

    return RAGSessionIndex(
        session_id=session_id,
        document_id=document_id,
        vector_path=vector_path,
        chunks=chunks,
        vector_store=vector_store,
        base_retriever=base_retriever,
        semantic_retriever=semantic_retriever,
        bm25_retriever=bm25_retriever,
    )


def register_session_index(index: RAGSessionIndex) -> None:
    with _lock:
        _indexes[index.session_id] = index


def has_session_index(session_id: str) -> bool:
    with _lock:
        return session_id in _indexes


def get_session_index(session_id: Optional[str] = None) -> RAGSessionIndex:
    resolved_session_id = session_id or get_current_session_id()
    if not resolved_session_id:
        raise MissingSessionDocumentError(
            "No RAG session is active. Upload a PDF and pass the returned session_id."
        )

    with _lock:
        index = _indexes.get(resolved_session_id)

    if index is None:
        raise MissingSessionDocumentError(
            f"No processed document is available for session '{resolved_session_id}'."
        )
    return index


class SessionRetrieverProxy:
    def __init__(self, retriever_name: str):
        self.retriever_name = retriever_name

    def _retriever(self, session_id: Optional[str] = None):
        return getattr(get_session_index(session_id), self.retriever_name)

    def invoke(self, input: Any, config: Optional[dict] = None, *, session_id: Optional[str] = None, **kwargs):
        retriever = self._retriever(session_id)
        # Do NOT forward session_id to the underlying retriever — it is not a
        # standard LangChain retriever argument and will raise a TypeError.
        return retriever.invoke(input, config=config, **kwargs)

    def __getattr__(self, name: str):
        return getattr(self._retriever(), name)


class SessionVectorStoreProxy:
    def __getattr__(self, name: str):
        return getattr(get_session_index().vector_store, name)


class SessionChunksProxy:
    def _chunks(self):
        return get_session_index().chunks

    def __iter__(self):
        return iter(self._chunks())

    def __len__(self):
        return len(self._chunks())

    def __getitem__(self, index):
        return self._chunks()[index]
