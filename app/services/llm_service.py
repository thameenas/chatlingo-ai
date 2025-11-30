"""
LLM Service for Chatlingo AI

Handles interactions with LLM providers (OpenAI, OpenRouter) using a strategy pattern.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

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
PRACTICE_SCENARIO_SYSTEM_PROMPT = load_prompt("practice_scenarios_system.txt")

class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        pass

class OpenAIService(BaseLLMService):
    """Standard OpenAI implementation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini" # Default for OpenAI

    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        try:
            messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
            messages.extend(history)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            return "Ayyo! Something went wrong with my brain. Please try again later, maadi."

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        try:
            system_prompt = PRACTICE_SCENARIO_SYSTEM_PROMPT.format(
                scenario_title=scenario.get('title', 'General Chat'),
                bot_persona=scenario.get('bot_persona', 'Local Bangalorean'),
                situation_seed=scenario.get('situation_seed', 'Casual conversation')
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI Practice Scenario Error: {str(e)}")
            return "Swalpa technical issue ide. Let's continue in a bit!"

class OpenRouterService(BaseLLMService):
    """OpenRouter implementation with custom headers and model routing"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.llm_model

    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        try:
            messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT}]
            messages.extend(history)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter API Error: {str(e)}")
            return "Ayyo! Something went wrong with my brain. Please try again later."

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        try:
            system_prompt = PRACTICE_SCENARIO_SYSTEM_PROMPT.format(
                scenario_title=scenario.get('title', 'General Chat'),
                bot_persona=scenario.get('bot_persona', 'Local Bangalorean'),
                situation_seed=scenario.get('situation_seed', 'Casual conversation')
            )
            
            messages = [{"role": "assistant", "content": system_prompt}]
            messages.extend(history)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter Error: {str(e)}")
            return "Swalpa technical issue ide. Let's continue in a bit!"

class LLMService:
    """Main service wrapper that delegates to the configured provider"""
    
    def __init__(self):
        self.provider: BaseLLMService = self._initialize_provider()
        logger.info(f"LLM Service initialized with provider: {settings.llm_provider}")

    def _initialize_provider(self) -> BaseLLMService:
        if settings.llm_provider == "openrouter":
            if not settings.openrouter_api_key:
                logger.warning("OpenRouter provider selected but no API key found. Falling back to OpenAI.")
                return OpenAIService()
            return OpenRouterService()
        else:
            return OpenAIService()
    
    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        return await self.provider.get_chat_response(history)

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        return await self.provider.get_practice_scenario_response(history, scenario)

# Global instance
llm_service = LLMService()