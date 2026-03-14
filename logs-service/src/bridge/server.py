"""
Logs Service — Python FastAPI bridge over Rust log parser.
Falls back to pure Python parsing if Rust extension not compiled.
"""
import re
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supportsight.logs")

app = FastAPI(title="SupportSight Logs Service", version="1.0.0")

try:
    import log_parser  # Rust PyO3 extension
    USE_RUST = True
    logger.info("Using Rust log parser (high-performance mode)")
except ImportError:
    USE_RUST = False
    logger.warning("Rust parser not available — using Python fallback")


class LogRequest(BaseModel):
    raw_logs: str
    session_id: Optional[str] = None


class LogResponse(BaseModel):
    errors: List[str]
    warnings: List[str]
    anomalies: List[str]
    probable_cause: str
    timestamp_range: Optional[str] = None
    total_lines: int = 0
    error_rate: float = 0.0


def _python_parse(raw: str) -> dict:
    lines = raw.splitlines()
    errors = [l for l in lines if re.search(r"ERROR|FATAL|EXCEPTION", l, re.IGNORECASE)]
    warnings = [l for l in lines if re.search(r"WARN", l, re.IGNORECASE)]
    cause = "No errors detected."
    if errors:
        if "Connection refused" in " ".join(errors):
            cause = "Service connectivity failure."
        elif "OutOfMemory" in " ".join(errors):
            cause = "Memory exhaustion."
        elif "timeout" in " ".join(errors).lower():
            cause = "Timeout cascade."
        else:
            cause = f"Application error in {len(errors)} log lines."
    return {
        "errors": [e[:300] for e in errors[:50]],
        "warnings": [w[:300] for w in warnings[:30]],
        "anomalies": [],
        "probable_cause": cause,
        "timestamp_range": None,
        "total_lines": len(lines),
        "error_rate": len(errors) / max(len(lines), 1),
    }


@app.get("/")
async def root():
    return {"status": "ok", "service": "logs-service", "rust_parser": USE_RUST}


@app.get("/health")
async def health():
    return {"status": "ok", "rust_parser": USE_RUST}


@app.post("/analyze", response_model=LogResponse)
async def analyze(body: LogRequest):
    logger.info({"event": "analyze_logs", "session_id": body.session_id, "lines": body.raw_logs.count("\n")})
    if USE_RUST:
        import json
        result = json.loads(log_parser.parse_logs_py(body.raw_logs))
        result["errors"] = [e["message"] for e in result.get("errors", [])]
        result["warnings"] = [w["message"] for w in result.get("warnings", [])]
    else:
        result = _python_parse(body.raw_logs)
    return LogResponse(**result)
