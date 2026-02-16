"""
Telegram Bot webhook endpoints.

Handles incoming updates from Telegram Bot API.
"""

from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from app.schemas.telegram import TelegramUpdate
from app.services.message_processor import MessageProcessor
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/telegram-webhook")
async def telegram_webhook(
    update: TelegramUpdate,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    """
    Receive incoming Telegram updates.
    
    Telegram will POST updates to this endpoint.
    Optional: Verify secret token for security.
    """
    from app.services.telegram_service import telegram_service
    
    # Check if Telegram is configured
    if not telegram_service:
        logger.error("Telegram webhook called but TELEGRAM_BOT_TOKEN not configured")
        raise HTTPException(
            status_code=503,
            detail="Telegram not configured. Please set TELEGRAM_BOT_TOKEN in environment variables."
        )
    
    # Verify secret token if configured
    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            logger.warning("Invalid Telegram webhook secret token")
            raise HTTPException(status_code=403, detail="Forbidden")
    
    logger.info(f"Received Telegram update: {update.update_id}")
    
    # Process update in background to return 200 OK quickly
    background_tasks.add_task(
        MessageProcessor.process_telegram_update,
        update
    )
    
    return {"status": "ok"}


@router.get("/telegram-webhook-info")
async def get_webhook_info():
    """
    Get current Telegram webhook configuration.
    Useful for debugging.
    """
    from app.services.telegram_service import telegram_service
    
    if not telegram_service:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    try:
        info = await telegram_service.get_webhook_info()
        return info
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
