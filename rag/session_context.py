from contextvars import ContextVar, Token
from typing import Optional


_current_session_id: ContextVar[Optional[str]] = ContextVar(
    "current_rag_session_id",
    default=None,
)


def get_current_session_id() -> Optional[str]:
    return _current_session_id.get()


def set_current_session_id(session_id: str) -> Token[Optional[str]]:
    return _current_session_id.set(session_id)


def reset_current_session_id(token: Token[Optional[str]]) -> None:
    _current_session_id.reset(token)
