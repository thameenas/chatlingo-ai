"""
Pydantic schemas for Chatlingo AI

Exports all schema classes from db and whatsapp modules for easy importing.
"""

# Database schemas
from app.schemas.db import (
    UserSchema,
    ScenarioSchema,
    ChatMessageSchema,
    UserProgressSchema
)

# WhatsApp webhook schemas
from app.schemas.whatsapp import (
    TextObject,
    ButtonReply,
    InteractiveObject,
    WhatsAppMessage,
    ValueObject,
    ChangeObject,
    EntryObject,
    WhatsAppWebhook
)

__all__ = [
    # Database schemas
    "UserSchema",
    "ScenarioSchema",
    "ChatMessageSchema",
    "UserProgressSchema",
    # WhatsApp schemas
    "TextObject",
    "ButtonReply",
    "InteractiveObject",
    "WhatsAppMessage",
    "ValueObject",
    "ChangeObject",
    "EntryObject",
    "WhatsAppWebhook",
]