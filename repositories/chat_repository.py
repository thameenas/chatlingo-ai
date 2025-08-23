from models.chat import ChatHistory
from .database import get_session
from utils.utils import hash_phone

class ChatRepository:
    def __init__(self):
        self.session_factory = get_session
    
    def get_chat_history(self, phone: str) -> list:
        """Get chat history for a user"""
        db = self.session_factory()
        try:
            phone_hash = hash_phone(phone)
            
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
            phone_hash = hash_phone(phone)
            
            chat = ChatHistory(phone=phone_hash, role=role, message=message)
            db.add(chat)
            db.commit()
        finally:
            db.close()
