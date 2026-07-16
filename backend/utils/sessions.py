from __future__ import annotations

import re
import uuid
from typing import Optional

from fastapi import Request, Response

from backend.config import settings
from backend.services.exceptions import InvalidSessionError


_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def create_session_id() -> str:
    return uuid.uuid4().hex


def normalize_session_id(session_id: Optional[str]) -> Optional[str]:
    if session_id is None:
        return None
    value = session_id.strip()
    if not value:
        return None
    if not _SESSION_ID_RE.match(value):
        raise InvalidSessionError("Session IDs may contain only letters, numbers, '-' and '_'.")
    return value


def resolve_session_id(request: Request, explicit_session_id: Optional[str] = None) -> Optional[str]:
    return normalize_session_id(
        explicit_session_id
        or request.headers.get("X-Session-ID")
        or request.cookies.get(settings.session_cookie_name)
    )


def attach_session(response: Response, session_id: str) -> None:
    response.headers["X-Session-ID"] = session_id
    response.set_cookie(
        settings.session_cookie_name,
        session_id,
        max_age=60 * 60 * 24 * 30,
        httponly=False,
        samesite="lax",
    )
