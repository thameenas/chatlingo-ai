from sqlalchemy.orm import sessionmaker
from models.user import User
from .database import get_session
from utils.utils import hash_phone

class UserRepository:
    def __init__(self):
        self.session_factory = get_session
    
    def get_user(self, phone: str):
        """Get user by phone number"""
        db = self.session_factory()
        try:
            phone_hash = hash_phone(phone)
            return db.query(User).filter(User.hashed_phone == phone_hash).first()
        finally:
            db.close()
    
    def get_last_day_number(self, phone: str) -> int:
        """Get the last day number for a user"""
        user = self.get_user(phone)
        return user.day_number if user else 1  # Default to day 1 for new users
    
    def set_last_day_number(self, phone: str, day_number: int):
        """Set the last day number for a user"""
        db = self.session_factory()
        try:
            phone_hash = hash_phone(phone)
            user = db.query(User).filter(User.hashed_phone == phone_hash).first()
            if user:
                user.day_number = day_number
                db.commit()
            else:
                # Create new user record
                record = User(
                    phone=phone_hash,
                    original_phone=phone,
                    day_number=day_number
                )
                db.add(record)
                db.commit()
        finally:
            db.close()

    def create_user(self, phone: str, day_number: int):
        """Set the last day number for a user"""
        db = self.session_factory()
        try:
            phone_hash = hash_phone(phone)
            record = User(
                    hashed_phone=phone_hash,
                    original_phone=phone,
                    day_number=day_number
                )
            db.add(record)
            db.commit()
        finally:
            db.close()
    
    def get_all_users(self):
        """Get all users for nudge sending"""
        db = self.session_factory()
        try:
            return db.query(User).all()
        finally:
            db.close()