"""
WhatsApp Webhook Pydantic models for Chatlingo AI

These models parse the incoming WhatsApp Cloud API webhook JSON payloads.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class TextObject(BaseModel):
    """Text message content"""
    body: str


class ButtonReply(BaseModel):
    """Button reply from interactive message"""
    id: str
    title: str


class InteractiveObject(BaseModel):
    """Interactive message (buttons, lists, etc.)"""
    type: str
    button_reply: Optional[ButtonReply] = None


class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message"""
    from_: str = Field(alias='from')
    id: str
    type: str
    text: Optional[TextObject] = None
    interactive: Optional[InteractiveObject] = None


class ValueObject(BaseModel):
    """Value object containing messages"""
    messaging_product: str
    messages: Optional[List[WhatsAppMessage]] = None


class ChangeObject(BaseModel):
    """Change object containing value"""
    value: ValueObject


class EntryObject(BaseModel):
    """Entry object containing changes"""
    changes: List[ChangeObject]


class WhatsAppWebhook(BaseModel):
    """Root webhook payload from WhatsApp"""
    object: str
    entry: List[EntryObject]