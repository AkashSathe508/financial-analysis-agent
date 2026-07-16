from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from backend.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from backend.services.exceptions import NoProcessedDocumentError
from backend.services.graph_service import GraphService
from backend.utils.sessions import resolve_session_id


router = APIRouter(tags=["analysis"])
graph_service = GraphService()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest, request: Request):
    session_id = resolve_session_id(request, payload.session_id)
    if not session_id:
        raise NoProcessedDocumentError("Upload a PDF before running analysis.")

    return await run_in_threadpool(
        graph_service.analyze,
        query=payload.query,
        company=payload.company,
        session_id=session_id,
    )


@router.post("/api/analyze")
async def analyze_stream(payload: AnalyzeRequest, request: Request):
    session_id = resolve_session_id(request, payload.session_id)
    if not session_id:
        return StreamingResponse(
            iter(['data: {"type": "error", "message": "Upload a PDF before running analysis."}\n\n']),
            media_type="text/event-stream",
        )

    return StreamingResponse(
        graph_service.stream(
            query=payload.query,
            company=payload.company,
            session_id=session_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
