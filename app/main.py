from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title="Orisync",
    description=(
        "Supply chain event tracking API with webhook delivery, "
        "observability, and role-based access control."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware allows web browsers to call this API
# from a different domain. In production, replace "*"
# with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.is_production else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus instrumentation: automatically tracks request
# count, latency, and error rate for every route.
# The /metrics endpoint is exposed for Prometheus to scrape.
Instrumentator().instrument(app).expose(app)

# Register all API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health_check():
    """
    Public health check endpoint.
    Load balancers and monitoring tools call this to verify
    the application is running.
    """
    return {"status": "healthy", "service": "orisync"}
