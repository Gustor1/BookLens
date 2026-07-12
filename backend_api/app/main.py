import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, media, recommendations, assistant

# Ensure app_build path is present
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

app = FastAPI(
    title="MediaLens V2 API Wrapper",
    description="FastAPI wrapper exposing BookLens and MediaLens services.",
    version="2.0.0"
)

# CORS configurations
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(media.router)
app.include_router(recommendations.router)
app.include_router(assistant.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to MediaLens V2 API Wrapper. Access /docs for API documentation.",
        "docs": "/docs"
    }
