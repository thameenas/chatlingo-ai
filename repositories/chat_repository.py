from models.chat import ChatHistory
from .database import get_session
from utils.utils import hash_phone

class ChatRepository:
    def __init__(self):
        self.session_factory = get_session
        
    def get_chat_history(self, phone: str):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            chat_history = session.query(ChatHistory).filter(
                ChatHistory.phone_hash == phone_hash
            ).first()
            return chat_history
        finally:
            session.close()
            
    def create_chat_history(self, phone: str):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            chat_history = ChatHistory(
                phone_hash=phone_hash,
                messages=[]
            )
            session.add(chat_history)
            session.commit()
            return chat_history
        finally:
            session.close()
            
    def add_message(self, phone: str, role: str, content: str):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            chat_history = session.query(ChatHistory).filter(
                ChatHistory.phone_hash == phone_hash
            ).first()
            
            if not chat_history:
                chat_history = ChatHistory(
                    phone_hash=phone_hash,
                    messages=[]
                )
                session.add(chat_history)
            
            # Add the new message to the messages array
            message = {"role": role, "content": content}
            
            if chat_history.messages is None:
                chat_history.messages = []
                
            # Append the new message to the existing messages
            messages = chat_history.messages
            messages.append(message)
            chat_history.messages = messages
            
            session.commit()
            return chat_history
        finally:
            session.close()
