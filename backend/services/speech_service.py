import edge_tts
import asyncio
import uuid
import os
import json
from config import AUDIO_DIR

# Voice mappings for different languages - Using high-quality neural voices
VOICE_MAP = {
    "en": "en-US-AriaNeural",      # Clear, warm female voice
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "hi": "hi-IN-SwaraNeural",
    "ar": "ar-SA-ZariyahNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "ru": "ru-RU-SvetlanaNeural"
}

async def text_to_speech(text: str, language: str = "en", speed: float = 1.0) -> dict:
    """
    Convert text to speech with word timestamps for highlighting.
    Returns audio file path and word timing data.
    """
    voice = VOICE_MAP.get(language, "en-US-AriaNeural")
    
    # Calculate rate adjustment (-50% to +100%)
    rate_percent = int((speed - 1.0) * 100)
    rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
    
    # Generate unique filename
    audio_id = str(uuid.uuid4())[:8]
    audio_filename = f"{audio_id}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    # Word timing data
    word_timings = []
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        
        # Collect word boundaries
        async def process_stream():
            nonlocal word_timings
            with open(audio_path, "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        word_timings.append({
                            "text": chunk["text"],
                            "start": chunk["offset"] / 10000000,  # Convert to seconds
                            "duration": chunk["duration"] / 10000000
                        })
        
        await process_stream()
        
        return {
            "audio_url": f"/audio/{audio_filename}",
            "word_timings": word_timings,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def get_available_languages():
    """Return list of supported languages"""
    return [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "hi", "name": "Hindi"},
        {"code": "ar", "name": "Arabic"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ru", "name": "Russian"}
    ]
