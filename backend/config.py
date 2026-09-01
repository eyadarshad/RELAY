import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "RELAY - Autonomous Operations Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Server Binding
    HOST: str = os.getenv("HOST", "0.0.0.0").strip()
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS & Deployment
    FRONTEND_URL: Optional[str] = (os.getenv("FRONTEND_URL") or "http://localhost:3000").strip()
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # CALL-E API Configuration
    CALLE_API_KEY: Optional[str] = (os.getenv("CALLE_API_KEY") or "").strip()
    CALLE_API_URL: str = (os.getenv("CALLE_API_URL") or "https://api.heycall-e.com/v1").strip()
    
    # LLM Settings (supports Gemini, OpenAI, or smart local rule-engine fallback)
    GEMINI_API_KEY: Optional[str] = (os.getenv("GEMINI_API_KEY") or "").strip()
    OPENAI_API_KEY: Optional[str] = (os.getenv("OPENAI_API_KEY") or "").strip()
    
    # Database
    DATABASE_URL: str = (os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///./relay.db").strip()
    
    # Approval Thresholds (USD) - Halts workflow before final binding order if total exceeds threshold
    APPROVAL_LOW_THRESHOLD: float = 500.0
    APPROVAL_HIGH_THRESHOLD: float = 5000.0
    
    # Safety Limits
    MAX_CALLS_PER_MISSION: int = 15
    CALL_TIMEOUT_SECONDS: int = 120
    
    # Safe Sandbox Default: Runs in zero-side-effect synthetic fixture preview mode by default.
    # Live outbound telephony execution requires explicit opt-in: FORCE_SIMULATION=false with a valid CALLE_API_KEY.
    FORCE_SIMULATION: bool = os.getenv("FORCE_SIMULATION", "true").lower().strip() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
