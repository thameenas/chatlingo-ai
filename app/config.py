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
    whatsapp_access_token: str
    whatsapp_phone_id: str
    whatsapp_verify_token: str
    
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


# Global settings instance
settings = Settings()