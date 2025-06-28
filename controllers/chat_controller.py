from flask import request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from services.chat_service import ChatService

class ChatController:
    def __init__(self):
        """Initialize chat controller with service"""
        self.chat_service = ChatService()
    
    def handle_whatsapp_webhook(self):
        """Handle WhatsApp webhook requests"""
        user_msg = request.form.get("Body", "").strip().lower()
        phone = request.form.get("From", "").replace("whatsapp:", "")
        print(f"User message: {user_msg}")
        
        try:
            response_text = self.chat_service.process_user_message(user_msg, phone)
            print(f"Response: {response_text}")
            twilio_resp = MessagingResponse()
            twilio_resp.message(response_text)
            return str(twilio_resp)
        except Exception as e:
            print(e)
            return f"⚠️ Error: {str(e)}", 200
    
    def handle_web_chat(self):
        """Handle web chat interface requests"""
        data = request.get_json()
        user_msg = data.get("user_msg", "")
        session_id = data.get("session_id", "")
        
        if not user_msg or not session_id:
            return jsonify({"error": "Missing user_msg or session_id"}), 400
        
        try:
            response = self.chat_service.process_user_message(user_msg, session_id)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def handle_reset_chat(self):
        """Handle chat history reset requests"""
        data = request.get_json()
        session_id = data.get("session_id", "")
        
        if not session_id:
            return jsonify({"error": "Missing session_id"}), 400
        
        try:
            self.chat_service.reset_chat_history(session_id)
            return jsonify({"response": "Chat history cleared"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def handle_manual_nudge(self):
        """Handle manual nudge trigger requests"""
        try:
            self.chat_service.send_daily_nudges()
            return jsonify({"response": "Daily nudges sent successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500 