"""
WhatsApp Webhook Router

Handles the verification and reception of WhatsApp webhooks.
"""

import json
import logging

from fastapi import APIRouter, Query, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from app.config import settings
from app.schemas.whatsapp import WhatsAppWebhook
from app.services.message_processor import message_processor

router = APIRouter(
    prefix="/whatsapp-webhook",
    tags=["whatsapp"]
)

logger = logging.getLogger(__name__)

@router.get("")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
):
    """Webhook verification endpoint for WhatsApp"""
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return PlainTextResponse(content=challenge, status_code=200)
    
    logger.warning("WhatsApp webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive incoming WhatsApp messages"""
    try:
        raw_body = await request.body()
        raw_json = json.loads(raw_body)
    except Exception as e:
        logger.error(f"Failed to parse webhook body: {e}")
        return {"status": "received"}
    
    try:
        payload = WhatsAppWebhook(**raw_json)
    except ValidationError as e:
        logger.error(f"Webhook validation failed: {e}")
        return {"status": "received"}
    
    background_tasks.add_task(message_processor.process_webhook, payload)
    return {"status": "received"}
