from flask import Flask
from dotenv import load_dotenv
import os
from repositories.database import init_db
from controllers.chat_controller import ChatController
from scheduler import NudgeScheduler

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database
init_db()

# Initialize controllers
chat_controller = ChatController()

# Routes
@app.route("/whatsapp-webhook", methods=["GET"])
def verify_webhook():
    """WhatsApp webhook verification endpoint"""
    return chat_controller.verify_whatsapp_webhook()

@app.route("/whatsapp-webhook", methods=["POST"])
def whatsapp_webhook():
    """WhatsApp webhook endpoint"""
    return chat_controller.handle_whatsapp_webhook()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
