"""Main FastAPI application with modular router architecture."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import health, faq


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI()
    
    # Include routers
    app.include_router(health.router)
    app.include_router(faq.router)
    
    return app


# Create the app instance
app = create_app()