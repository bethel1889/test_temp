import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Determine the environment and load the appropriate .env file
# In a real production scenario, you would not have a .env file.
# Environment variables would be set by your deployment environment (e.g., Docker, K8s).
env_file = ".env"

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database Configuration
    # The DSN (Data Source Name) for connecting to the PostgreSQL database.
    # Pydantic's PostgresDsn type validates the URL format.
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # LiveKit API Configuration
    # These are read by the LiveKit SDK automatically, but we define them here
    # for explicit configuration and validation.
    LIVEKIT_URL: str = Field(..., env="LIVEKIT_URL")
    LIVEKIT_API_KEY: str = Field(..., env="LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET: str = Field(..., env="LIVEKIT_API_SECRET")

    # Application Secret Key
    # Used for signing tokens or other security-related functions.
    APP_SECRET_KEY: str = Field(..., env="APP_SECRET_KEY")

    # Model configuration
    # Tells Pydantic to load settings from the specified .env file.
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

# Create a single, reusable instance of the settings
settings = Settings()