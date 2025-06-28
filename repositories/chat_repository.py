from models.chat import ChatHistory
from .database import get_session

class ChatRepository:
    def __init__(self):
        self.session_factory = get_session
    
    def get_chat_history(self, phone: str) -> list:
        """Get chat history for a user"""
        db = self.session_factory()
        try:
            from repositories.user_repository import UserRepository
            user_repo = UserRepository()
            phone_hash = user_repo.hash_phone(phone)
            
            history = db.query(ChatHistory)\
                .filter(ChatHistory.phone == phone_hash)\
                .order_by(ChatHistory.timestamp.asc())\
                .all()
            return [{'role': msg.role, 'parts': msg.message} for msg in history]
        finally:
            db.close()
    
    def add_chat_message(self, phone: str, role: str, message: str):
        """Add a chat message to the database"""
        db = self.session_factory()
        try:
            from repositories.user_repository import UserRepository
            user_repo = UserRepository()
            phone_hash = user_repo.hash_phone(phone)
            
            chat = ChatHistory(phone=phone_hash, role=role, message=message)
            db.add(chat)
            db.commit()
        finally:
            db.close()
    
    def clear_chat_history(self, phone: str):
        """Clear chat history for a user"""
        db = self.session_factory()
        try:
            from repositories.user_repository import UserRepository
            user_repo = UserRepository()
            phone_hash = user_repo.hash_phone(phone)
            
            db.query(ChatHistory).filter(ChatHistory.phone == phone_hash).delete()
            db.commit()
        finally:
            db.close() 