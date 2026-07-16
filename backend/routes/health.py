from fastapi import APIRouter

from backend.config import settings
from backend.schemas.common import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
@router.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=settings.api_version)
