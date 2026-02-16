"""
Chatlingo AI - Main FastAPI application

Entry point for the multi-platform chatbot backend.
"""

import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import whatsapp_webhook
from app.routers import telegram_webhook
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True
)

for name in ["app", "app.routers", "app.services", "uvicorn", "uvicorn.error"]:
    logging.getLogger(name).setLevel(logging.DEBUG if settings.debug else logging.INFO)

logger = logging.getLogger(__name__)

logger.info(f"Chatlingo AI starting | env={settings.environment} | llm={settings.llm_provider}/{settings.llm_model}")

# Initialize FastAPI app
app = FastAPI(
    title="Chatlingo AI",
    description="Multi-platform chatbot for teaching Bangalore Kannada in Kanglish (WhatsApp & Telegram)",
    version="0.2.0",
    debug=settings.debug
)

# Include routers
app.include_router(whatsapp_webhook.router)
app.include_router(telegram_webhook.router)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": settings.environment
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
