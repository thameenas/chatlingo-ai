"""
Platform adapter to provide a unified interface for both WhatsApp and Telegram.

Simplified version - direct delegation without Protocol overhead.
"""

import logging
from typing import List, Dict, Any
from app.services.whatsapp_service import WhatsAppService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


class WhatsAppAdapter:
    """Adapter for WhatsApp messaging"""
    
    def __init__(self, service: WhatsAppService):
        self.service = service
    
    async def send_text(self, user_id: str, text: str) -> None:
        await self.service.send_text_message(user_id, text)
    
    async def send_menu_buttons(self, user_id: str, text: str, buttons: List[Dict[str, str]]) -> None:
        await self.service.send_interactive_buttons(user_id, text, buttons)
    
    async def send_menu_list(self, user_id: str, text: str, button_text: str, items: List[Dict[str, str]]) -> None:
        sections = [{"title": "Options", "rows": items}]
        await self.service.send_interactive_list_message(user_id, text, button_text, sections)


class TelegramAdapter:
    """Adapter for Telegram messaging"""
    
    def __init__(self, service: TelegramService):
        self.service = service
    
    async def send_text(self, user_id: str, text: str) -> None:
        chat_id = int(user_id)
        await self.service.send_text_message(chat_id, text)
    
    async def send_menu_buttons(self, user_id: str, text: str, buttons: List[Dict[str, str]]) -> None:
        chat_id = int(user_id)
        inline_keyboard = [[{"text": btn["title"], "callback_data": btn["id"]}] for btn in buttons]
        await self.service.send_inline_keyboard(chat_id, text, inline_keyboard)
    
    async def send_menu_list(self, user_id: str, text: str, button_text: str, items: List[Dict[str, str]]) -> None:
        chat_id = int(user_id)
        inline_keyboard = [[{"text": item["title"], "callback_data": item["id"]}] for item in items]
        await self.service.send_inline_keyboard(chat_id, text, inline_keyboard)


def get_platform_adapter(platform: str, service: Any):
    """Get the appropriate platform adapter"""
    if platform == "whatsapp":
        return WhatsAppAdapter(service)
    elif platform == "telegram":
        return TelegramAdapter(service)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
