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

# Initialize nudge scheduler
nudge_scheduler = None

def initialize_scheduler():
    """Initialize and start the nudge scheduler"""
    global nudge_scheduler
    nudge_scheduler = NudgeScheduler()
    nudge_scheduler.start_scheduler()

# Routes
@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    """WhatsApp webhook endpoint"""
    return chat_controller.handle_whatsapp_webhook()

@app.route("/api/chat", methods=["POST"])
def chat():
    """Web chat interface endpoint"""
    return chat_controller.handle_web_chat()

@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset chat history endpoint"""
    return chat_controller.handle_reset_chat()

@app.route("/api/nudges/send", methods=["POST"])
def manual_send_nudges():
    """Manual nudge trigger endpoint"""
    return chat_controller.handle_manual_nudge()

@app.route("/")
def index():
    """Serve web interface"""
    return app.send_static_file('index.html')

if __name__ == "__main__":
    # Initialize the scheduler when the app starts
    initialize_scheduler()
    
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
