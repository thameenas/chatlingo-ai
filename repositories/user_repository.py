from sqlalchemy.orm import sessionmaker
from models.user import LastDayNumber
import hashlib
from .database import get_session

class UserRepository:
    def __init__(self):
        self.session_factory = get_session
    
    def hash_phone(self, phone: str) -> str:
        """Hash phone number for security"""
        return hashlib.sha256(phone.encode('utf-8')).hexdigest()
    
    def get_last_day_number(self, phone: str) -> int:
        """Get the last day number for a user"""
        db = self.session_factory()
        try:
            phone_hash = self.hash_phone(phone)
            result = db.query(LastDayNumber).filter(LastDayNumber.phone == phone_hash).first()
            return result.day_number if result else None
        finally:
            db.close()
    
    def set_last_day_number(self, phone: str, day_number: int):
        """Set the last day number for a user"""
        db = self.session_factory()
        try:
            phone_hash = self.hash_phone(phone)
            record = LastDayNumber(phone=phone_hash, original_phone=phone, day_number=day_number)
            db.merge(record)  # merge will update if exists, insert if not
            db.commit()
        finally:
            db.close()
    
    def get_all_users(self):
        """Get all users for nudge sending"""
        db = self.session_factory()
        try:
            return db.query(LastDayNumber).all()
        finally:
            db.close() 