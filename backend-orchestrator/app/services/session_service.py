"""
Session Service — manages short-term session state with Redis.
"""
import json
import logging
import uuid
import redis.asyncio as redis
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from app.config import get_settings
from app.domain.models import SessionState, IncidentCategory, IncidentSeverity, Hypothesis, SuggestedAction, ActionStatus

logger = logging.getLogger("supportsight.session")
settings = get_settings()

class SessionService:
    def __init__(self, redis_url: str = settings.REDIS_URL):
        # Fallback to in-memory if redis_url is not a valid redis URL or is missing
        self._redis = None
        self._use_redis = False
        
        if redis_url and any(scheme in redis_url for scheme in ["redis://", "rediss://", "unix://"]):
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._use_redis = True
                logger.info(f"SessionService using Redis at {redis_url.split('@')[-1]}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory.")
        else:
            logger.warning(f"Invalid or missing REDIS_URL. Falling back to in-memory store.")
            
        self._ttl = settings.SESSION_TTL_SECONDS
        self._memory_store = {} # Fallback store

    async def get_or_create(self, session_id: str, correlation_id: str) -> SessionState:
        state = await self.get(session_id)
        if state:
            return state
        return SessionState(session_id=session_id, correlation_id=correlation_id)

    async def save(self, state: SessionState):
        if self._use_redis:
            try:
                data = self._serialize(state)
                await self._redis.setex(
                    f"session:{state.session_id}",
                    self._ttl,
                    json.dumps(data)
                )
                return
            except Exception as e:
                logger.error(f"Error saving session to Redis: {e}")
        
        # Fallback to memory
        self._memory_store[f"session:{state.session_id}"] = state

    async def get(self, session_id: str) -> Optional[SessionState]:
        if self._use_redis:
            try:
                raw = await self._redis.get(f"session:{session_id}")
                if not raw:
                    return None
                return self._deserialize(json.loads(raw))
            except Exception as e:
                logger.error(f"Error retrieving session from Redis: {e}")
        
        return self._memory_store.get(f"session:{session_id}")
            if not raw:
                return None
            return self._deserialize(json.loads(raw))
        except Exception as e:
            logger.error(f"Error retrieving session from Redis: {e}")
            return None

    def _serialize(self, state: SessionState) -> dict:
        data = asdict(state)
        data["created_at"] = state.created_at.isoformat()
        # Convert enums to values for JSON serialization
        data["incident_category"] = state.incident_category.value
        data["severity"] = state.severity.value
        data["active_hypotheses"] = [
            {**asdict(h), "category": h.category.value}
            for h in state.active_hypotheses
        ]
        data["pending_actions"] = [
            {**asdict(a), "status": a.status.value}
            for a in state.pending_actions
        ]
        return data

    def _deserialize(self, data: dict) -> SessionState:
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["incident_category"] = IncidentCategory(data["incident_category"])
        data["severity"] = IncidentSeverity(data["severity"])
        
        data["active_hypotheses"] = [
            Hypothesis(**{**h, "category": IncidentCategory(h["category"])})
            for h in data.get("active_hypotheses", [])
        ]
        data["pending_actions"] = [
            SuggestedAction(**{**a, "status": ActionStatus(a["status"])})
            for a in data.get("pending_actions", [])
        ]
        return SessionState(**data)
