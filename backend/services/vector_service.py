from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any

from backend.config import settings
from backend.services.exceptions import (
    CorruptedPDFError,
    InvalidPDFError,
    NoProcessedDocumentError,
    VectorCreationError,
)
from rag.loaders.pdf_loader import load_financial_report
from rag.splitter.text_splitter import split_documents
from rag.vectorstores.session_registry import (
    VectorIndexLoadError,
    has_session_index,
    load_index,
    persist_index,
    register_session_index,
)


class VectorService:
    _cache_lock = RLock()

    def __init__(
        self,
        upload_dir: Path = settings.upload_dir,
        vector_dir: Path = settings.vector_dir,
        cache_dir: Path = settings.vector_cache_dir,
    ):
        self.upload_dir = upload_dir
        self.vector_dir = vector_dir
        self.cache_dir = cache_dir

    def process_pdf(
        self,
        *,
        session_id: str,
        pdf_path: Path,
        original_filename: str,
        document_hash: str,
        size_bytes: int,
    ) -> dict[str, Any]:
        document_id = document_hash[:16]
        session_vector_root = self.vector_dir / session_id
        session_vector_path = session_vector_root / document_id
        cache_vector_path = self.cache_dir / document_hash

        with self._cache_lock:
            cached = self._is_valid_vector_path(cache_vector_path)
            if not cached:
                self._build_cached_index(pdf_path, cache_vector_path, document_hash)

            if not self._is_valid_vector_path(session_vector_path):
                self._copy_index(cache_vector_path, session_vector_path)

        self._register_session_index(session_id, document_id, session_vector_path)
        manifest = self._write_manifest(
            session_id=session_id,
            document_id=document_id,
            document_hash=document_hash,
            original_filename=original_filename,
            upload_path=pdf_path,
            vector_path=session_vector_path,
            cached=cached,
            size_bytes=size_bytes,
        )
        return manifest

    def ensure_session_ready(self, session_id: str) -> dict[str, Any]:
        manifest = self.get_manifest(session_id)
        if not manifest:
            raise NoProcessedDocumentError(
                "No processed PDF is available for this session. Upload a PDF before running analysis."
            )

        if not has_session_index(session_id):
            self._register_session_index(
                session_id,
                manifest["document_id"],
                Path(manifest["vector_path"]),
            )
        return manifest

    def get_manifest(self, session_id: str) -> dict[str, Any] | None:
        path = self.vector_dir / session_id / "manifest.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_cached_index(self, pdf_path: Path, cache_vector_path: Path, document_hash: str) -> None:
        build_path = self.cache_dir / f".building-{document_hash}-{uuid.uuid4().hex}"
        try:
            documents = load_financial_report(str(pdf_path))
            if not documents:
                raise InvalidPDFError("The uploaded PDF did not contain loadable pages.")

            chunks = split_documents(documents)
            if not chunks:
                raise InvalidPDFError("The uploaded PDF did not contain extractable text.")

            persist_index(chunks, build_path)
            if cache_vector_path.exists():
                shutil.rmtree(cache_vector_path)
            build_path.rename(cache_vector_path)
        except InvalidPDFError:
            raise
        except VectorIndexLoadError as exc:
            raise VectorCreationError("Vector index creation failed.") from exc
        except Exception as exc:
            raise CorruptedPDFError(
                "The PDF could not be processed. It may be corrupted or encrypted."
            ) from exc
        finally:
            if build_path.exists():
                shutil.rmtree(build_path, ignore_errors=True)

    def _register_session_index(self, session_id: str, document_id: str, vector_path: Path) -> None:
        try:
            register_session_index(load_index(session_id, document_id, vector_path))
        except VectorIndexLoadError as exc:
            raise VectorCreationError("Failed to load the processed vector index.") from exc

    def _write_manifest(
        self,
        *,
        session_id: str,
        document_id: str,
        document_hash: str,
        original_filename: str,
        upload_path: Path,
        vector_path: Path,
        cached: bool,
        size_bytes: int,
    ) -> dict[str, Any]:
        session_vector_root = self.vector_dir / session_id
        session_vector_root.mkdir(parents=True, exist_ok=True)
        manifest = {
            "session_id": session_id,
            "document_id": document_id,
            "document_hash": document_hash,
            "original_filename": original_filename,
            "upload_path": str(upload_path),
            "vector_path": str(vector_path),
            "cached": cached,
            "size_bytes": size_bytes,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }
        (session_vector_root / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return manifest

    def _copy_index(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)

    @staticmethod
    def _is_valid_vector_path(path: Path) -> bool:
        return (
            path.exists()
            and (path / "index.faiss").exists()
            and (path / "index.pkl").exists()
            and (path / "chunks.pkl").exists()
        )
