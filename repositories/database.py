from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models.user import Base as UserBase
from models.chat import Base as ChatBase

def get_database_url():
    """Get database URL from environment variable"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    else:
        raise RuntimeError('DATABASE_URL environment variable is not set. Please set it to your PostgreSQL connection string.')

# Create engine and session
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Get database session"""
    return SessionLocal()

def init_db():
    """Initialize database tables"""
    # Create all tables from both models
    UserBase.metadata.create_all(bind=engine)
    ChatBase.metadata.create_all(bind=engine) 