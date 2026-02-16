"""
Pydantic models for Telegram Bot API webhook payloads.

Reference: https://core.telegram.org/bots/api#update
"""

from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    """Telegram user object"""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class Chat(BaseModel):
    """Telegram chat object"""
    id: int
    type: str  # 'private', 'group', 'supergroup', 'channel'
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class InlineKeyboardButton(BaseModel):
    """Inline keyboard button"""
    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None


class CallbackQuery(BaseModel):
    """Callback query from inline keyboard button press"""
    id: str
    from_: User = Field(alias="from")
    message: Optional["Message"] = None
    data: Optional[str] = None
    chat_instance: str


class Message(BaseModel):
    """Telegram message object"""
    message_id: int
    from_: Optional[User] = Field(None, alias="from")
    chat: Chat
    date: int
    text: Optional[str] = None
    reply_markup: Optional[dict] = None


class TelegramUpdate(BaseModel):
    """
    Telegram webhook update object.
    
    Contains either a message or a callback_query.
    """
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
