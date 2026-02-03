import asyncio
from backend.services.speech_service import text_to_speech

async def test_tts():
    text = "नमस्ते दुनिया"  # Hello World in Hindi
    language = "hi"
    
    print(f"Testing TTS for: {text} ({language})")
    result = await text_to_speech(text, language)
    
    if result.get("success"):
        print("Success!")
        print(f"Audio URL: {result['audio_url']}")
        print(f"Word Timings: {len(result['word_timings'])} words")
        print(result['word_timings'])
    else:
        print("Failed!")
        print(result.get("error"))

if __name__ == "__main__":
    asyncio.run(test_tts())
