"""
FastAPI application for Distributed Compute Marketplace.

This is the main entry point for the API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from src.api import auth

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

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {"status": "ok", "service": "compute-marketplace-api"}
