"""
SupportSight Live — Backend Orchestrator
Entry point: FastAPI application with lifespan, middleware and routers.
"""
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes import health, agent, session, logs

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)
logger = logging.getLogger("supportsight")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "startup", "version": settings.APP_VERSION, "env": settings.ENVIRONMENT})
    yield
    logger.info({"event": "shutdown"})


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multimodal incident support agent powered by Gemini Live API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get(settings.CORRELATION_ID_HEADER, str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response: Response = await call_next(request)
    response.headers[settings.CORRELATION_ID_HEADER] = correlation_id
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.error({"event": "unhandled_error", "correlation_id": correlation_id, "error": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "correlation_id": correlation_id},
    )


# ── Routers ──
@app.get("/")
async def root():
    return {"status": "ok", "service": "backend-orchestrator", "version": settings.APP_VERSION}


app.include_router(health.router, tags=["health"])
app.include_router(agent.router, prefix="/agent", tags=["agent"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
