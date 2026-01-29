from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Store document context per session (in production, use database or Redis)
document_context = {}

def store_document_context(session_id: str, document_text: str):
    """Store document text for a session"""
    document_context[session_id] = document_text

def get_document_context(session_id: str) -> str:
    """Retrieve stored document text for a session"""
    return document_context.get(session_id, "")

def clear_document_context(session_id: str):
    """Clear stored document for a session"""
    if session_id in document_context:
        del document_context[session_id]

def _get_qa_prompt(question: str, document_text: str, dyslexia_type: str, lang_name: str) -> str:
    """Generate dyslexia-type-specific Q&A prompts"""
    
    qa_instructions = {
        "phonological": """Answer the question using simple, phonetically regular words. Avoid silent letters and homophones. Keep the answer clear and easy to read aloud.""",
        "surface": """Answer using short, common words with regular spelling patterns. Use words that look visually distinct. Make each word clear and recognizable by shape.""",
        "visual": """Answer in very short sentences (max 8 words each). Use generous white space. One idea per sentence. Use simple words only.""",
        "auditory": """Answer using words with distinct, clear sounds. Avoid rhyming or similar-sounding words. Use numbered lists for sequences.""",
        "mixed": """Answer using the simplest words and structures. Very short sentences (max 8 words). One concept per sentence. Maximum clarity.""",
        "general": """Answer clearly and simply using common words. Keep sentences short (under 15 words). Use active voice."""
    }
    
    instruction = qa_instructions.get(dyslexia_type, qa_instructions["general"])
    
    prompt = f"""You are a helpful assistant answering questions about a document for someone with dyslexia.

DOCUMENT CONTEXT:
{document_text}

USER QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY based on the document provided above.
2. If the answer is not in the document, say: "I cannot find this information in the document."
3. {instruction}
4. Keep your answer short and focused.
5. Use plain text only - no special formatting.
6. Use active voice only.
7. Avoid jargon and complex terms.
8. If the question needs multiple points, use numbered lists (1, 2, 3).
9. Respond in {lang_name} only.

ANSWER:"""
    
    return prompt

async def answer_question(question: str, session_id: str, dyslexia_type: str = "general", language: str = "en") -> dict:
    """Answer a question based on uploaded document context"""
    
    if not client:
        return {
            "error": "Groq API key not configured.",
            "success": False
        }
    
    # Retrieve document context
    document_text = get_document_context(session_id)
    
    if not document_text:
        return {
            "error": "No document uploaded for this session. Please upload a document first.",
            "success": False
        }
    
    if not question.strip():
        return {
            "error": "Please enter a question.",
            "success": False
        }
    
    language_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "hi": "Hindi", "ar": "Arabic",
        "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ru": "Russian"
    }
    lang_name = language_names.get(language, "English")
    
    # Generate type-specific prompt
    prompt = _get_qa_prompt(question, document_text, dyslexia_type, lang_name)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content.strip()
        
        return {
            "question": question,
            "answer": answer,
            "success": True
        }
    except Exception as e:
        return {
            "error": f"Error processing question: {str(e)}",
            "success": False
        }
