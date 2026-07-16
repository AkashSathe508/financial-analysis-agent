from typing import Any, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1)
    company: str = ""
    session_id: Optional[str] = None


class AnalyzeResponse(BaseModel):
    success: bool = True
    session_id: str
    query: str
    company: str = ""
    ticker: str = ""
    blocked: bool = False
    response: str = ""
    market: Any = None
    news: Any = None
    rag: Any = None
    risk: Any = None
    investment: Any = None
    report: Any = None
