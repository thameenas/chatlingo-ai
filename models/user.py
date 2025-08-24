from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    hashed_phone = Column(String, primary_key=True)  
    original_phone = Column(String, nullable=False)  # Store original phone for WhatsApp
    day_number = Column(Integer, nullable=False)