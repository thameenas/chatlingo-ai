from datetime import datetime
from typing import Optional

class UserDTO:
    """
    Data Transfer Object for User model
    Contains the same fields as the User model but without SQLAlchemy dependencies
    """
    
    def __init__(
        self,
        phone_hash: str,
        current_scenario_id: Optional[str] = None,
        last_active_at: datetime = None
    ):
        self.phone_hash = phone_hash
        self.current_scenario_id = current_scenario_id
        self.last_active_at = last_active_at or datetime.utcnow()
    
    @classmethod
    def from_model(cls, user_model):
        """
        Create a UserDTO from a User model instance
        """
        if user_model is None:
            return None
            
        return cls(
            phone_hash=user_model.phone_hash,
            current_scenario_id=user_model.current_scenario_id,
            last_active_at=user_model.last_active_at
        )
    
    def to_dict(self):
        """
        Convert the DTO to a dictionary
        """
        return {
            "phone_hash": self.phone_hash,
            "current_scenario_id": self.current_scenario_id,
            "last_active_at": self.last_active_at
        }