from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

from rag.session_context import reset_current_session_id, set_current_session_id
from rag.vectorstores.session_registry import MissingSessionDocumentError

from backend.services.exceptions import GraphExecutionError, NoProcessedDocumentError
from backend.services.report_service import ReportService
from backend.services.vector_service import VectorService


NODE_TO_AGENT = {
    "prompt_guard": "guard",
    "blocked": "guard",
    "supervisor": "supervisor",
    "entity_extractor": "entity_extractor",
    "ticker_resolver": "ticker_resolver",
    "market_agent": "market",
    "news_agent": "news",
    "rag_agent": "rag",
    "risk_agent": "risk",
    "investment_agent": "investment",
    "report_generator": "report",
}

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(
        self,
        vector_service: VectorService | None = None,
        report_service: ReportService | None = None,
    ):
        self.vector_service = vector_service or VectorService()
        self.report_service = report_service or ReportService()

    def analyze(self, *, query: str, company: str, session_id: str) -> dict[str, Any]:
        self.vector_service.ensure_session_ready(session_id)
        token = set_current_session_id(session_id)
        try:
            result = self._graph().invoke(self._initial_state(query, company, session_id))
        except MissingSessionDocumentError as exc:
            raise NoProcessedDocumentError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Graph execution failed during analysis.")
            raise GraphExecutionError("Graph or LLM execution failed during analysis.") from exc
        finally:
            reset_current_session_id(token)

        response = self._format_response(result, query, session_id)
        self._save_report_if_available(session_id, response)
        return response

    def stream(self, *, query: str, company: str, session_id: str) -> Iterator[str]:
        try:
            self.vector_service.ensure_session_ready(session_id)
        except Exception as exc:
            yield self._sse({"type": "error", "message": getattr(exc, "message", str(exc))})
            return

        # Set the session context for the entire synchronous generator.  We do NOT
        # use the token-based reset here because this generator is iterated by
        # Starlette's iterate_in_threadpool which may switch OS threads between
        # yields.  ContextVar.reset(token) raises ValueError when called from a
        # different contextvars.Context than the one that called .set().  Since
        # the session_id is fixed for the lifetime of this request, a simple set
        # without a paired reset is safe and correct.
        set_current_session_id(session_id)

        latest_state = self._initial_state(query, company, session_id)
        try:
            yield self._sse({"type": "run_started", "query": query})
            for update in self._stream_graph_updates(latest_state, session_id):
                for node_name, payload in update.items():
                    agent = NODE_TO_AGENT.get(node_name)
                    if not agent:
                        continue

                    yield self._sse({"type": "agent_status", "agent": agent, "status": "running"})
                    if isinstance(payload, dict):
                        self._merge_update(latest_state, payload)
                        yield from self._output_events(agent, node_name, payload)
                    yield self._sse({"type": "agent_status", "agent": agent, "status": "done"})

            response = self._format_response(latest_state, query, session_id)
            self._save_report_if_available(session_id, response)
            yield self._sse({"type": "run_completed"})
        except MissingSessionDocumentError as exc:
            yield self._sse({"type": "error", "message": str(exc)})
        except Exception:
            logger.exception("Graph stream failed during analysis.")
            yield self._sse({"type": "error", "message": "Graph or LLM execution failed during analysis."})

    def _initial_state(self, query: str, company: str, session_id: str) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "query": query,
            "company": company or "",
            "ticker": "",
            "agent_outputs": {},
            "final_report": "",
            "blocked": False,
            "response": "",
            "messages": [],
        }

    def _graph(self):
        from graphs.main_graph import graph

        return graph

    def _stream_graph_updates(self, state: dict[str, Any], session_id: str) -> Iterator[dict[str, Any]]:
        # session_id ContextVar is already set by the caller (stream/analyze).
        # We do NOT call set/reset inside the loop to avoid cross-context errors
        # when Starlette's thread pool iterates this generator across threads.
        updates = self._graph().stream(state, stream_mode="updates")
        try:
            yield from updates
        finally:
            close = getattr(updates, "close", None)
            if close:
                close()

    def _format_response(self, result: dict[str, Any], query: str, session_id: str) -> dict[str, Any]:
        outputs = result.get("agent_outputs", {})
        final_report = result.get("final_report") or outputs.get("report", {}).get("analysis", "")
        return {
            "success": True,
            "session_id": session_id,
            "query": query,
            "company": result.get("company", ""),
            "ticker": result.get("ticker", ""),
            "blocked": bool(result.get("blocked", False)),
            "response": result.get("response", ""),
            "market": outputs.get("market"),
            "news": outputs.get("news"),
            "rag": outputs.get("rag"),
            "risk": outputs.get("risk"),
            "investment": outputs.get("investment"),
            "report": final_report,
        }

    def _save_report_if_available(self, session_id: str, response: dict[str, Any]) -> None:
        report = response.get("report")
        if not report:
            return
        self.report_service.save_report(
            session_id,
            str(report),
            {
                "query": response.get("query"),
                "company": response.get("company"),
                "ticker": response.get("ticker"),
            },
        )

    def _merge_update(self, state: dict[str, Any], update: dict[str, Any]) -> None:
        for key, value in update.items():
            if key == "agent_outputs" and isinstance(value, dict):
                state.setdefault("agent_outputs", {}).update(value)
            elif key == "messages" and isinstance(value, list):
                state.setdefault("messages", []).extend(value)
            else:
                state[key] = value

    def _output_events(self, agent: str, node_name: str, payload: dict[str, Any]) -> Iterator[str]:
        if payload.get("blocked"):
            yield self._sse({"type": "blocked", "response": payload.get("response", "")})

        if node_name == "blocked":
            yield self._sse({"type": "blocked", "response": payload.get("response", "")})

        if "company" in payload:
            yield self._sse({"type": "agent_output", "agent": agent, "output": {"company": payload["company"]}})

        if "ticker" in payload:
            yield self._sse({"type": "agent_output", "agent": agent, "output": {"ticker": payload["ticker"]}})

        emitted_report_tokens = False
        for output_agent, output in payload.get("agent_outputs", {}).items():
            yield self._sse({"type": "agent_output", "agent": output_agent, "output": output})
            if output_agent == "report":
                report = output.get("analysis", "") if isinstance(output, dict) else str(output)
                yield from self._report_tokens(report)
                emitted_report_tokens = True

        if node_name == "report_generator" and payload.get("final_report") and not emitted_report_tokens:
            yield from self._report_tokens(str(payload["final_report"]))

    def _report_tokens(self, report: str) -> Iterator[str]:
        for index in range(0, len(report), 32):
            yield self._sse({"type": "report_token", "token": report[index:index + 32]})

    @staticmethod
    def _sse(payload: dict[str, Any]) -> str:
        return f"data: {json.dumps(payload, default=str)}\n\n"
