from repositories.user_repository import UserRepository
from repositories.chat_repository import ChatRepository
from services.llm_service import LLMService
from services.whatsapp_service import WhatsAppService
import os
from datetime import datetime
import re

class ChatService:
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()
        self.whatsapp_service = WhatsAppService()