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