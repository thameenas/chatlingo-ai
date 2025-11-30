"""
LLM Service for Chatlingo AI

Handles interactions with OpenAI for generating conversational responses.
"""

import logging
import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

def load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory"""
    try:
        # Construct absolute path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", filename)
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to load prompt {filename}: {str(e)}")
        return ""

# Load prompts at module level
BASE_SYSTEM_PROMPT = load_prompt("base_system.txt")
ROLEPLAY_SYSTEM_PROMPT = load_prompt("roleplay_system.txt")

class LLMService:
    """Service for generating AI responses"""
    
    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        """
        Generate a response for general chat/menu mode.
        
        Args:
            history: List of message dicts [{'role': 'user', 'content': '...'}, ...]
            
        Returns:
            Generated response string
        """
        try:
            messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
            messages.extend(history)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            return "Ayyo! Something went wrong with my brain. Please try again later, maadi."

    async def get_roleplay_response(
        self, 
        history: List[Dict[str, str]], 
        scenario: Dict[str, Any]
    ) -> str:
        """
        Generate a response for roleplay mode.
        
        Args:
            history: List of message dicts
            scenario: Scenario details (title, persona, situation)
            
        Returns:
            Generated response string
        """
        try:
            # Format the specific system prompt for this scenario
            system_prompt = ROLEPLAY_SYSTEM_PROMPT.format(
                scenario_title=scenario.get('title', 'General Chat'),
                bot_persona=scenario.get('bot_persona', 'Local Bangalorean'),
                situation_seed=scenario.get('situation_seed', 'Casual conversation')
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8, # Slightly higher creativity for roleplay
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI Roleplay Error: {str(e)}")
            return "Swalpa technical issue ide. Let's continue in a bit!"

# Global instance
llm_service = LLMService()