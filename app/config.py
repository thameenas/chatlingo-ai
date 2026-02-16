"""
Configuration management for Chatlingo AI

Loads environment variables and provides typed configuration objects.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str | None = None

    # OpenRouter Configuration
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # LLM Configuration
    llm_provider: Literal["openai", "openrouter"] = "openrouter"
    llm_model: str = "anthropic/claude-3.5-sonnet"
    
    
    
    # WhatsApp Cloud API Configuration
    whatsapp_access_token: str | None = None
    whatsapp_phone_id: str | None = None
    whatsapp_verify_token: str | None = None
    
    # Telegram Bot Configuration
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    telegram_allowed_user_ids: str | None = None  # Comma-separated list of allowed Telegram user IDs
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    
    # Application Configuration
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_allowed_telegram_user_ids(self) -> set[int]:
        """Parse and return set of allowed Telegram user IDs"""
        if not self.telegram_allowed_user_ids:
            return set()
        
        try:
            # Parse comma-separated string to set of integers
            return {int(uid.strip()) for uid in self.telegram_allowed_user_ids.split(',') if uid.strip()}
        except ValueError:
            # Log warning and return empty set if parsing fails
            import logging
            logging.warning("Invalid TELEGRAM_ALLOWED_USER_IDS format. Expected comma-separated integers.")
            return set()


# Global settings instance
settings = Settings()