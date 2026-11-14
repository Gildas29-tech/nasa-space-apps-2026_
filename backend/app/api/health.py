from fastapi import APIRouter
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/ready")
async def readiness_check():
    # Check external services connectivity
    checks = {
        "nasa_power": "unknown",
        "supabase": "not_configured" if not settings.SUPABASE_URL else "unknown",
    }
    return {"status": "ready", "checks": checks}