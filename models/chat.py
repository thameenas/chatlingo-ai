from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from models.base import Base

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    phone_hash = Column(String, ForeignKey('users.phone_hash'), primary_key=True)
    messages = Column(JSONB, nullable=False, default=list)
    summary = Column(JSONB, nullable=True)