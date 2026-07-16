from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from backend.services.exceptions import InvalidPDFError, MissingPDFError


_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    cleaned = _SAFE_FILENAME_RE.sub("_", Path(filename).name).strip("._")
    return cleaned or "uploaded_report.pdf"


def validate_pdf_upload(file: UploadFile) -> None:
    if file is None or not file.filename:
        raise MissingPDFError("A PDF file is required.")

    if not file.filename.lower().endswith(".pdf"):
        raise InvalidPDFError("Only PDF uploads are supported.")


def validate_pdf_header(path: Path) -> None:
    with path.open("rb") as handle:
        header = handle.read(5)
    if header != b"%PDF-":
        raise InvalidPDFError("The uploaded file is not a valid PDF.")


async def save_upload_file(file: UploadFile, destination: Path, max_bytes: int) -> tuple[str, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    total_bytes = 0

    with destination.open("wb") as handle:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                raise InvalidPDFError(
                    f"PDF exceeds the {max_bytes // (1024 * 1024)} MB upload limit."
                )
            hasher.update(chunk)
            _write_chunk(handle, chunk)

    if total_bytes == 0:
        raise MissingPDFError("The uploaded PDF is empty.")

    validate_pdf_header(destination)
    return hasher.hexdigest(), total_bytes


def _write_chunk(handle: BinaryIO, chunk: bytes) -> None:
    handle.write(chunk)
