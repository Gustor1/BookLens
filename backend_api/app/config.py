import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Try loading from backend_api/.env first
load_dotenv()

# Also load from app_build/.env as fallback
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_ENV = os.path.join(BASE_DIR, "app_build", ".env")
if os.path.exists(APP_BUILD_ENV):
    load_dotenv(APP_BUILD_ENV)

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # API Keys
    NVIDIA_API_KEY: str = ""
    HF_API_KEY: str = ""
    TMDB_API_KEY: str = ""
    RAWG_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
