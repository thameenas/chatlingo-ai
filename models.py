from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import hashlib

# Create base class for declarative models
Base = declarative_base()

class LastDayNumber(Base):
    __tablename__ = 'last_day_number'
    
    phone = Column(String, primary_key=True)
    day_number = Column(Integer, nullable=False)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    phone = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database URL configuration
def get_database_url():
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    else:
        raise RuntimeError('DATABASE_URL environment variable is not set. Please set it to your PostgreSQL connection string.')

# Create engine and session
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Utility function to hash phone numbers
def hash_phone(phone: str) -> str:
    return hashlib.sha256(phone.encode('utf-8')).hexdigest()

# Database operations
def get_last_day_number(phone: str) -> int:
    db = SessionLocal()
    try:
        phone_hash = hash_phone(phone)
        result = db.query(LastDayNumber).filter(LastDayNumber.phone == phone_hash).first()
        return result.day_number if result else None
    finally:
        db.close()

def set_last_day_number(phone: str, day_number: int):
    db = SessionLocal()
    try:
        phone_hash = hash_phone(phone)
        record = LastDayNumber(phone=phone_hash, day_number=day_number)
        db.merge(record)  # merge will update if exists, insert if not
        db.commit()
    finally:
        db.close()

def get_chat_history(phone: str) -> list:
    db = SessionLocal()
    try:
        phone_hash = hash_phone(phone)
        history = db.query(ChatHistory)\
            .filter(ChatHistory.phone == phone_hash)\
            .order_by(ChatHistory.timestamp.asc())\
            .all()
        return [{'role': msg.role, 'parts': msg.message} for msg in history]
    finally:
        db.close()

def add_chat_message(phone: str, role: str, message: str):
    db = SessionLocal()
    try:
        phone_hash = hash_phone(phone)
        chat = ChatHistory(phone=phone_hash, role=role, message=message)
        db.add(chat)
        db.commit()
    finally:
        db.close()

def clear_chat_history(phone: str):
    db = SessionLocal()
    try:
        phone_hash = hash_phone(phone)
        db.query(ChatHistory).filter(ChatHistory.phone == phone_hash).delete()
        db.commit()
    finally:
        db.close() 