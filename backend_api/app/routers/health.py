from fastapi import APIRouter
from app.schemas.media import PublicConfigResponse
from app.config import settings

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "recommender_model": "active",
            "llm_provider": "active" if settings.NVIDIA_API_KEY else "inactive"
        }
    }

@router.get("/config/public", response_model=PublicConfigResponse)
def get_public_config():
    return PublicConfigResponse(
        status="healthy",
        version="2.0.0",
        providers={
            "nvidia": bool(settings.NVIDIA_API_KEY),
            "huggingface": bool(settings.HF_API_KEY)
        }
    )
