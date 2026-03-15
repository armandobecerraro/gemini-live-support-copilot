"""
Pydantic schemas for request/response validation.
Separated from domain models to follow Clean Architecture.
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import base64


class IssueRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=4000)
    logs: Optional[str] = Field(None, max_length=50000)
    image_base64: Optional[str] = Field(None, description="Base64-encoded screenshot")
    session_id: Optional[str] = None

    @field_validator("image_base64")
    @classmethod
    def validate_image(cls, v):
        if v:
            try:
                base64.b64decode(v, validate=True)
            except Exception:
                raise ValueError("image_base64 must be valid base64")
        return v


class ActionConfirmRequest(BaseModel):
    session_id: str
    action_id: str
    approved: bool


class AgentResponse(BaseModel):
    session_id: str
    correlation_id: str
    what_i_understood: str
    what_i_see: Optional[str] = None
    root_cause_summary: Optional[str] = None
    recommendations: List[str]
    next_action: Optional[str] = None
    hypotheses: List[dict] = []
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    needs_more_info: bool = False
    suggested_actions: List[dict] = []


class SessionSummaryResponse(BaseModel):
    session_id: str
    problem_summary: str
    incident_category: str
    severity: str
    resolved: bool
    timeline: List[dict]
    markdown_report: str


class LogAnalysisRequest(BaseModel):
    raw_logs: str = Field(..., min_length=1, max_length=100000)
    session_id: Optional[str] = None


class LogAnalysisResponse(BaseModel):
    errors: List[str]
    warnings: List[str]
    anomalies: List[str]
    probable_cause: str
    timestamp_range: Optional[str] = None
