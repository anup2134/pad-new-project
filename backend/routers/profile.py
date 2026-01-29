from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory storage for demo (use database in production)
user_profile = {
    "dyslexia_type": "visual",
    "font_family": "OpenDyslexic",
    "font_size": 18,
    "background_color": "#FDF6E3",
    "text_color": "#333333",
    "speech_speed": 1.0,
    "language": "en"
}

class ProfileUpdate(BaseModel):
    dyslexia_type: Optional[str] = None  # visual, auditory, mixed
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    speech_speed: Optional[float] = None
    language: Optional[str] = None

@router.get("/")
async def get_profile():
    """Get current user profile settings"""
    return user_profile

@router.post("/")
async def update_profile(profile: ProfileUpdate):
    """Update user profile settings"""
    if profile.dyslexia_type:
        user_profile["dyslexia_type"] = profile.dyslexia_type
    if profile.font_family:
        user_profile["font_family"] = profile.font_family
    if profile.font_size:
        user_profile["font_size"] = profile.font_size
    if profile.background_color:
        user_profile["background_color"] = profile.background_color
    if profile.text_color:
        user_profile["text_color"] = profile.text_color
    if profile.speech_speed:
        user_profile["speech_speed"] = profile.speech_speed
    if profile.language:
        user_profile["language"] = profile.language
    
    return {"message": "Profile updated", "profile": user_profile}
