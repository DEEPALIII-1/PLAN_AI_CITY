from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "plan_ai_city.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Plan AI City"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(default="plan-ai-city-super-secret-key-change-in-production-2026", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite:///{DEFAULT_DB_PATH}",
        env="DATABASE_URL"
    )
    USE_POSTGIS: bool = Field(default=False, env="USE_POSTGIS")
    USE_PGVECTOR: bool = Field(default=False, env="USE_PGVECTOR")
    
    # LLM & AI Engine
    LLM_PROVIDER: str = Field(default="GEMINI", env="LLM_PROVIDER")  # GEMINI, OPENAI, GROQ, OLLAMA, MOCK
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    DEFAULT_LLM_MODEL: str = "gemini-1.5-flash"
    
    # Vector Search
    EMBEDDING_DIM: int = 384
    SIMILARITY_THRESHOLD: float = 0.55
    TOP_K_RAG: int = 4
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
