from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


class Settings:
    app_name = "Financial Analysis Backend"
    api_version = "1.0.0"

    storage_dir = PROJECT_ROOT / "backend" / "storage"
    upload_dir = storage_dir / "uploads"
    vector_dir = storage_dir / "vectors"
    report_dir = storage_dir / "reports"
    vector_cache_dir = vector_dir / "_cache"

    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "100"))
    session_cookie_name = os.getenv(
        "SESSION_COOKIE_NAME",
        "financial_analysis_session",
    )
    cors_origins = _csv_env(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    )

    def ensure_storage_dirs(self) -> None:
        for path in (
            self.upload_dir,
            self.vector_dir,
            self.report_dir,
            self.vector_cache_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
