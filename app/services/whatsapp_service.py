"""
WhatsApp Service for Chatlingo AI

Handles all outgoing communication with the WhatsApp Cloud API.
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for interacting with WhatsApp Cloud API"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v22.0/{settings.whatsapp_phone_id}"
        self.headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }
    
    async def _send_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Internal method to send requests to WhatsApp API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code not in [200, 201]:
                    logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"WhatsApp request timeout: {endpoint}")
            return None
        except Exception as e:
            logger.error(f"WhatsApp request failed: {e}")
            return None

    async def mark_message_as_read(self, message_id: str) -> bool:
        """Mark a received message as read"""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

    async def send_text_message(self, to_phone: str, content: str) -> bool:
        """Send a standard text message"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": content
            }
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

    async def send_interactive_buttons(self, to_phone: str, body_text: str, buttons: List[Dict[str, str]]) -> bool:
        """Send a message with interactive buttons (max 3)"""
        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"]
                }
            }
            for btn in buttons
        ]
            
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": formatted_buttons}
            }
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

    async def send_interactive_list_message(self, to_phone: str, body_text: str, button_text: str, 
                                           sections: List[Dict[str, Any]]) -> bool:
        """Send a message with a list menu (up to 10 items)"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

# Global instance
whatsapp_service = WhatsAppService()
