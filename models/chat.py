from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    phone_hash = Column(String, ForeignKey('users.phone_hash'), primary_key=True)
    messages = Column(JSONB, nullable=False, default=list)
    summary = Column(JSONB, nullable=True)