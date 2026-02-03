import edge_tts
import uuid
import os
import asyncio
from config import AUDIO_DIR

# Language mappings for Edge TTS
LANGUAGE_MAP = {
    "en": {"code": "en", "description": "English (US)", "voice": "en-US-AriaNeural"},
    "en-GB": {"code": "en", "description": "English (British)", "voice": "en-GB-SoniaNeural"},
    "es": {"code": "es", "description": "Spanish (Spain)", "voice": "es-ES-ElviraNeural"},
    "es-MX": {"code": "es", "description": "Spanish (Mexico)", "voice": "es-MX-DaliaNeural"},
    "fr": {"code": "fr", "description": "French", "voice": "fr-FR-DeniseNeural"},
    "de": {"code": "de", "description": "German", "voice": "de-DE-KatjaNeural"},
    "it": {"code": "it", "description": "Italian", "voice": "it-IT-ElsaNeural"},
    "pt": {"code": "pt", "description": "Portuguese (Brazil)", "voice": "pt-BR-FranciscaNeural"},
    "pt-PT": {"code": "pt-PT", "description": "Portuguese (Portugal)", "voice": "pt-PT-RaquelNeural"},
    "hi": {"code": "hi", "description": "Hindi", "voice": "hi-IN-SwaraNeural"},
    "ar": {"code": "ar", "description": "Arabic", "voice": "ar-SA-ZariyahNeural"},
    "zh": {"code": "zh-CN", "description": "Chinese (Simplified)", "voice": "zh-CN-XiaoxiaoNeural"},
    "zh-TW": {"code": "zh-TW", "description": "Chinese (Traditional)", "voice": "zh-TW-HsiaoChenNeural"},
    "ja": {"code": "ja", "description": "Japanese", "voice": "ja-JP-NanamiNeural"},
    "ko": {"code": "ko", "description": "Korean", "voice": "ko-KR-SunHiNeural"},
    "ru": {"code": "ru", "description": "Russian", "voice": "ru-RU-SvetlanaNeural"}
}

async def text_to_speech(text: str, language: str = "en", speed: float = 1.0) -> dict:
    """
    Convert text to speech using Edge TTS with accurate timing.
    
    Args:
        text: Text to convert to speech
        language: Language code
        speed: Speech speed (0.5 to 2.0)
    
    Returns:
        Dictionary with audio URL and word timing data
    """
    
    # Get language config or default to English
    lang_config = LANGUAGE_MAP.get(language, LANGUAGE_MAP["en"])
    voice = lang_config.get("voice", "en-US-AriaNeural")
    lang_code = lang_config["code"]
    
    # Validate text
    if not text or not text.strip():
        return {
            "error": "Please provide text to convert",
            "success": False
        }
    
    # Generate unique filename
    audio_id = str(uuid.uuid4())[:8]
    audio_filename = f"{audio_id}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    try:
        # Calculate rate string (e.g. "+50%", "-20%")
        # map 0.5-2.0 to -50% to +100% (approx)
        rate_percent = int((speed - 1.0) * 100)
        rate_str = f"{'+' if rate_percent >= 0 else ''}{rate_percent}%"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        
        word_timings = []
        
        # Open file to write audio
        with open(audio_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start_ms = chunk["offset"] / 10000
                    duration_ms = chunk["duration"] / 10000
                    word_timings.append({
                        "word": chunk["text"],
                        "start_ms": start_ms,
                        "duration_ms": duration_ms,
                        "end_ms": start_ms + duration_ms
                    })

        # Verify file
        if not (os.path.exists(audio_path) and os.path.getsize(audio_path) > 0):
             return {
                "error": "Generated audio file is empty",
                "success": False
            }
            
        # FALLBACK: Elastic Alignment if no word timings
        if not word_timings:
            print("! No accurate timing from Edge TTS. Applying Elastic Alignment.")
            try:
                from mutagen.mp3 import MP3
                audio = MP3(audio_path)
                total_duration_ms = audio.info.length * 1000
                print(f"  - Exact Audio Duration: {total_duration_ms:.2f}ms")
            except Exception as e:
                print(f"  ! Failed to get duration with mutagen: {e}")
                total_duration_ms = 0
            
            words = text.split()
            if words and total_duration_ms > 0:
                # Calculate total character length for weighting
                total_chars = sum(len(w) for w in words)
                # Add "virtual chars" for pauses between words (e.g. 1 char equivalent)
                total_weight = total_chars + (len(words) - 1) * 2  # spacing weight
                
                # Calculate duration per weight unit
                ms_per_unit = total_duration_ms / max(1, total_weight)
                
                current_time = 0
                for i, word in enumerate(words):
                    # Weight: length of word
                    weight = len(word)
                    word_duration = weight * ms_per_unit
                    
                    # Ensure minimum duration for visibility (50ms)
                    # But suppress if we are over budget? No, elastic fits exactly.
                    # Just basic elastic distribution:
                    
                    word_timings.append({
                        "word": word,
                        "start_ms": current_time,
                        "duration_ms": word_duration,
                        "end_ms": current_time + word_duration
                    })
                    
                    current_time += word_duration
                    
                    # Add gap to start time for next word (spacing)
                    if i < len(words) - 1:
                         current_time += (2 * ms_per_unit)
                         
                # Adjust final end_ms to match total exactly (fix floating point drift)
                if word_timings:
                    word_timings[-1]["end_ms"] = total_duration_ms

            elif words:
                 # Fallback to pure estimation if mutagen failed
                 print("  ! Using pure estimation fallback.")
                 avg_word = 400 / speed
                 curr = 0
                 for w in words:
                     dur = avg_word * (len(w)/5.0)
                     word_timings.append({"word":w, "start_ms":curr, "duration_ms":dur, "end_ms":curr+dur})
                     curr += dur + 50
        
        print(f"✓ TTS generated: {audio_id}.mp3 ({len(word_timings)} words with timing)")
        
        return {
            "audio_url": f"/audio/{audio_filename}",
            "audio_id": audio_id,
            "word_timings": word_timings,
            "language": language,
            "lang_code": lang_code,
            "total_words": len(word_timings),
            "success": True
        }
        
    except Exception as e:
        # Clean up on failure
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
        
        print(f"✗ TTS Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "error": f"TTS Error: {str(e)}",
            "success": False
        }

async def simplify_text(text: str, dyslexia_type: str = "general", language: str = "en") -> dict:
    """Simplify text for dyslexic users"""
    if not text.strip():
        return {
            "error": "Please provide text to simplify.",
            "success": False
        }
    
    return {
        "error": "Text simplification endpoint - requires Groq API",
        "success": False
    }

def get_available_languages():
    """Return list of supported languages with descriptions"""
    languages = []
    for code, config in LANGUAGE_MAP.items():
        languages.append({
            "code": code,
            "name": config["description"],
            "lang_code": config["code"]
        })
    return sorted(languages, key=lambda x: x["code"])
