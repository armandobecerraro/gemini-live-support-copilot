"""
Incident Analyst Agent — formulates hypotheses and classifies incident.
"""
import json
import logging
from app.domain.models import Hypothesis, IncidentCategory
from app.infrastructure.gemini.client import GeminiClient
from app.prompts.loader import load_prompt

logger = logging.getLogger("supportsight.agents.analyst")


class IncidentAnalystAgent:
    def __init__(self, gemini: GeminiClient):
        self._gemini = gemini

    async def analyze(
        self,
        description: str,
        visual_context: str,
        log_summary: str,
    ) -> tuple[list[Hypothesis], IncidentCategory, str]:
        """Return prioritized hypotheses, incident category, and root cause summary."""
        prompt = load_prompt("incident_analysis").format(
            description=description,
            visual_context=visual_context or "No visual context provided.",
            log_summary=log_summary or "No logs provided.",
        )
        raw = await self._gemini.generate(prompt)
        try:
            parsed = json.loads(raw.strip("```json\n").strip("```"))
            hypotheses = [
                Hypothesis(
                    description=h["description"],
                    confidence=float(h.get("confidence", 0.5)),
                    evidence=h.get("evidence", []),
                    category=IncidentCategory(h.get("category", "unknown")),
                )
                for h in parsed.get("hypotheses", [])
            ]
            category = IncidentCategory(parsed.get("category", "unknown"))
            root_cause = parsed.get("root_cause_summary", "Unknown root cause.")
        except Exception as exc:
            logger.warning({"event": "analyst_parse_error", "error": str(exc), "raw": raw[:200]})
            hypotheses = [Hypothesis(description="Parsing error in analysis.", confidence=0.0)]
            category = IncidentCategory.UNKNOWN
            root_cause = "Analysis failed due to format error."
        return hypotheses, category, root_cause
