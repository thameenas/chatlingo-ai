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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "..", "prompts", filename)
        logger.debug(f"[LLM] Loading prompt from: {prompt_path}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            logger.info(f"[LLM] ✅ Loaded prompt '{filename}' ({len(content)} chars)")
            return content
    except Exception as e:
        logger.error(f"[LLM] ❌ Failed to load prompt {filename}: {str(e)}")
        return ""

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
            base_system_prompt = load_prompt("base_system.txt")
            messages = [{"role": "system", "content": base_system_prompt}]
            messages.extend(history)
            logger.info(f"[LLM-OpenAI] Sending {len(messages)} messages to API...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            logger.info(f"[LLM-OpenAI] ✅ Chat response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"[LLM-OpenAI] ❌ API Error: {str(e)}")
            import traceback
            logger.error(f"[LLM-OpenAI] ❌ Traceback:\n{traceback.format_exc()}")
            return "Ayyo! Something went wrong with my brain. Please try again later, maadi."

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        logger.info(f"[LLM-OpenAI] get_practice_scenario_response: {len(history)} history, scenario='{scenario.get('title')}'")
        try:
            practice_scenario_prompt = load_prompt("practice_scenarios_system.txt")
            system_prompt = practice_scenario_prompt.format(
                scenario_title=scenario.get('title', 'General Chat'),
                bot_persona=scenario.get('bot_persona', 'Local Bangalorean'),
                situation_seed=scenario.get('situation_seed', 'Casual conversation')
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            logger.info(f"[LLM-OpenAI] Sending {len(messages)} messages to API...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            logger.info(f"[LLM-OpenAI] ✅ Scenario response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"[LLM-OpenAI] ❌ Practice Scenario Error: {str(e)}")
            import traceback
            logger.error(f"[LLM-OpenAI] ❌ Traceback:\n{traceback.format_exc()}")
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
            base_system_prompt = load_prompt("base_system.txt")
            messages = [{"role": "system", "content": base_system_prompt}]
            messages.extend(history)
            logger.info(f"[LLM-OpenRouter] Sending {len(messages)} messages to API...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            return result
            
        except Exception as e:
            logger.error(f"[LLM-OpenRouter] ❌ API Error: {str(e)}")
            import traceback
            logger.error(f"[LLM-OpenRouter] ❌ Traceback:\n{traceback.format_exc()}")
            return "Ayyo! Something went wrong with my brain. Please try again later."

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        logger.info(f"[LLM-OpenRouter] get_practice_scenario_response: {len(history)} history, scenario='{scenario.get('title')}'")
        try:
            practice_scenario_prompt = load_prompt("practice_scenarios_system.txt")
            system_prompt = practice_scenario_prompt.format(
                scenario_title=scenario.get('title', 'General Chat'),
                bot_persona=scenario.get('bot_persona', 'Local Bangalorean'),
                situation_seed=scenario.get('situation_seed', 'Casual conversation')
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            logger.info(f"[LLM-OpenRouter] Sending {len(messages)} messages to API...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            logger.info(f"[LLM-OpenRouter] ✅ Scenario response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"[LLM-OpenRouter] ❌ Error: {str(e)}")
            import traceback
            logger.error(f"[LLM-OpenRouter] ❌ Traceback:\n{traceback.format_exc()}")
            return "Swalpa technical issue ide. Let's continue in a bit!"

class LLMService:
    """Main service wrapper that delegates to the configured provider"""
    
    def __init__(self):
        self.provider: BaseLLMService = self._initialize_provider()
        logger.info(f"[LLM] ✅ LLM Service initialized with provider: {settings.llm_provider}, model: {settings.llm_model}")

    def _initialize_provider(self) -> BaseLLMService:
        if settings.llm_provider == "openrouter":
            if not settings.openrouter_api_key:
                logger.warning("[LLM] ⚠️ OpenRouter provider selected but no API key found. Falling back to OpenAI.")
                return OpenAIService()
            logger.info(f"[LLM] Using OpenRouter with model: {settings.llm_model}")
            return OpenRouterService()
        else:
            logger.info("[LLM] Using OpenAI")
            return OpenAIService()
    
    async def get_chat_response(self, history: List[Dict[str, str]]) -> str:
        logger.info(f"[LLM] Delegating get_chat_response to provider")
        return await self.provider.get_chat_response(history)

    async def get_practice_scenario_response(self, history: List[Dict[str, str]], scenario: Dict[str, Any]) -> str:
        logger.info(f"[LLM] Delegating get_practice_scenario_response to provider")
        return await self.provider.get_practice_scenario_response(history, scenario)

# Global instance
llm_service = LLMService()