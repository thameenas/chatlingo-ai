from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    phone = Column(String, primary_key=True)  # This will be the hashed phone
    original_phone = Column(String, nullable=False)  # Store original phone for WhatsApp
    day_number = Column(Integer, nullable=False)
    is_new_user = Column(Boolean, default=True)  # Track if user is new