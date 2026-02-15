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
        logger.info(f"[WHATSAPP] 📤 Sending request to {endpoint}: type={payload.get('type', 'N/A')}, to={payload.get('to', 'N/A')}")
        logger.debug(f"[WHATSAPP] Full payload: {payload}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code not in [200, 201]:
                    logger.error(f"[WHATSAPP] ❌ API Error: status={response.status_code}, response={response.text}")
                    return None
                
                result = response.json()
                logger.info(f"[WHATSAPP] ✅ API Success: status={response.status_code}")
                logger.debug(f"[WHATSAPP] Response body: {result}")
                return result
                
        except httpx.TimeoutException:
            logger.error(f"[WHATSAPP] ❌ Request timed out for {endpoint}")
            return None
        except Exception as e:
            logger.error(f"[WHATSAPP] ❌ Failed to send request: {str(e)}")
            import traceback
            logger.error(f"[WHATSAPP] ❌ Traceback:\n{traceback.format_exc()}")
            return None

    async def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a received message as read.
        """
        logger.info(f"[WHATSAPP] 👁️ Marking message as read: {message_id}")
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        result = await self._send_request("messages", payload)
        success = result is not None
        logger.info(f"[WHATSAPP] Mark as read: success={success}")
        return success

    async def send_text_message(self, to_phone: str, content: str) -> bool:
        """Send a standard text message."""
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
        success = result is not None
        logger.info(f"[WHATSAPP] Text message sent: success={success}")
        return success

    async def send_interactive_buttons(self, to_phone: str, body_text: str, buttons: List[Dict[str, str]]) -> bool:
        """Send a message with interactive buttons (max 3)."""
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
        success = result is not None
        logger.info(f"[WHATSAPP] Interactive buttons sent: success={success}")
        return success

    async def send_interactive_list_message(self, to_phone: str, body_text: str, button_text: str, sections: List[Dict[str, Any]]) -> bool:
        """Send a message with a list menu (up to 10 items)."""
        logger.info(f"[WHATSAPP] 📋 Sending interactive list to {to_phone}: button='{button_text}'")
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        result = await self._send_request("messages", payload)
        success = result is not None
        logger.info(f"[WHATSAPP] Interactive list sent: success={success}")
        return success

# Global instance
whatsapp_service = WhatsAppService()