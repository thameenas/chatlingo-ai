import os
import requests
import json

class WhatsAppService:
    def __init__(self):
        """Initialize WhatsApp service with API credentials"""
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        
        if not self.api_token or not self.phone_number_id:
            print("WARNING: WhatsApp API credentials not found in environment variables")
    
    def verify_webhook(self, mode, token, challenge):
        """Verify webhook callback URL"""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def parse_webhook_message(self, data):
        """Parse incoming webhook data from WhatsApp Cloud API"""
        try:
            if not data.get("object") or not data.get("entry"):
                return None, None
                
            entry = data["entry"][0]
            changes = entry.get("changes", [])
            
            if not changes or not changes[0].get("value") or not changes[0]["value"].get("messages"):
                return None, None
                
            message = changes[0]["value"]["messages"][0]
            
            if message.get("type") != "text":
                return None, None
                
            # Extract phone number and message text
            phone = message.get("from")
            text = message["text"]["body"].strip()
            
            return phone, text
        except Exception as e:
            print(f"Error parsing webhook message: {e}")
            return None, None
    
    def send_message(self, to_number, message_text):
        """Send a WhatsApp message using the Cloud API"""
        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                print(f"Error sending message: {response.text}")
                return False, response.text
                
            return True, response.json()
        except Exception as e:
            print(f"Exception sending message: {e}")
            return False, str(e)