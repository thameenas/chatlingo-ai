from typing import List, Dict, Optional, Any

class ChatHistoryDTO:
    """
    Data Transfer Object for ChatHistory model
    Contains the same fields as the ChatHistory model but without SQLAlchemy dependencies
    """
    
    def __init__(
        self,
        phone_hash: str,
        messages: List[Dict[str, Any]] = None,
        summary: Optional[Dict[str, Any]] = None
    ):
        self.phone_hash = phone_hash
        self.messages = messages or []
        self.summary = summary
    
    @classmethod
    def from_model(cls, chat_history_model):
        """
        Create a ChatHistoryDTO from a ChatHistory model instance
        """
        if chat_history_model is None:
            return None
            
        return cls(
            phone_hash=chat_history_model.phone_hash,
            messages=chat_history_model.messages,
            summary=chat_history_model.summary
        )
    
    def to_dict(self):
        """
        Convert the DTO to a dictionary
        """
        return {
            "phone_hash": self.phone_hash,
            "messages": self.messages,
            "summary": self.summary
        }