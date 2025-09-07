from models.chat import ChatHistory
from .database import get_session
from utils.utils import hash_phone

class ChatRepository:
    def __init__(self):
        self.session_factory = get_session
