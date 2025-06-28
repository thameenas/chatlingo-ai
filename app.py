from collections import defaultdict
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re
from models import init_db, get_last_day_number, set_last_day_number, get_chat_history, add_chat_message, clear_chat_history
from twilio.rest import Client
from datetime import datetime
from scheduler import NudgeScheduler

# Load environment variables
load_dotenv()

app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
prompt_template = ""

# Initialize Twilio client for sending nudges
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize database
init_db()

# Initialize nudge scheduler
nudge_scheduler = None

# 📚 Load 30-day scenarios
with open("scenarios.json", "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# 📝 Load prompt template
with open("prompt_template.txt", "r", encoding="utf-8") as f:
    prompt_template = f.read()
    print(f"Prompt message: {prompt_template}")

def build_prompt(day_number):
    if 1 <= day_number <= 30:
        scenario_title = scenarios[day_number - 1]
        return prompt_template.format(day_number=day_number, scenario_title=scenario_title)
    return None

def initialize_scheduler():
    """Initialize and start the nudge scheduler"""
    global nudge_scheduler
    nudge_scheduler = NudgeScheduler(twilio_client, twilio_phone_number, build_prompt)
    nudge_scheduler.start_scheduler()

def process_user_message(user_msg, session_id):
    user_msg = user_msg.strip().lower()
    phone = session_id
    match = re.match(r"(?i)^day\s*(\d+)$", user_msg)
    if user_msg.lower() == "start":
        day_number = 1
        set_last_day_number(phone, day_number)
        prompt = build_prompt(day_number)
    elif match:
        day_number = int(match.group(1))
        set_last_day_number(phone, day_number)
        prompt = build_prompt(day_number)
    else:
        prompt = user_msg
    chat_session = model.start_chat(history=get_chat_history(phone))
    response = chat_session.send_message(prompt)
    add_chat_message(phone, 'user', prompt)
    add_chat_message(phone, 'model', response.text)
    return response.text

@app.route("/webhook", methods=["POST"])
def whatsapp_reply():
    user_msg = request.form.get("Body", "").strip().lower()
    phone = request.form.get("From", "").replace("whatsapp:", "")
    print(f"User message: {user_msg}")
    try:
        response_text = process_user_message(user_msg, phone)
        print(f"Response: {response_text}")
        twilio_resp = MessagingResponse()
        twilio_resp.message(response_text)
        return str(twilio_resp)
    except Exception as e:
        print(e)
        return f"⚠️ Error: {str(e)}", 200

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("user_msg", "")
    session_id = data.get("session_id", "")
    if not user_msg or not session_id:
        return jsonify({"error": "Missing user_msg or session_id"}), 400
    try:
        response = process_user_message(user_msg, session_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json()
    session_id = data.get("session_id", "")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
    try:
        clear_chat_history(session_id)
        return jsonify({"response": "Chat history cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/nudges/send", methods=["POST"])
def manual_send_nudges():
    """Manually trigger daily nudges for testing"""
    try:
        if nudge_scheduler:
            nudge_scheduler.send_daily_nudges()
            return jsonify({"response": "Daily nudges sent successfully"})
        else:
            return jsonify({"error": "Scheduler not initialized"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    # Initialize the scheduler when the app starts
    initialize_scheduler()
    
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
