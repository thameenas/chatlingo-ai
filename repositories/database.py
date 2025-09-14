from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models.base import Base
from dotenv import load_dotenv

load_dotenv()

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
    # Create all tables from all models at once
    # Since we're using a single Base, SQLAlchemy will handle the correct order
    # based on foreign key dependencies
    Base.metadata.create_all(bind=engine)