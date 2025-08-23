from flask import request, jsonify
from services.chat_service import ChatService

class ChatController:
    def __init__(self):
        """Initialize chat controller with service"""
        self.chat_service = ChatService()
    
    def verify_whatsapp_webhook(self):
        """Verify WhatsApp webhook callback URL"""
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        # Use the WhatsApp service to verify the webhook
        result = self.chat_service.whatsapp_service.verify_webhook(mode, token, challenge)
        if result:
            return result
        else:
            return "Verification failed", 403
    
    def handle_whatsapp_webhook(self):
        """Handle WhatsApp webhook requests"""
        try:
            # Get the JSON data from the webhook
            data = request.get_json()
            print(f"Received webhook data: {data}")
            
            # Parse the message using WhatsApp service
            phone, user_msg = self.chat_service.whatsapp_service.parse_webhook_message(data)
            
            if not phone or not user_msg:
                return jsonify({"status": "no_message"}), 200
                
            print(f"User message: {user_msg}")
            
            # Process the message
            response_text = self.chat_service.process_user_message(user_msg, phone)
            print(f"Response: {response_text}")
            
            # Send the response back to the user
            success, result = self.chat_service.whatsapp_service.send_message(phone, response_text)
            
            if success:
                return jsonify({"status": "success"}), 200
            else:
                print(f"Failed to send message: {result}")
                return jsonify({"status": "error", "message": result}), 200
                
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 200  # Return 200 to acknowledge receipt
    
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