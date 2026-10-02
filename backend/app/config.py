import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseModel):
    PROJECT_NAME: str = "MahaSeva AI"
    TAGLINE: str = "One Digital Gateway for Maharashtra Government Services"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Directories
    DATA_DIR: Path = BASE_DIR / "data"
    DB_DIR: Path = BASE_DIR / "db"
    
    # Environment & CORS
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Optional LLM API Keys
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)
    
    # Translation Provider Settings
    TRANSLATION_PROVIDER: str = os.getenv("TRANSLATION_PROVIDER", "google")
    TRANSLATION_API_KEY: str | None = os.getenv("TRANSLATION_API_KEY", None)
    TRANSLATION_PROJECT_ID: str | None = os.getenv("TRANSLATION_PROJECT_ID", None)
    TRANSLATION_LOCATION: str = os.getenv("TRANSLATION_LOCATION", "global")
    
    # RTS Act info
    RTS_ACT_NAME: str = "Maharashtra Right to Public Services Act, 2015"
    RTS_PORTAL_URL: str = "https://aaplesarkar.mahaonline.gov.in"

settings = Settings()
