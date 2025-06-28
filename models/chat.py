from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow) 