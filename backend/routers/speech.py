from fastapi import APIRouter
from pydantic import BaseModel

from services.speech_service import text_to_speech, get_available_languages

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    speed: float = 1.0

class HighlightWordRequest(BaseModel):
    """Request for word-level highlighting during TTS playback"""
    text: str
    language: str = "en"
    speed: float = 1.0

@router.post("/tts")
async def generate_speech(request: TTSRequest):
    """
    Convert text to speech with word timing data for highlighting.
    
    Response includes:
    - audio_url: URL to the generated MP3 file
    - word_timings: Array of word timing data with millisecond precision
    - total_words: Number of words in the text
    """
    result = await text_to_speech(
        text=request.text,
        language=request.language,
        speed=request.speed
    )
    return result

@router.post("/tts-with-highlight")
async def generate_speech_with_highlight(request: HighlightWordRequest):
    """
    Convert text to speech and return word-by-word timing data for highlighting.
    
    This endpoint is optimized for:
    - Dyslexic users who benefit from visual word highlighting
    - Word-level synchronization during audio playback
    - Multiple language support with clear pronunciation
    
    Returns:
    - audio_url: URL to MP3 file
    - word_timings: Array of {word, start_ms, duration_ms, end_ms}
    - total_words: Count of words
    """
    result = await text_to_speech(
        text=request.text,
        language=request.language,
        speed=request.speed
    )
    
    if result["success"]:
        return {
            "audio_url": result["audio_url"],
            "audio_id": result["audio_id"],
            "word_timings": result["word_timings"],
            "language": result["language"],
            "total_words": result["total_words"],
            "success": True
        }
    return result

@router.get("/languages")
async def list_languages():
    """
    Get list of supported languages with voice details.
    
    Returns list of available languages for TTS with descriptions
    """
    return {
        "languages": get_available_languages(),
        "total": len(get_available_languages())
    }
