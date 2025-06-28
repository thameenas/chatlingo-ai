from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LastDayNumber(Base):
    __tablename__ = 'last_day_number'
    
    phone = Column(String, primary_key=True)  # This will be the hashed phone
    original_phone = Column(String, nullable=False)  # Store original phone for WhatsApp
    day_number = Column(Integer, nullable=False) 