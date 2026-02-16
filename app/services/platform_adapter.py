"""
Platform adapter to provide a unified interface for both WhatsApp and Telegram.

This allows the message processor to work with both platforms without
knowing the implementation details of each.
"""

from typing import Protocol, List, Dict, Any, Optional
from app.services.whatsapp_service import WhatsAppService
from app.services.telegram_service import TelegramService


class MessagingPlatform(Protocol):
    """Protocol defining the interface all messaging platforms must implement"""
    
    async def send_text(self, user_id: str, text: str) -> None:
        """Send a plain text message"""
        ...
    
    async def send_menu_buttons(
        self, 
        user_id: str, 
        text: str, 
        buttons: List[Dict[str, str]]
    ) -> None:
        """Send a message with button options"""
        ...
    
    async def send_menu_list(
        self, 
        user_id: str, 
        text: str, 
        button_text: str,
        items: List[Dict[str, str]]
    ) -> None:
        """Send a message with a list menu"""
        ...


class WhatsAppAdapter:
    """Adapter for WhatsApp to conform to MessagingPlatform protocol"""
    
    def __init__(self, service: WhatsAppService):
        self.service = service
    
    async def send_text(self, user_id: str, text: str) -> None:
        """Send text message via WhatsApp"""
        await self.service.send_text_message(user_id, text)
    
    async def send_menu_buttons(
        self, 
        user_id: str, 
        text: str, 
        buttons: List[Dict[str, str]]
    ) -> None:
        """
        Send interactive buttons via WhatsApp.
        
        Args:
            buttons: List of dicts with 'id' and 'title' keys
        """
        await self.service.send_interactive_buttons(user_id, text, buttons)
    
    async def send_menu_list(
        self, 
        user_id: str, 
        text: str, 
        button_text: str,
        items: List[Dict[str, str]]
    ) -> None:
        """
        Send list menu via WhatsApp.
        
        Args:
            items: List of dicts with 'id', 'title', and optional 'description'
        """
        sections = [{"title": "Options", "rows": items}]
        await self.service.send_interactive_list_message(
            user_id, 
            text, 
            button_text, 
            sections
        )


class TelegramAdapter:
    """Adapter for Telegram to conform to MessagingPlatform protocol"""
    
    def __init__(self, service: TelegramService):
        self.service = service
    
    async def send_text(self, user_id: str, text: str) -> None:
        """Send text message via Telegram"""
        chat_id = int(user_id)
        await self.service.send_text_message(chat_id, text)
    
    async def send_menu_buttons(
        self, 
        user_id: str, 
        text: str, 
        buttons: List[Dict[str, str]]
    ) -> None:
        """
        Send inline keyboard buttons via Telegram.
        
        Args:
            buttons: List of dicts with 'id' and 'title' keys
        """
        chat_id = int(user_id)
        
        # Convert to Telegram inline keyboard format
        # Each button on its own row for better mobile UX
        inline_keyboard = [
            [{"text": btn["title"], "callback_data": btn["id"]}]
            for btn in buttons
        ]
        
        await self.service.send_inline_keyboard(chat_id, text, inline_keyboard)
    
    async def send_menu_list(
        self, 
        user_id: str, 
        text: str, 
        button_text: str,
        items: List[Dict[str, str]]
    ) -> None:
        """
        Send list as inline keyboard via Telegram.
        
        Args:
            items: List of dicts with 'id', 'title', and optional 'description'
        """
        chat_id = int(user_id)
        
        # Format text with list items
        formatted_text = f"{text}\n\n"
        
        # Convert to inline keyboard
        inline_keyboard = [
            [{"text": item["title"], "callback_data": item["id"]}]
            for item in items
        ]
        
        await self.service.send_inline_keyboard(chat_id, formatted_text, inline_keyboard)


def get_platform_adapter(platform: str, service: Any) -> MessagingPlatform:
    """
    Factory function to get the appropriate platform adapter.
    
    Args:
        platform: 'whatsapp' or 'telegram'
        service: The platform-specific service instance
    
    Returns:
        Platform adapter implementing MessagingPlatform protocol
    """
    if platform == "whatsapp":
        return WhatsAppAdapter(service)
    elif platform == "telegram":
        return TelegramAdapter(service)
    else:
        raise ValueError(f"Unsupported platform: {platform}")
