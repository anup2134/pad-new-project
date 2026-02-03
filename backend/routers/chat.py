from fastapi import APIRouter, Form
from pydantic import BaseModel
import uuid

from services.chat_service import answer_question, simplify_text, store_document_context, clear_document_context

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    session_id: str
    language: str = "en"
    dyslexia_type: str = "general"

class SimplifyTextRequest(BaseModel):
    text: str
    language: str = "en"
    dyslexia_type: str = "general"

class DocumentContextRequest(BaseModel):
    document_text: str
    session_id: str

@router.post("/simplify")
async def simplify_user_text(request: SimplifyTextRequest):
    """Simplify text for dyslexic users"""
    result = await simplify_text(
        text=request.text,
        dyslexia_type=request.dyslexia_type,
        language=request.language
    )
    return result

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about an uploaded document"""
    result = await answer_question(
        question=request.question,
        session_id=request.session_id,
        dyslexia_type=request.dyslexia_type,
        language=request.language
    )
    return result

@router.post("/set-context")
async def set_document_context(request: DocumentContextRequest):
    """Store document context for a chat session"""
    store_document_context(request.session_id, request.document_text)
    return {
        "message": "Document context stored successfully",
        "session_id": request.session_id,
        "success": True
    }

@router.delete("/clear-context/{session_id}")
async def clear_chat_context(session_id: str):
    """Clear document context for a session"""
    clear_document_context(session_id)
    return {
        "message": "Document context cleared",
        "session_id": session_id,
        "success": True
    }

@router.get("/new-session")
async def create_new_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())[:8]
    return {
        "session_id": session_id,
        "message": "New session created",
        "success": True
    }
