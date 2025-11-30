"""
WhatsApp Webhook Router

Handles the verification and reception of WhatsApp webhooks.
"""

from fastapi import APIRouter, Query, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.config import settings
from app.schemas.whatsapp import WhatsAppWebhook
from app.services.message_processor import message_processor
import logging

router = APIRouter(
    prefix="/whatsapp-webhook",
    tags=["webhook"]
)

logger = logging.getLogger(__name__)

@router.get("")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    """
    Webhook verification endpoint.
    WhatsApp sends a GET request to verify the webhook URL.
    """
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully!")
        return PlainTextResponse(content=challenge, status_code=200)
    
    logger.warning("Webhook verification failed. Invalid token.")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(
    payload: WhatsAppWebhook,
    background_tasks: BackgroundTasks
):
    """
    Receive incoming WhatsApp messages.
    """
    # Process in background to return 200 OK immediately
    background_tasks.add_task(message_processor.process_webhook, payload)
    
    return {"status": "received"}