from fastapi import APIRouter
from pydantic import BaseModel

from services.speech_service import text_to_speech, get_available_languages

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    speed: float = 1.0

@router.post("/tts")
async def generate_speech(request: TTSRequest):
    """Convert text to speech with word timing data"""
    result = await text_to_speech(
        text=request.text,
        language=request.language,
        speed=request.speed
    )
    return result

@router.get("/languages")
async def list_languages():
    """Get list of supported languages"""
    return {"languages": get_available_languages()}
