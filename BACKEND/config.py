import os
from typing import Optional

class Settings:
    """Application settings loaded from environment variables"""
    
    # LLM API Configuration
    LLM_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", "your-openrouter-api-key")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Application Configuration
    APP_NAME: str = "AI Resume Assistant API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Session Configuration
    SESSION_TIMEOUT_HOURS: int = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings"""
        if cls.LLM_API_KEY == "your-openrouter-api-key":
            print("Warning: LLM_API_KEY not set. Please set the environment variable.")
        
        if not cls.LLM_API_URL:
            raise ValueError("LLM_API_URL is required")

# Create settings instance
settings = Settings() 