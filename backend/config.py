import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "RELAY - Autonomous Operations Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Server Binding
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS & Deployment
    FRONTEND_URL: Optional[str] = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # CALL-E API Configuration
    CALLE_API_KEY: Optional[str] = os.getenv("CALLE_API_KEY", "")
    CALLE_API_URL: str = os.getenv("CALLE_API_URL", "https://api.heycall-e.com/v1")
    
    # LLM Settings (supports Gemini, OpenAI, or smart local rule-engine fallback)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./relay.db")
    
    # Approval Thresholds (USD)
    APPROVAL_LOW_THRESHOLD: float = 500.0
    APPROVAL_HIGH_THRESHOLD: float = 5000.0
    
    # Safety Limits
    MAX_CALLS_PER_MISSION: int = 15
    CALL_TIMEOUT_SECONDS: int = 120
    
    # Simulation / Offline Testing Mode when CALL-E API key is not yet set or sandbox mode is toggled
    # Note: If CALLE_API_KEY is provided and FORCE_SIMULATION is False, REAL phone calls are dispatched.
    FORCE_SIMULATION: bool = os.getenv("FORCE_SIMULATION", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
