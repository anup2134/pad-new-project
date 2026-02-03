import asyncio
import edge_tts
import os

async def test_minimal_tts():
    text = "Hello, this is a test."
    voice = "en-US-AriaNeural"
    rate = "+0%"
    output_file = "test_audio.mp3"

    print(f"Testing edge-tts with voice={voice}, rate={rate}")
    
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        # Simple save
        await communicate.save(output_file)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"Success! File created: {output_file}, Size: {os.path.getsize(output_file)} bytes")
        else:
            print("Failure: File not created or empty.")

        # Test streaming (which is what the service uses)
        print("Testing streaming...")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                print(f"Received audio chunk: {len(chunk['data'])} bytes")
                break # Just need to know we got something
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_minimal_tts())
