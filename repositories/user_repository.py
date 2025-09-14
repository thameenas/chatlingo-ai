from models.user import User
from .database import get_session
from utils.utils import hash_phone
from datetime import datetime

class UserRepository:
    def __init__(self):
        self.session_factory = get_session
        
    def get_user_by_phone(self, phone: str):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            user = session.query(User).filter(User.phone_hash == phone_hash).first()
            return user
        finally:
            session.close()
            
    def create_user(self, phone: str, current_scenario_id: int = 1):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            user = User(
                phone_hash=phone_hash,
                current_scenario_id=str(current_scenario_id),
                last_active_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            return user
        finally:
            session.close()
            
    def update_user_scenario(self, phone: str, scenario_id: int):
        phone_hash = hash_phone(phone)
        session = self.session_factory()
        try:
            user = session.query(User).filter(User.phone_hash == phone_hash).first()
            if user:
                user.current_scenario_id = str(scenario_id)
                user.last_active_at = datetime.utcnow()
                session.commit()
            return user
        finally:
            session.close()
