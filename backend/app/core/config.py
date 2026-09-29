import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "GRASK AI: Bureau of Indian Standards & National Conformity Intelligence (SIH26107)"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Gemini AI
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-3.8-flash", env="GEMINI_MODEL")
    EMBEDDING_MODEL: str = Field(default="models/text-embedding-004", env="EMBEDDING_MODEL")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, "data", "chroma_db")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "data", "uploads")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "data", "reports")
    TELEMETRY_DB_PATH: str = os.path.join(BASE_DIR, "data", "telemetry.db")
    
    # Security
    ADMIN_API_KEY: str = "bis-admin-secret-key-2026"
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        extra = "allow"


settings = Settings()

# Ensure required directories exist
for path in [settings.DATA_DIR, settings.CHROMA_PERSIST_DIR, settings.UPLOAD_DIR, settings.REPORTS_DIR]:
    os.makedirs(path, exist_ok=True)
