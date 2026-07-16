from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import settings
from backend.services.exceptions import ReportNotFoundError


class ReportService:
    def __init__(self, report_dir: Path = settings.report_dir):
        self.report_dir = report_dir

    def save_report(self, session_id: str, report: str, metadata: dict[str, Any]) -> dict[str, Any]:
        path = self._report_path(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": session_id,
            "report": report,
            "metadata": {
                **metadata,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def get_report(self, session_id: str) -> dict[str, Any]:
        path = self._report_path(session_id)
        if not path.exists():
            raise ReportNotFoundError(f"No generated report was found for session '{session_id}'.")
        return json.loads(path.read_text(encoding="utf-8"))

    def _report_path(self, session_id: str) -> Path:
        return self.report_dir / session_id / "report.json"
