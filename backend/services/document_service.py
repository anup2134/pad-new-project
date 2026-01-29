import pdfplumber
from docx import Document
import os

def extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"
    return text.strip()

def extract_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n\n"
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"
    return text.strip()

def extract_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def extract_text(file_path: str) -> str:
    """Extract text from any supported file type"""
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.pdf':
        return extract_from_pdf(file_path)
    elif ext == '.docx':
        return extract_from_docx(file_path)
    elif ext == '.txt':
        return extract_from_txt(file_path)
    else:
        return f"Unsupported file type: {ext}"
