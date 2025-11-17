"""
FastAPI application for Distributed Compute Marketplace.

This is the main entry point for the API server.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import routers
from src.api import (
    auth, nodes, offers, jobs,
    analytics, cost_estimation,
    notifications, preferences,
    websocket_monitoring
)

# Create FastAPI app
app = FastAPI(
    title="Distributed Compute Marketplace",
    description="P2P marketplace for sharing computing resources among friends",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Global exception handler for HTTP exceptions.

    Ensures all HTTP errors return JSON responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global exception handler for request validation errors.

    Returns structured JSON for validation failures.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.

    Catches all other exceptions and returns a generic 500 error.
    """
    # Log the exception (will add proper logging in Task 15)
    print(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(nodes.router, prefix="/nodes", tags=["Nodes"])
app.include_router(offers.router, prefix="/offers", tags=["Resource Offers"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(cost_estimation.router, prefix="/cost", tags=["Cost Estimation"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
app.include_router(websocket_monitoring.router, prefix="/ws", tags=["WebSocket Monitoring"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {"status": "ok", "service": "compute-marketplace-api"}
