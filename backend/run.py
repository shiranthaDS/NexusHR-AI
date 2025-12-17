#!/usr/bin/env python3
"""
NexusHR AI Backend Server
Entry point for running the FastAPI application
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )
