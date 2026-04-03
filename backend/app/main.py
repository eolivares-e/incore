from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.exceptions import InsuranceCoreError
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.domains.billing.router import router as billing_router
from app.domains.policies.router import router as policies_router
from app.domains.policy_holders.router import router as policy_holders_router
from app.domains.pricing.router import (
    pricing_rules_router,
    quotes_router,
)
from app.domains.underwriting.router import router as underwriting_router
from app.domains.users.router import auth_router, users_router
from app.workflows.router import router as workflows_router

# Configure logging before app initialization
configure_logging(log_format=settings.LOG_FORMAT, log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Insurance Core Backend API",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(policy_holders_router, prefix=settings.API_V1_STR)
app.include_router(policies_router, prefix=settings.API_V1_STR)
app.include_router(quotes_router, prefix=settings.API_V1_STR)
app.include_router(pricing_rules_router, prefix=settings.API_V1_STR)
app.include_router(underwriting_router, prefix=settings.API_V1_STR)
app.include_router(billing_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)

# Middleware (order matters - first added = outermost layer)
# 1. Request logging middleware (logs all requests/responses)
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/health/ready", "/health/live"],
)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(InsuranceCoreError)
async def insurance_core_exception_handler(
    request: Request, exc: InsuranceCoreError
) -> JSONResponse:
    """Handle all custom Insurance Core exceptions."""
    logger.warning(
        "insurance_core_error",
        error_type=type(exc).__name__,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        message=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": {"message": str(exc)} if settings.DEBUG else {},
        },
    )


# Root endpoints
@app.get("/")
def read_root():
    return {
        "message": "Insurance Core API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint.

    Checks:
    - API is running
    - Database connectivity
    - Returns version info

    Returns:
        200: All systems healthy
        503: Service unavailable (database down)
    """
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
        "checks": {},
    }

    # Check database connectivity
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error("health_check_database_failed", error=str(e))
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status,
        )

    return health_status


@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint.

    Checks if the application is ready to accept traffic.
    More comprehensive than liveness - checks database connectivity.

    Returns:
        200: Ready to accept traffic
        503: Not ready (database unavailable)
    """
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "reason": "database_unavailable"},
        )


@app.get("/health/live")
def liveness_check():
    """Kubernetes liveness probe endpoint.

    Simple check if the application is alive (not frozen/deadlocked).
    Does NOT check database or external dependencies.

    Returns:
        200: Application is alive
    """
    return {"status": "alive"}
