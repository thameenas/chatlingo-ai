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
            return db.query(User).filter(User.phone == phone_hash).first()
        finally:
            db.close()
    
    def is_new_user(self, phone: str) -> bool:
        """Check if user is new"""
        user = self.get_user(phone)
        return user.is_new_user if user else True
    
    def mark_user_as_existing(self, phone: str):
        """Mark user as no longer new"""
        db = self.session_factory()
        try:
            phone_hash = hash_phone(phone)
            user = db.query(User).filter(User.phone == phone_hash).first()
            if user:
                user.is_new_user = False
                db.commit()
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
            user = db.query(User).filter(User.phone == phone_hash).first()
            if user:
                user.day_number = day_number
                user.is_new_user = False  # Mark as existing user when day is set
                db.commit()
            else:
                # Create new user record
                record = User(
                    phone=phone_hash,
                    original_phone=phone,
                    day_number=day_number,
                    is_new_user=False  # New user becomes existing after first interaction
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