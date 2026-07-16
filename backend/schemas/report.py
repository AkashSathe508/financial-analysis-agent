from typing import Any

from pydantic import BaseModel


class ReportResponse(BaseModel):
    success: bool = True
    session_id: str
    report: str
    metadata: dict[str, Any] = {}
