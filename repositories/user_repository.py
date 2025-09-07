from sqlalchemy.orm import sessionmaker
from models.user import User
from .database import get_session
from utils.utils import hash_phone

class UserRepository:
    def __init__(self):
        self.session_factory = get_session
