from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers import documents, speech, profile, chat
from config import AUDIO_DIR

app = FastAPI(
    title="DyslexiFlow API",
    description="AI-powered accessibility platform for people with dyslexia",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio directory for serving TTS files
if os.path.exists(AUDIO_DIR):
    app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# Include routers
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(speech.router, prefix="/api/speech", tags=["Speech"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to AccessaAI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
