import json
import os

import google.generativeai as genai


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

    def generate_response(self, user_message, history=None, summary=None):
        """
        Generate a response from the LLM using the system prompt, user message, chat history,
        and an optional summary of previous interactions
        
        Args:
            user_message (str): The message from the user
            history (list, optional): List of previous messages in the format
                                     [{"role": "user|model", "parts": ["message"]}]
            summary (str, optional): A summary of previous user-model interactions or user's
                                    learning progress to provide additional context
            
        Returns:
            str: The LLM's response
        """
        try:
            # Set up the generation config
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }

            # Set up the safety settings
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]

            # Initialize content with system prompt
            content = [{"role": "system", "parts": [self.prompt_template]}]

            # Add summary as a system message if provided
            if summary and isinstance(summary, str):
                content.append({
                    "role": "system",
                    "parts": [f"Summary of previous interactions: {summary}"]
                })

            # Add chat history if provided
            if history and isinstance(history, list):
                # Validate and add history messages
                for message in history:
                    if (isinstance(message, dict) and
                            "role" in message and
                            "parts" in message and
                            message["role"] in ["user", "model"]):
                        content.append(message)

            # Add the current user message
            content.append({"role": "user", "parts": [user_message]})

            # Generate response
            response = self.model.generate_content(
                content,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Return the text response
            return response.text

        except Exception as e:
            print(f"Error generating response: {e}")
            # Return a fallback message
            return "Sorry, I'm having trouble responding right now. Please try again later."
