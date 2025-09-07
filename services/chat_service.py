from repositories.chat_repository import ChatRepository
from repositories.user_repository import UserRepository
from services.llm_service import LLMService


class ChatService:
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()