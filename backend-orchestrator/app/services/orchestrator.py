"""
Orchestrator Service — coordinates all agents for a complete incident analysis.
Hexagonal pattern: this is the use-case layer.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

import httpx

from app.agents.vision_agent import VisionAgent
from app.agents.incident_analyst import IncidentAnalystAgent
from app.agents.runbook_agent import RunbookAgent
from app.agents.action_agent import ActionAgent
from app.config import get_settings
from app.domain.models import SessionState, IncidentSeverity
from app.domain.schemas import IssueRequest, AgentResponse
from app.infrastructure.gemini.client import GeminiClient
from app.infrastructure.gemini.embeddings import EmbeddingService
from app.infrastructure.postgres.models import VectorDBClient
from app.services.session_service import SessionService

logger = logging.getLogger("supportsight.orchestrator")
settings = get_settings()


class OrchestratorService:
    def __init__(self, session_service: SessionService):
        gemini = GeminiClient()
        embedding_service = EmbeddingService(settings.GEMINI_API_KEY)
        vector_db = VectorDBClient(settings.DATABASE_URL)
        
        self._session_service = session_service
        self._vision_agent = VisionAgent(gemini)
        self._analyst_agent = IncidentAnalystAgent(gemini)
        self._runbook_agent = RunbookAgent(gemini, embedding_service, vector_db)
        self._action_agent = ActionAgent(gemini)

    async def process_issue(
        self, request: IssueRequest, correlation_id: str
    ) -> AgentResponse:
        # 1. Resolve or create session
        session_id = request.session_id or str(uuid.uuid4())
        state = await self._session_service.get_or_create(session_id, correlation_id)
        state.add_timeline_event("issue_received", {"description": request.description[:200]})

        # 2. Parallel Processing (Simulation for competition)
        # We process logs via Rust and visuals via Gemini Vision
        
        # 2.1 Visual analysis (optional)
        visual_context = ""
        what_i_see = None
        if request.image_base64:
            visual_context = await self._vision_agent.analyze(
                request.image_base64, request.description
            )
            what_i_see = visual_context
            state.add_timeline_event("vision_analyzed", {"summary": visual_context[:100]})

        # 2.2 Log analysis via high-speed Rust service
        log_summary = ""
        if request.logs:
            log_summary = await self._call_logs_service(request.logs, session_id)
            state.add_timeline_event("logs_analyzed", {"lines": request.logs.count("\n"), "summary": log_summary[:100]})

        # 3. Deep Incident Analysis (Reasoning Layer)
        hypotheses, category, root_cause = await self._analyst_agent.analyze(
            request.description, visual_context, log_summary
        )
        state.active_hypotheses = hypotheses
        state.incident_category = category

        # 4. Severity Assessment
        state.severity = self._assess_severity(hypotheses)

        # 5. Remediation Protocol (Runbook Query)
        runbook_context = await self._runbook_agent.query(
            request.description, category.value
        )

        # 6. Action Generation
        actions = await self._action_agent.prepare(
            request.description, hypotheses, runbook_context
        )
        state.pending_actions = actions
        state.add_timeline_event("actions_prepared", {"count": len(actions)})

        # 7. Persist session
        await self._session_service.save(state)

        top_hyp = hypotheses[0] if hypotheses else None
        return AgentResponse(
            session_id=session_id,
            correlation_id=correlation_id,
            what_i_understood=request.description,
            what_i_see=what_i_see,
            root_cause_summary=root_cause,
            recommendations=[h.description for h in hypotheses[:3]],
            next_action=actions[0].description if actions else "Awaiting further diagnostic data...",
            hypotheses=[
                {"description": h.description, "confidence": h.confidence, "evidence": h.evidence}
                for h in hypotheses
            ],
            confidence=top_hyp.confidence if top_hyp else 0.0,
            needs_more_info=not request.logs and not request.image_base64,
            suggested_actions=[
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "command": a.command,
                    "requires_confirmation": a.requires_confirmation,
                    "is_destructive": a.is_destructive,
                }
                for a in actions
            ],
        )

    async def _call_logs_service(self, raw_logs: str, session_id: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{settings.LOGS_SERVICE_URL}/analyze",
                    json={"raw_logs": raw_logs, "session_id": session_id},
                )
                if r.status_code == 200:
                    data = r.json()
                    return f"Errors: {data.get('errors', [])}. Probable cause: {data.get('probable_cause', 'unknown')}"
        except Exception as exc:
            logger.warning({"event": "logs_service_unavailable", "error": str(exc)})
        return ""

    @staticmethod
    def _assess_severity(hypotheses) -> IncidentSeverity:
        if not hypotheses:
            return IncidentSeverity.MEDIUM
        max_conf = max(h.confidence for h in hypotheses)
        if max_conf >= 0.85:
            return IncidentSeverity.CRITICAL
        if max_conf >= 0.6:
            return IncidentSeverity.HIGH
        if max_conf >= 0.35:
            return IncidentSeverity.MEDIUM
        return IncidentSeverity.LOW
