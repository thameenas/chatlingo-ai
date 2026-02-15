"""
Chatlingo AI - Main FastAPI application

Entry point for the WhatsApp chatbot backend.
"""

import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import webhook
import logging

# Configure logging - force output to stdout for Render visibility
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,  # Render captures stdout
    force=True  # Override any existing handlers
)

# Ensure all loggers propagate to root
for name in ["app", "app.routers", "app.services", "uvicorn", "uvicorn.error"]:
    logging.getLogger(name).setLevel(logging.DEBUG if settings.debug else logging.INFO)

logger = logging.getLogger(__name__)

logger.info(f"🚀 Chatlingo AI starting up | env={settings.environment} | debug={settings.debug} | llm={settings.llm_provider}/{settings.llm_model}")

# Initialize FastAPI app
app = FastAPI(
    title="Chatlingo AI",
    description="WhatsApp chatbot for teaching Bangalore Kannada in Kanglish",
    version="0.1.0",
    debug=settings.debug
)

# Include routers
app.include_router(webhook.router)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.info("[HEALTH] Health check requested")
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.environment
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Chatlingo AI in {settings.environment} mode")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )