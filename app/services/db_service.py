"""
Database service for Chatlingo AI using Supabase

Handles all database operations without ORM, using Supabase Python client.
Returns Pydantic models from app.schemas.
"""

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

# Initialize Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def get_or_create_user(phone: str) -> UserSchema:
    """
    Get user by phone number, or create if doesn't exist.
    
    Args:
        phone: User's phone number
        
    Returns:
        UserSchema object
    """
    # Try to get existing user
    response = supabase.table('users').select('*').eq('phone_number', phone).execute()
    
    if response.data and len(response.data) > 0:
        # User exists, return it
        return UserSchema(**response.data[0])
    
    # User doesn't exist, create new one
    new_user = {
        'phone_number': phone,
        'current_mode': 'menu',
        'joined_at': datetime.utcnow().isoformat()
    }
    
    response = supabase.table('users').insert(new_user).execute()
    
    return UserSchema(**response.data[0])


def update_user_mode(phone: str, mode: str, scenario_id: Optional[int] = None) -> None:
    """
    Update user's current mode and optionally scenario_id.
    
    Args:
        phone: User's phone number
        mode: New mode ('menu', 'chat', 'roleplay', 'translate')
        scenario_id: Optional scenario ID for roleplay mode
    """
    update_data = {
        'current_mode': mode,
        'current_scenario_id': scenario_id
    }
    
    supabase.table('users').update(update_data).eq('phone_number', phone).execute()


def add_message(phone: str, role: str, content: str, mode: str = "menu") -> None:
    """
    Add a message to chat history.
    
    Args:
        phone: User's phone number
        role: Message role ('user' or 'bot')
        content: Message content
        mode: Current mode of the user
    """
    message_data = {
        'phone_number': phone,
        'role': role,
        'content': content,
        'mode': mode,
        'created_at': datetime.utcnow().isoformat()
    }
    
    supabase.table('chat_history').insert(message_data).execute()


def get_recent_messages(phone: str, limit: int = 10) -> List[ChatMessageSchema]:
    """
    Get recent messages for a user in chronological order (oldest to newest).
    
    Args:
        phone: User's phone number
        limit: Maximum number of messages to retrieve (default: 10)
        
    Returns:
        List of ChatMessageSchema in chronological order (oldest first)
    """
    # Fetch messages ordered by created_at DESC (newest first)
    response = supabase.table('chat_history')\
        .select('phone_number, role, mode, scenario_id, content, created_at')\
        .eq('phone_number', phone)\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute()
    
    # Handle empty result
    if not response.data:
        return []
    
    # Convert to Pydantic models
    messages = [ChatMessageSchema(**msg) for msg in response.data]
    
    # Reverse to get chronological order (oldest to newest)
    messages.reverse()
    
    return messages


def get_all_scenarios() -> List[ScenarioSchema]:
    """
    Get all available roleplay scenarios.
    
    Returns:
        List of ScenarioSchema objects
    """
    response = supabase.table('scenarios').select('*').execute()
    
    # Handle empty result
    if not response.data:
        return []
    
    return [ScenarioSchema(**scenario) for scenario in response.data]


def get_scenario_by_id(scenario_id: int) -> Optional[ScenarioSchema]:
    """
    Get a specific scenario by ID.
    
    Args:
        scenario_id: Scenario ID
        
    Returns:
        ScenarioSchema object or None if not found
    """
    response = supabase.table('scenarios').select('*').eq('id', scenario_id).execute()
    
    if not response.data or len(response.data) == 0:
        return None
    
    return ScenarioSchema(**response.data[0])


def mark_scenario_complete(phone: str, scenario_id: int) -> None:
    """
    Mark a scenario as completed for a user (upsert into user_progress).
    
    Args:
        phone: User's phone number
        scenario_id: Scenario ID that was completed
    """
    progress_data = {
        'phone_number': phone,
        'scenario_id': scenario_id,
        'status': 'completed',
        'completed_at': datetime.utcnow().isoformat()
    }
    
    # Upsert: insert if doesn't exist, update if exists
    supabase.table('user_progress').upsert(progress_data).execute()