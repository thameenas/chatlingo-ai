from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    phone_hash = Column(String, primary_key=True)
    current_scenario_id = Column(String, nullable=True)
    last_active_at = Column(DateTime, default=datetime.utcnow)
