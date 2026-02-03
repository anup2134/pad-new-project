import asyncio
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.speech_service import text_to_speech

async def main():
    print("Testing text_to_speech service...")
    try:
        # Test 1: English
        print("\nTest 1: English")
        res = await text_to_speech("Hello world", "en", 1.0)
        print(f"Result: {res}")
        
        # Test 2: Hindi (since user had issues)
        print("\nTest 2: Hindi")
        res = await text_to_speech("नमस्ते दुनिया", "hi", 1.0)
        print(f"Result: {res}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
