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
    
    def build_prompt(self, day_number, is_new_user=False, is_returning_user=False):
        """Build prompt for a specific day with optional welcome message"""
        if 1 <= day_number <= 30:
            scenario_title = self.scenarios[day_number - 1]
            base_prompt = self.prompt_template.format(day_number=day_number, scenario_title=scenario_title)
            
            # For new users, add welcome message to the system prompt
            if is_new_user:
                welcome_prefix = """
Before starting the lesson, warmly welcome the user to their 30-day Kannada learning journey.
Explain that each day focuses on a real-life scenario in Karnataka and that you'll teach them
practical phrases they can use right away. Encourage them to reply naturally and assure them
that you'll guide them step by step.

"""
                return welcome_prefix + base_prompt
            
            # For returning users who are continuing, add a reminder
            elif is_returning_user:
                returning_prefix = f"""
Welcome the user back to their Kannada learning journey. Remind them that they're currently on
Day {day_number}: {scenario_title}. Express enthusiasm about continuing their learning journey.

"""
                return returning_prefix + base_prompt
            
            # Regular prompt for ongoing conversations
            else:
                return base_prompt
        return None
    
    def process_message(self, user_msg, chat_history, is_new_user=False, is_returning_user=False):
        """Process user message with LLM"""
        # If this is a day prompt (not a regular message)
        if "Day " in user_msg and "scenario" in user_msg:
            # Extract day number from the prompt
            day_match = re.search(r"Day (\d+)", user_msg)
            if day_match:
                day_number = int(day_match.group(1))
                # Rebuild the prompt with appropriate welcome/returning message
                user_msg = self.build_prompt(day_number, is_new_user, is_returning_user)
        
        # Process with LLM
        chat_session = self.model.start_chat(history=chat_history)
        response = chat_session.send_message(user_msg)
        return response.text
    
    def parse_day_command(self, user_msg):
        """Parse day command from user message"""
        user_msg = user_msg.strip().lower()
        if match := re.match(r"(?i)^day\s*(\d+)$", user_msg):
            return int(match.group(1))
        else:
            return None