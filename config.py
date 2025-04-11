import os
from typing import Optional, Dict, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from secure_vault import vault
from utils import logger

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Get credentials from secure vault
    credentials: ClassVar[Dict[str, str]] = vault.get_credentials() or {}
    
    # X (Twitter) API credentials
    X_API_KEY: str = Field(default=credentials.get("X_API_KEY", ""), env="X_API_KEY")
    X_API_SECRET: str = Field(default=credentials.get("X_API_SECRET", ""), env="X_API_SECRET")
    X_ACCESS_TOKEN: str = Field(default=credentials.get("X_ACCESS_TOKEN", ""), env="X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET: str = Field(default=credentials.get("X_ACCESS_TOKEN_SECRET", ""), env="X_ACCESS_TOKEN_SECRET")
    
    # Grok API credentials
    GROK_API_KEY: str = Field(default=credentials.get("GROK_API_KEY", ""), env="GROK_API_KEY")
    
    # Modal API credentials
    MODAL_API_KEY: str = Field(default=credentials.get("MODAL_API_KEY", ""), env="MODAL_API_KEY")
    
    # SerpAPI credentials
    SERPAPI_API_KEY: str = Field(default=credentials.get("SERPAPI_API_KEY", ""), env="SERPAPI_API_KEY")
    
    # MongoDB settings
    MONGODB_URI: str = Field(default="mongodb://localhost:27017", env="MONGODB_URI")
    MONGODB_DB: str = Field(default="social_agent", env="MONGODB_DB")
    
    # Application settings
    MAX_TWEET_LENGTH: int = 280
    MAX_RETRIES: int = 3
    X_RATE_LIMIT_PER_15M: int = 50  # 50 tweets per 15 minutes
    X_RATE_LIMIT_PER_DAY: int = 500  # 500 tweets per day
    X_RATE_LIMIT_PER_MONTH: int = 1000  # 1000 tweets per month
    GROK_RATE_LIMIT: int = 60  # Requests per hour
    X_RATE_LIMIT: int = 50     # Requests per 15-minute window
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 1000
    
    # Monitoring settings
    LOG_LEVEL: str = "INFO"
    METRICS_INTERVAL: int = 300  # 5 minutes
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def validate_settings(self) -> bool:
        """Validate that all required settings are present"""
        required_fields = [
            "X_API_KEY",
            "X_API_SECRET",
            "X_ACCESS_TOKEN",
            "X_ACCESS_TOKEN_SECRET",
            "GROK_API_KEY"
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Missing required configuration: {field}")
        return True

    def save_credentials(self) -> None:
        """Save credentials to secure vault."""
        credentials = {
            "X_API_KEY": self.X_API_KEY,
            "X_API_SECRET": self.X_API_SECRET,
            "X_ACCESS_TOKEN": self.X_ACCESS_TOKEN,
            "X_ACCESS_TOKEN_SECRET": self.X_ACCESS_TOKEN_SECRET,
            "GROK_API_KEY": self.GROK_API_KEY,
            "MODAL_API_KEY": self.MODAL_API_KEY,
            "SERPAPI_API_KEY": self.SERPAPI_API_KEY
        }
        vault.store_credentials(credentials)
        logger.info("Saved credentials to secure vault")

# Create global settings instance
settings = Settings()
# Validate settings on startup
settings.validate_settings()
# Save credentials to secure vault
settings.save_credentials()