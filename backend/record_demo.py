import asyncio
from playwright.async_api import async_playwright
import os

async def record_demo():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=1000) # Open visible browser, slow down for video quality
        
        # Create context with video recording enabled
        context = await browser.new_context(
            record_video_dir="demo_video",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        
        print("Navigating to app...")
        await page.goto("http://localhost:5173")
        # await page.wait_for_load_state("networkidle") # Caused timeout
        await asyncio.sleep(5) # Simple wait
        
        print("Step 1: Introduction")
        await asyncio.sleep(2)
        
        print("Step 2: Switching to Hindi")
        # Assuming settings is opened via a button or is visible
        # Updating based on App.jsx: Settings panel is at the bottom
        await page.select_option("select", value="hi")
        await asyncio.sleep(2)
        
        print("Step 3: Entering Hindi Text")
        hindi_text = "डिस्लेक्सिया एक सीखने की अक्षमता है जो पढ़ने, लिखने और वर्तनी में कठिनाई पैदा करती है। यह बुद्धि से संबंधित नहीं है।"
        
        # Click "Type Text" tab if needed
        await page.click("text=Type Text")
        
        await page.fill("textarea", hindi_text)
        await asyncio.sleep(1)
        
        print("Step 4: Simplification")
        await page.click("text=Simplify Text")
        
        # Wait for simplification to complete (loading spinner to disappear)
        await page.wait_for_selector(".loading", state="detached", timeout=30000)
        await asyncio.sleep(3) # Let user see result
        
        print("Step 5: Text-to-Speech")
        await page.click("text=Read Aloud")
        await asyncio.sleep(10) # Listen to audio
        
        print("Step 6: Chat Q&A")
        # Ask a question
        await page.fill("input[placeholder='Ask a question about the document...']", "डिस्लेक्सिया क्या है?")
        await page.click("text=Ask")
        
        # Wait for answer
        await page.wait_for_selector(".chat-history div", timeout=30000)
        await asyncio.sleep(5)
        
        print("Step 7: Summarization")
        # Reset text first? No, use same text.
        await page.click("text=Summarize")
        await page.wait_for_selector(".loading", state="detached", timeout=30000)
        await asyncio.sleep(3)
        
        print("Finishing up...")
        await context.close()
        await browser.close()
        print("Demo recorded successfully in 'demo_video' directory.")

if __name__ == "__main__":
    asyncio.run(record_demo())
