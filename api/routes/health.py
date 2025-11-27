"""Health check endpoint"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check for Northflank"""
    return {
        "status": "ok",
        "service": "ozon-parser-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
