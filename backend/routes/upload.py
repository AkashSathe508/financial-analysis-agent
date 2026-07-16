from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, Request, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from backend.config import settings
from backend.schemas.upload import UploadResponse
from backend.services.rag_service import RAGService
from backend.utils.files import sanitize_filename, save_upload_file, validate_pdf_upload
from backend.utils.sessions import attach_session, create_session_id, resolve_session_id


router = APIRouter(tags=["upload"])
rag_service = RAGService()


@router.post("/upload", response_model=UploadResponse)
@router.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
):
    validate_pdf_upload(file)
    resolved_session_id = resolve_session_id(request, session_id) or create_session_id()
    attach_session(response, resolved_session_id)

    filename = sanitize_filename(file.filename)
    upload_dir = settings.upload_dir / resolved_session_id
    temp_path = upload_dir / f".upload-{uuid.uuid4().hex}-{filename}"
    document_hash, size_bytes = await save_upload_file(
        file,
        temp_path,
        settings.max_upload_mb * 1024 * 1024,
    )

    document_id = document_hash[:16]
    final_path = _final_upload_path(upload_dir, document_id, filename)
    if final_path.exists():
        temp_path.unlink(missing_ok=True)
    else:
        temp_path.rename(final_path)

    manifest = await run_in_threadpool(
        rag_service.process_uploaded_document,
        session_id=resolved_session_id,
        pdf_path=final_path,
        original_filename=file.filename,
        document_hash=document_hash,
        size_bytes=size_bytes,
    )

    return UploadResponse(
        session_id=resolved_session_id,
        document_id=manifest["document_id"],
        cached=bool(manifest["cached"]),
    )


def _final_upload_path(upload_dir: Path, document_id: str, filename: str) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir / f"{document_id}_{filename}"
