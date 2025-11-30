"""
Database Pydantic models for Chatlingo AI

These models represent the structure of data stored in Supabase tables.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserSchema(BaseModel):
    """User model - represents a WhatsApp user"""
    phone_number: str
    current_mode: str = Field(default='menu')
    current_scenario_id: Optional[int] = None
    current_session_id: Optional[str] = None
    joined_at: Optional[datetime] = None


class ScenarioSchema(BaseModel):
    """Roleplay scenario model"""
    id: int
    title: str
    bot_persona: str
    situation_seed: str
    opening_line: str


class ChatMessageSchema(BaseModel):
    """Chat message model - represents a single message in conversation"""
    phone_number: str
    role: str  # 'user' or 'bot'
    mode: str   # e.g., 'menu', 'roleplay'
    scenario_id: Optional[int] = None
    session_id: Optional[str] = None
    content: str
    created_at: datetime


class UserProgressSchema(BaseModel):
    """User progress tracking for scenarios"""
    phone_number: str
    scenario_id: int
    status: str  # e.g., 'in_progress', 'completed'
    completed_at: Optional[datetime] = None