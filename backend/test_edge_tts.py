import asyncio
import edge_tts

async def test_tts():
    text = "Hello world."
    voice = "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    print(f"Testing TTS with voice: {voice}")
    
    async for chunk in communicate.stream():
        print(f"Chunk Type: {chunk['type']}")
        if chunk["type"] == "WordBoundary":
            print(f"Word: {chunk['text']}")

if __name__ == "__main__":
    asyncio.run(test_tts())
