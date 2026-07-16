from __future__ import annotations

from fastapi import APIRouter

from backend.schemas.report import ReportResponse
from backend.services.report_service import ReportService
from backend.utils.sessions import normalize_session_id


router = APIRouter(tags=["report"])
report_service = ReportService()


@router.get("/report/{session_id}", response_model=ReportResponse)
@router.get("/api/report/{session_id}", response_model=ReportResponse)
async def get_report(session_id: str):
    resolved_session_id = normalize_session_id(session_id)
    payload = report_service.get_report(resolved_session_id or session_id)
    return ReportResponse(
        session_id=payload["session_id"],
        report=payload["report"],
        metadata=payload.get("metadata", {}),
    )
