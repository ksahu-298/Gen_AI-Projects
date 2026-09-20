from fastapi import APIRouter
from app.config import settings
from app.db.session import get_db_type

router = APIRouter()


@router.get("/health", summary="System Health & Diagnostics")
def health_check():
    """Returns status, active environment, database engine, and LLM configuration."""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database_type": get_db_type(),
        "llm_provider": settings.LLM_PROVIDER,
        "gemini_model": settings.GEMINI_MODEL,
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY)
    }
