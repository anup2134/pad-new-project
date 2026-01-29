import edge_tts
import asyncio

async def test():
    text = "The quick brown fox jumps over the lazy dog. Accessibility is important for everyone."
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    found_boundary = False
    async for chunk in communicate.stream():
        if chunk['type'] == "WordBoundary":
            found_boundary = True
            print(f"Found WordBoundary at {chunk['offset']}: {chunk['text']}")
        elif chunk['type'] != "audio":
            print(f"Chunk type: {chunk['type']}")
    
    if not found_boundary:
        print("No WordBoundary events found!")

if __name__ == "__main__":
    asyncio.run(test())
