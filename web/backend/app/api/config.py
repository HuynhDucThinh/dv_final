from fastapi import APIRouter
from app.config import (
    GOOGLE_API_KEY,
    HUGGINGFACE_API_KEY,
    GROQ_API_KEY,
    OPENAI_API_KEY
)

router = APIRouter()

@router.get("/providers")
async def get_configured_providers():
    return {
        "google": bool(GOOGLE_API_KEY.strip()),
        "huggingface": bool(HUGGINGFACE_API_KEY.strip()),
        "groq": bool(GROQ_API_KEY.strip()),
        "openai": bool(OPENAI_API_KEY.strip()),
        "ollama": True  # Local models do not require API keys
    }
