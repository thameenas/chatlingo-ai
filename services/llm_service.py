import google.generativeai as genai
import os
import json
import re

class LLMService:
    def __init__(self):
        """Initialize LLM service with Gemini model"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        self.prompt_template = ""
        self.scenarios = []
        self._load_resources()
    
    def _load_resources(self):
        """Load scenarios and prompt template"""
        # Load 30-day scenarios
        with open("scenarios.json", "r", encoding="utf-8") as f:
            self.scenarios = json.load(f)
        
        # Load prompt template
        with open("prompt_template.txt", "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            print(f"Prompt message: {self.prompt_template}")
    
    def build_prompt(self, day_number):
        """Build prompt for a specific day"""
        if 1 <= day_number <= 30:
            scenario_title = self.scenarios[day_number - 1]
            return self.prompt_template.format(day_number=day_number, scenario_title=scenario_title)
        return None
    
    def process_message(self, user_msg, chat_history):
        """Process user message with LLM"""
        chat_session = self.model.start_chat(history=chat_history)
        response = chat_session.send_message(user_msg)
        return response.text
    
    def parse_day_command(self, user_msg):
        """Parse day command from user message"""
        user_msg = user_msg.strip().lower()
        
        if user_msg == "start":
            return 1
        elif match := re.match(r"(?i)^day\s*(\d+)$", user_msg):
            return int(match.group(1))
        else:
            return None 