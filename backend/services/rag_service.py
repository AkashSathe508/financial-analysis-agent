from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.services.vector_service import VectorService


class RAGService:
    def __init__(self, vector_service: VectorService | None = None):
        self.vector_service = vector_service or VectorService()

    def process_uploaded_document(
        self,
        *,
        session_id: str,
        pdf_path: Path,
        original_filename: str,
        document_hash: str,
        size_bytes: int,
    ) -> dict[str, Any]:
        return self.vector_service.process_pdf(
            session_id=session_id,
            pdf_path=pdf_path,
            original_filename=original_filename,
            document_hash=document_hash,
            size_bytes=size_bytes,
        )
