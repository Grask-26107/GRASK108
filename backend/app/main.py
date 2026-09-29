import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.services.seed_data import seed_database_if_empty

from app.api.chat import router as chat_router
from app.api.standards import router as standards_router
from app.api.audit import router as audit_router
from app.api.feedback import router as feedback_router
from app.api.telemetry import router as telemetry_router
from app.api.certificates import router as certificates_router
from app.api.procurement import router as procurement_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bis_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing BIS Intelligent Assistant backend...")
    # Initialize SQLite database
    init_db()
    # Seed out-of-the-box BIS standards
    seed_database_if_empty()
    logger.info("System ready for queries, audits, and uploads.")
    yield
    logger.info("Shutting down BIS Intelligent Assistant backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-powered Intelligent Assistant for Indian Standards (BIS) - SIH26107",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.security_firewall import DefensiveSecurityMiddleware

app.add_middleware(DefensiveSecurityMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An error occurred while processing your request. All system paths and hardware telemetry have been protected.",
            "status": "ERROR"
        }
    )


# Register API Routers
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(standards_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(certificates_router, prefix=settings.API_V1_STR)
app.include_router(procurement_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/health", tags=["Health"])
def health_check(refresh: bool = False):
    from app.core.gemini_manager import gemini_manager
    gemini_health = gemini_manager.check_health(force_refresh=refresh)
    return {
        "status": "healthy" if gemini_health.get("is_healthy", False) else "degraded",
        "gemini_online": gemini_health.get("gemini_online", False),
        "active_model": gemini_health.get("active_model", settings.GEMINI_MODEL),
        "available_models": gemini_health.get("available_models", []),
        "latency_ms": gemini_health.get("latency_ms", 0),
        "message": gemini_health.get("message", "Operational"),
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "chroma_storage": settings.CHROMA_PERSIST_DIR,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/health/gemini", tags=["Health"])
def gemini_health_status(refresh: bool = False):
    from app.core.gemini_manager import gemini_manager
    return gemini_manager.check_health(force_refresh=refresh)
