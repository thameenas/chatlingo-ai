"""
Chatlingo AI - Main FastAPI application

Entry point for the WhatsApp chatbot backend.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chatlingo AI",
    description="WhatsApp chatbot for teaching Bangalore Kannada in Kanglish",
    version="0.1.0",
    debug=settings.debug
)

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
    logger.info(f"Starting Chatlingo AI in {settings.environment} mode")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )