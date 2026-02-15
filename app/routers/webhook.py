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
    logger.info(f"[WEBHOOK-GET] Verification attempt: mode={mode}, token={'***' + token[-4:] if len(token) > 4 else '***'}")
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("[WEBHOOK-GET] ✅ Webhook verified successfully!")
        return PlainTextResponse(content=challenge, status_code=200)
    
    logger.warning("[WEBHOOK-GET] ❌ Webhook verification failed. Invalid token.")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive incoming WhatsApp messages.
    Accepts raw request body first, logs it, then parses with Pydantic.
    """
    # Step 1: Read and log raw payload BEFORE Pydantic parsing
    try:
        raw_body = await request.body()
        raw_json = json.loads(raw_body)
        logger.info(f"[WEBHOOK-POST] 📩 Raw payload received: {json.dumps(raw_json, indent=2)}")
    except Exception as e:
        logger.error(f"[WEBHOOK-POST] ❌ Failed to read/parse raw body: {e}")
        return {"status": "received"}  # Still return 200 to prevent WhatsApp retries
    
    # Step 2: Parse with Pydantic model
    try:
        payload = WhatsAppWebhook(**raw_json)
        logger.info("[WEBHOOK-POST] ✅ Pydantic validation passed")
    except ValidationError as e:
        logger.error(f"[WEBHOOK-POST] ❌ Pydantic validation FAILED: {e}")
        logger.error(f"[WEBHOOK-POST] Raw JSON that failed: {json.dumps(raw_json, indent=2)}")
        return {"status": "received"}  # Still return 200 to prevent WhatsApp retries
    
    # Step 3: Process in background to return 200 OK immediately
    logger.info("[WEBHOOK-POST] 🚀 Dispatching to background task")
    background_tasks.add_task(message_processor.process_webhook, payload)
    
    return {"status": "received"}