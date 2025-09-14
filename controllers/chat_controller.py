from flask import request, jsonify
from services.chat_service import ChatService
from services.whatsapp_service import WhatsAppService


class ChatController:
    def __init__(self):
        """Initialize chat controller with service"""
        self.chat_service = ChatService()
        self.whatsapp_service = WhatsAppService()

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
            phone, user_msg = self.whatsapp_service.parse_webhook_message(data)

            if not phone or not user_msg:
                return jsonify({"status": "no_message"}), 200

            print(f"User message: {user_msg}")

            # Process the message using our new method
            response_text = self.chat_service.process_message(phone, user_msg)
            print(f"Response: {response_text}")

            # Send the response back to the user
            success, result = self.whatsapp_service.send_message(phone, response_text)

            if success:
                return jsonify({"status": "success"}), 200
            else:
                print(f"Failed to send message: {result}")
                return jsonify({"status": "error", "message": result}), 200

        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 200  # Return 200 to acknowledge receipt
