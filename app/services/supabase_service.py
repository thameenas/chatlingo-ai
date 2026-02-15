"""
Database service for Chatlingo AI using Supabase

Handles all database operations without ORM, using Supabase Python client.
Returns Pydantic models from app.schemas.
"""

import logging
import traceback
from supabase import create_client, Client
from typing import List, Optional
from datetime import datetime

from app.config import settings
from app.schemas import (
    UserSchema,
    ScenarioSchema,
    ChatMessageSchema,
    UserProgressSchema
)

logger = logging.getLogger(__name__)

# Initialize Supabase client
logger.info("[SUPABASE] Initializing Supabase client...")
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
logger.info("[SUPABASE] ✅ Supabase client initialized")


def get_or_create_user(phone: str) -> UserSchema:
    """Get user by phone number, or create if doesn't exist."""
    logger.info(f"[SUPABASE] get_or_create_user: phone={phone}")
    try:
        # Try to get existing user
        response = supabase.table('users').select('*').eq('phone_number', phone).execute()
        
        if response.data and len(response.data) > 0:
            user = UserSchema(**response.data[0])
            logger.info(f"[SUPABASE] Found existing user: mode={user.current_mode}, scenario_id={user.current_scenario_id}")
            return user
        
        # User doesn't exist, create new one
        logger.info(f"[SUPABASE] Creating new user: phone={phone}")
        new_user = {
            'phone_number': phone,
            'current_mode': 'menu',
            'joined_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.table('users').insert(new_user).execute()
        user = UserSchema(**response.data[0])
        return user
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in get_or_create_user: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def update_user_mode(phone: str, mode: str, scenario_id: Optional[int] = None, session_id: Optional[str] = None) -> None:
    """
    Update user's current mode and optionally scenario_id and session_id.
    
    Args:
        phone: User's phone number
        mode: New mode ('menu', 'chat', 'roleplay', 'translate')
        scenario_id: Optional scenario ID for roleplay mode
        session_id: Optional session UUID for tracking conversation context
    """
    logger.info(f"[SUPABASE] update_user_mode: phone={phone}, mode={mode}, scenario_id={scenario_id}, session_id={session_id}")
    try:
        update_data = {
            'current_mode': mode,
            'current_scenario_id': scenario_id
        }
        
        if session_id:
            update_data['current_session_id'] = session_id
            
        supabase.table('users').update(update_data).eq('phone_number', phone).execute()
        logger.info(f"[SUPABASE] ✅ User mode updated")
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in update_user_mode: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def add_message(phone: str, role: str, content: str, mode: str = "menu", session_id: Optional[str] = None, scenario_id: Optional[int] = None) -> None:
    """Add a message to chat history."""
    try:
        message_data = {
            'phone_number': phone,
            'role': role,
            'content': content,
            'mode': mode,
            'session_id': session_id,
            'scenario_id': scenario_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('chat_history').insert(message_data).execute()
        logger.info(f"[SUPABASE] ✅ Message saved to chat_history")
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in add_message: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def get_recent_messages(phone: str, limit: int = 10, session_id: Optional[str] = None) -> List[ChatMessageSchema]:
    """Get recent messages for a user in chronological order (oldest to newest)."""
    try:
        # Build query
        query = supabase.table('chat_history')\
            .select('phone_number, role, mode, scenario_id, content, created_at')\
            .eq('phone_number', phone)
            
        # Filter by session_id if provided
        if session_id:
            query = query.eq('session_id', session_id)
            
        # Execute query
        response = query.order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        # Handle empty result
        if not response.data:
            logger.info(f"[SUPABASE] No messages found")
            return []
        
        # Convert to Pydantic models
        messages = [ChatMessageSchema(**msg) for msg in response.data]
        
        # Reverse to get chronological order (oldest to newest)
        messages.reverse()
        
        logger.info(f"[SUPABASE] ✅ Retrieved {len(messages)} messages")
        return messages
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in get_recent_messages: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def get_all_scenarios() -> List[ScenarioSchema]:
    """Get all available roleplay scenarios."""
    logger.info("[SUPABASE] get_all_scenarios")
    try:
        response = supabase.table('scenarios').select('*').execute()
        
        if not response.data:
            logger.warning("[SUPABASE] ⚠️ No scenarios found in DB")
            return []
        
        scenarios = [ScenarioSchema(**scenario) for scenario in response.data]
        logger.info(f"[SUPABASE] ✅ Retrieved {len(scenarios)} scenarios")
        return scenarios
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in get_all_scenarios: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def get_scenario_by_id(scenario_id: int) -> Optional[ScenarioSchema]:
    """Get a specific scenario by ID."""
    logger.info(f"[SUPABASE] get_scenario_by_id: id={scenario_id}")
    try:
        response = supabase.table('scenarios').select('*').eq('id', scenario_id).execute()
        
        if not response.data or len(response.data) == 0:
            logger.warning(f"[SUPABASE] ⚠️ Scenario {scenario_id} not found")
            return None
        
        scenario = ScenarioSchema(**response.data[0])
        logger.info(f"[SUPABASE] ✅ Found scenario: '{scenario.title}'")
        return scenario
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in get_scenario_by_id: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise


def mark_scenario_complete(phone: str, scenario_id: int) -> None:
    """Mark a scenario as completed for a user."""
    try:
        progress_data = {
            'phone_number': phone,
            'scenario_id': scenario_id,
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        }
        
        supabase.table('user_progress').upsert(progress_data).execute()
        logger.info(f"[SUPABASE] ✅ Scenario {scenario_id} marked complete for {phone}")
    except Exception as e:
        logger.error(f"[SUPABASE] ❌ Error in mark_scenario_complete: {e}")
        logger.error(f"[SUPABASE] ❌ Traceback:\n{traceback.format_exc()}")
        raise