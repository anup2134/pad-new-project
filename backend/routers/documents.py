from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
import os
import uuid

from services.document_service import extract_text
from services.groq_service import simplify_text, summarize_text, get_dyslexia_types
from config import UPLOAD_DIR

router = APIRouter()

class TextRequest(BaseModel):
    text: str
    language: str = "en"
    dyslexia_type: str = "general"

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document and extract text"""
    # Validate file type
    allowed_types = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename.lower())[1]
    
    if file_ext not in allowed_types:
        return {"error": f"Unsupported file type. Allowed: {', '.join(allowed_types)}"}
    
    # Save file temporarily
    file_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text
        extracted_text = extract_text(file_path)
        
        # Clean up file
        os.remove(file_path)
        
        return {
            "filename": file.filename,
            "text": extracted_text,
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}

@router.post("/simplify")
async def simplify_document(request: TextRequest):
    """Simplify text for easier reading based on dyslexia type"""
    simplified = await simplify_text(request.text, request.language, request.dyslexia_type)
    return {
        "original_length": len(request.text),
        "simplified_text": simplified,
        "dyslexia_type": request.dyslexia_type,
        "success": True
    }

@router.post("/summarize")
async def summarize_document(request: TextRequest):
    """Summarize text into key points based on dyslexia type"""
    summary = await summarize_text(request.text, request.language, request.dyslexia_type)
    return {
        "original_length": len(request.text),
        "summary": summary,
        "dyslexia_type": request.dyslexia_type,
        "success": True
    }

@router.get("/dyslexia-types")
async def list_dyslexia_types():
    """Get list of supported dyslexia types"""
    return {"types": get_dyslexia_types()}

