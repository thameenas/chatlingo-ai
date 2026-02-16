"""
Telegram Bot API service for sending messages and managing bot interactions.
"""

import httpx
import logging
from typing import List, Dict
from app.config import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for interacting with Telegram Bot API"""
    
    def __init__(self):
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_text_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> dict:
        """Send a text message to a Telegram chat"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                logger.error(f"Telegram API error: {result.get('description')}")
                raise Exception(f"Telegram API error: {result.get('description')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def send_inline_keyboard(self, chat_id: int, text: str, buttons: List[List[Dict[str, str]]], 
                                   parse_mode: str = "Markdown") -> dict:
        """Send a message with inline keyboard buttons"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "reply_markup": {"inline_keyboard": buttons}
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                logger.error(f"Telegram API error: {result.get('description')}")
                raise Exception(f"Telegram API error: {result.get('description')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error sending inline keyboard: {e}")
            raise
    
    async def answer_callback_query(self, callback_query_id: str, text: str = None, 
                                    show_alert: bool = False) -> dict:
        """Answer a callback query from an inline button press"""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        
        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = show_alert
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            raise
    
    async def set_webhook(self, webhook_url: str, secret_token: str = None) -> dict:
        """Set the webhook URL for receiving updates"""
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        
        if secret_token:
            payload["secret_token"] = secret_token
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Webhook set to: {webhook_url}")
            return result
        
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            raise
    
    async def get_webhook_info(self) -> dict:
        """Get current webhook status"""
        url = f"{self.base_url}/getWebhookInfo"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
telegram_service = TelegramService() if settings.telegram_bot_token else None
