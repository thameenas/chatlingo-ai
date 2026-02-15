"""
Conversation Engine for Chatlingo AI

Core conversation logic abstracted from transport layer (WhatsApp/CLI).
Handles LLM interactions and conversation flow.
"""

import logging
import uuid
from typing import List, Optional

from app.schemas.db import ScenarioSchema
from app.services import supabase_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ConversationEngine:
    """
    Core conversation engine - transport agnostic.
    Works with database for persistence, transport handles I/O.
    """
    
    @staticmethod
    def get_all_scenarios() -> List[ScenarioSchema]:
        """Get all available scenarios from database"""
        logger.info("[ENGINE] Fetching all scenarios")
        scenarios = supabase_service.get_all_scenarios()
        logger.info(f"[ENGINE] Found {len(scenarios)} scenarios")
        return scenarios
    
    @staticmethod
    def get_scenario(scenario_id: int) -> Optional[ScenarioSchema]:
        """Get a specific scenario by ID"""
        logger.info(f"[ENGINE] Fetching scenario id={scenario_id}")
        scenario = supabase_service.get_scenario_by_id(scenario_id)
        logger.info(f"[ENGINE] Scenario found: {scenario is not None}")
        return scenario
    
    @staticmethod
    def start_scenario(phone: str, scenario_id: int) -> str:
        """Start a scenario session, returns new session_id"""
        session_id = str(uuid.uuid4())
        logger.info(f"[ENGINE] Starting scenario: phone={phone}, scenario_id={scenario_id}, session_id={session_id}")
        supabase_service.update_user_mode(
            phone,
            "practice_scenario",
            scenario_id=scenario_id,
            session_id=session_id
        )
        return session_id
    
    @staticmethod
    async def generate_opening(
        phone: str,
        scenario: ScenarioSchema,
        session_id: str
    ) -> str:
        """Generate scenario opening line using LLM"""
        response = await llm_service.get_practice_scenario_response(
            [],
            scenario.model_dump()
        )
        supabase_service.add_message(
            phone,
            "assistant",
            response,
            mode="practice_scenario",
            session_id=session_id,
            scenario_id=scenario.id
        )
        
        return response
    
    @staticmethod
    def save_user_message(
        phone: str,
        message: str,
        scenario_id: int,
        session_id: str
    ) -> None:
        """Save user message to database"""
        supabase_service.add_message(
            phone,
            "user",
            message,
            mode="practice_scenario",
            session_id=session_id,
            scenario_id=scenario_id
        )
    
    @staticmethod
    async def process_message(
        phone: str,
        scenario: ScenarioSchema,
        session_id: str
    ) -> str:
        """
        Generate LLM response based on conversation history.
        Assumes user message is already saved to DB.
        """
        # Get conversation history
        history_objs = supabase_service.get_recent_messages(
            phone,
            limit=50,
            session_id=session_id
        )
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_objs
        ]
        # Generate LLM response
        logger.info("[ENGINE] Calling LLM for scenario response...")
        response = await llm_service.get_practice_scenario_response(
            history,
            scenario.model_dump()
        )
        logger.info(f"[ENGINE] LLM response received")
        
        # Save assistant response
        supabase_service.add_message(
            phone,
            "assistant",
            response,
            mode="practice_scenario",
            session_id=session_id,
            scenario_id=scenario.id
        )
        return response


# Global instance
conversation_engine = ConversationEngine()
