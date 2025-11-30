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
        """
        Internal method to send requests to WhatsApp API.
        
        Args:
            endpoint: API endpoint (e.g., "messages")
            payload: JSON payload
            
        Returns:
            Response JSON or None if failed
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code not in [200, 201]:
                    logger.error(f"WhatsApp API Error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to send request to WhatsApp: {str(e)}")
            return None

    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a received message as read.
        
        Args:
            message_id: The ID of the message to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

    async def send_text_message(self, to_phone: str, content: str) -> bool:
        """
        Send a standard text message.
        
        Args:
            to_phone: Recipient's phone number
            content: Text content to send
            
        Returns:
            True if successful, False otherwise
        """
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
        """
        Send a message with interactive buttons (max 3).
        
        Args:
            to_phone: Recipient's phone number
            body_text: Main text of the message
            buttons: List of dicts with 'id' and 'title' keys
                     e.g. [{'id': 'btn1', 'title': 'Button 1'}]
            
        Returns:
            True if successful, False otherwise
        """
        # Format buttons for WhatsApp API
        formatted_buttons = []
        for btn in buttons:
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"]
                }
            })
            
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }
        
        result = await self._send_request("messages", payload)
        return result is not None

# Global instance
whatsapp_service = WhatsAppService()