"""
Ozon Parser API
FastAPI application for parsing competitor prices from Ozon
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import parse, health
from api.services.ozon_parser import OzonParserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Ozon Parser API...")

    # Initialize parser service
    app.state.parser = OzonParserService()
    await app.state.parser.start()
    logger.info("Parser service initialized")

    yield

    # Cleanup
    logger.info("Shutting down...")
    await app.state.parser.close()


app = FastAPI(
    title="Ozon Parser API",
    description="API for parsing competitor prices from Ozon marketplace",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(parse.router, prefix="/api", tags=["Parser"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Ozon Parser API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }
