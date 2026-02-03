from groq import AsyncGroq
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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

def _get_simplification_prompt(text: str, dyslexia_type: str, lang_name: str) -> str:
    """Generate dyslexia-type-specific text simplification prompts with grounding and few-shot examples"""
    
    prompts_by_type = {
        "phonological": f"""You are a text simplification expert for people with PHONOLOGICAL DYSLEXIA.

UNDERSTANDING PHONOLOGICAL DYSLEXIA:
- Difficulty with sound patterns and pronunciation
- Struggles with rhyming words and phonetic sounds
- Needs clear, easy-to-pronounce words

SIMPLIFICATION RULES:
1. Focus on CHANGING WORDING to be easier, NOT shortening the text.
2. DO NOT summarize. Keep the same amount of information as the original.
3. One clear concept per sentence. Split complex sentences if needed.
4. Maintain the original semantic meaning and approximate length.
5. Common words only. Active voice only.

EXAMPLES:
❌ "The knight knew the psychology of their fight"
✅ "The fighter understood how to win the contest."

❌ "You should thoroughly through the knowledge"
✅ "Read and learn the information."

ORIGINAL TEXT:
{text}

Now simplify the text for someone with phonological dyslexia. Keep all important information but use clear, easy-to-say words. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
,
        "surface": f"""You are a text simplification expert for people with SURFACE DYSLEXIA.

UNDERSTANDING SURFACE DYSLEXIA:
- Difficulty with irregular spelling patterns
- Struggles to recognize whole words by sight
- Needs clear visual patterns and distinct word shapes

SIMPLIFICATION RULES:
1. Focus on CHANGING WORDING to be easier, NOT shortening the text.
2. DO NOT summarize. Keep the same amount of information as the original.
3. Keep sentence structure simple but complete.
4. Maintain the original semantic meaning and approximate length.
5. Use visually distinct, regular words. Active voice only.

EXAMPLES:
❌ "The foreign bureaucracy was too complex"
✅ "The government system was hard to understand."

❌ "He read about the psychology of behaviour"
✅ "He learned about how people act and think."

ORIGINAL TEXT:
{text}

Now simplify the text for someone with surface dyslexia. Use words with regular spelling patterns and clear shapes. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
,
        "visual": f"""You are a text simplification expert for people with VISUAL DYSLEXIA.

UNDERSTANDING VISUAL DYSLEXIA:
- Difficulty with visual processing and letter/word positioning
- Struggles with crowded text and visual complexity
- Needs maximum spacing and shortest possible sentences

SIMPLIFICATION RULES:
1. Maximum 8 words per sentence (strict limit)
2. Add extra white space between sentences
3. One concept per sentence only
4. Use only simple, common words (under 10 letters)
5. Short paragraphs (max 3 sentences)
6. Active voice only
7. No complex punctuation

FORMAT WITH EXTRA SPACING:

EXAMPLES:
❌ "The comprehensive study demonstrated significant psychological impacts on learning"
✅ "The study showed a big finding.
    Learning was affected.
    People felt worried."

❌ "Unfortunately, the bureaucratic procedures were unnecessarily complicated"
✅ "The system was hard to use.
    Too many rules.
    Simple is better."

ORIGINAL TEXT:
{text}

Now simplify the text for visual dyslexia. Use very short sentences. Add space between them. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
,
        "auditory": f"""You are a text simplification expert for people with AUDITORY DYSLEXIA.

UNDERSTANDING AUDITORY DYSLEXIA:
- Difficulty with sound discrimination
- Struggles with similar-sounding words
- Needs clear, distinct sounds in words

SIMPLIFICATION RULES:
1. Use words with distinct, different sounds
2. Avoid rhyming words (cat/bat, right/light)
3. Avoid similar-sounding words (accept/except, affect/effect)
4. Use numbered lists for sequences (1, 2, 3)
5. Short, clear sentences
6. One action per sentence
7. Active voice only

EXAMPLES:
❌ "Right through the light"
✅ "Move forward in the brightness."

❌ "The affect on behavior was to accept the effect"
✅ "1. The mood changed the person's behavior.
    2. The person agreed with the decision."

ORIGINAL TEXT:
{text}

Now simplify the text for auditory dyslexia. Use distinct-sounding words. Use numbered lists. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
,
        "mixed": f"""You are a text simplification expert for people with MIXED DYSLEXIA.

UNDERSTANDING MIXED DYSLEXIA:
- Combination of phonological, surface, and visual challenges
- Struggles with multiple aspects of reading
- Needs maximum simplicity and clarity

SIMPLIFICATION RULES:
1. Maximum 8 words per sentence
2. Phonetically regular words only
3. Regular spelling patterns only
4. Visually clear structure
5. Extra white space between sentences
6. One concept per sentence
7. Numbered lists for any sequences
8. Active voice only
9. Common words only (under 10 letters)

EXAMPLES:
❌ "The psychology and behaviour studies showed comprehensive analysis"
✅ "1. We studied how people think.
    2. We studied what people do.
    3. We found clear results."

❌ "Unfortunately, there were several significant complications"
✅ "1. There were many problems.
    2. It was hard to fix.
    3. We need more help."

ORIGINAL TEXT:
{text}

Now simplify for mixed dyslexia. Use all the rules above. Maximum clarity. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
,
        "general": f"""You are a text simplification expert for people with dyslexia.

SIMPLIFICATION RULES:
1. Use simple, common words
2. Keep sentences under 15 words
3. One idea per sentence
4. Active voice only
5. Avoid jargon and complex terms
6. Use short paragraphs
7. Numbered lists for sequences

EXAMPLES:
❌ "The comprehensive methodology demonstrated significant psychological implications"
✅ "The study showed important findings about how people think."

ORIGINAL TEXT:
{text}

Now simplify the text clearly and simply. Respond in {lang_name} only.

SIMPLIFIED TEXT:"""
    }
    
    prompt = prompts_by_type.get(dyslexia_type, prompts_by_type["general"])
    return prompt

def _get_qa_prompt(question: str, document_text: str, dyslexia_type: str, lang_name: str) -> str:
    """Generate dyslexia-type-specific Q&A prompts with grounding and few-shot examples"""
    
    qa_prompts_by_type = {
        "phonological": f"""You are a helpful assistant answering questions for people with PHONOLOGICAL DYSLEXIA.

UNDERSTANDING PHONOLOGICAL DYSLEXIA:
- Difficulty with sound patterns and pronunciation
- Struggles with rhyming words and phonetic complexity
- Needs clear, easy-to-pronounce words that sound straightforward

YOUR TASK:
- Answer ONLY based on the document below
- Use phonetically regular words (no silent letters)
- Avoid homophones and rhyming words
- Make the answer easy to read aloud
- One idea per sentence

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Use simple, easy-to-pronounce words
3. Avoid silent letters (know, through, psychology)
4. Avoid homophones (to/two, there/their)
5. One clear idea per sentence
6. Active voice only
7. If not in document: "I cannot find this information in the document."
8. If multiple points, use numbered list (1, 2, 3)
9. Respond in {lang_name} only

ANSWER:"""
,
        "surface": f"""You are a helpful assistant answering questions for people with SURFACE DYSLEXIA.

UNDERSTANDING SURFACE DYSLEXIA:
- Difficulty with irregular spelling patterns
- Struggles to recognize words by sight
- Needs clear, regular spelling patterns and visually distinct words

YOUR TASK:
- Answer ONLY based on the document below
- Use words with regular, predictable spelling
- Make words visually distinct and recognizable
- Keep structure simple and clear

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Use regular spelling patterns (avoid: said, build, though)
3. Use visually distinct words
4. One idea per sentence
5. Short sentences (under 15 words)
6. Active voice only
7. Avoid abbreviations
8. If not in document: "I cannot find this information in the document."
9. If multiple points, use numbered list (1, 2, 3)
10. Respond in {lang_name} only

ANSWER:"""
,
        "visual": f"""You are a helpful assistant answering questions for people with VISUAL DYSLEXIA.

UNDERSTANDING VISUAL DYSLEXIA:
- Difficulty with visual processing and text crowding
- Struggles with complex text layouts
- Needs maximum spacing and short sentences

YOUR TASK:
- Answer ONLY based on the document below
- Use very short sentences (max 8 words each)
- Add space between sentences
- Use only simple words
- One concept per sentence

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Maximum 8 words per sentence (strict)
3. Add blank line between each sentence
4. Simple words only (no words over 10 letters)
5. One idea per sentence
6. No complex punctuation
7. Short paragraphs (max 3 sentences)
8. Active voice only
9. If not in document: "I cannot find this information."
10. If multiple points, use numbered list:
    1. First point.
    2. Second point.
11. Respond in {lang_name} only

ANSWER:"""
,
        "auditory": f"""You are a helpful assistant answering questions for people with AUDITORY DYSLEXIA.

UNDERSTANDING AUDITORY DYSLEXIA:
- Difficulty with sound discrimination
- Struggles with similar-sounding or rhyming words
- Needs words with distinct, clear sounds

YOUR TASK:
- Answer ONLY based on the document below
- Use words with distinct sounds
- Avoid rhyming and similar-sounding words
- Use numbered lists for clarity
- Make each point easy to hear

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Use words with distinct sounds
3. Avoid rhyming words (cat/bat, light/right)
4. Avoid similar sounds (accept/except, affect/effect)
5. Short, clear sentences
6. Active voice only
7. Use numbered lists for sequences:
    1. First point.
    2. Second point.
8. One action per sentence
9. If not in document: "I cannot find this information in the document."
10. Respond in {lang_name} only

ANSWER:"""
,
        "mixed": f"""You are a helpful assistant answering questions for people with MIXED DYSLEXIA.

UNDERSTANDING MIXED DYSLEXIA:
- Combination of phonological, surface, and visual challenges
- Needs maximum simplicity in every aspect
- Struggles with multiple reading difficulties simultaneously

YOUR TASK:
- Answer ONLY based on the document below
- Apply ALL simplification rules
- Maximum clarity and simplicity
- Perfect formatting for easy reading

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Maximum 8 words per sentence
3. Phonetically regular words only
4. Regular spelling patterns only
5. Visually clear - add space between sentences
6. One concept per sentence
7. Use numbered lists for sequences:
    1. First point.
    2. Second point.
8. Active voice only
9. Simple words only (under 10 letters)
10. If not in document: "I cannot find this information."
11. Respond in {lang_name} only

ANSWER:"""
,
        "general": f"""You are a helpful assistant answering questions for people with dyslexia.

DOCUMENT CONTEXT:
{document_text}

QUESTION:
{question}

ANSWER GUIDELINES:
1. Answer ONLY from the document above
2. Use simple, common words
3. Keep sentences under 15 words
4. One idea per sentence
5. Active voice only
6. Avoid jargon
7. If not in document: "I cannot find this information in the document."
8. If multiple points, use numbered list:
    1. First point.
    2. Second point.
9. Respond in {lang_name} only

ANSWER:"""
    }
    
    prompt = qa_prompts_by_type.get(dyslexia_type, qa_prompts_by_type["general"])
    return prompt

async def simplify_text(text: str, dyslexia_type: str = "general", language: str = "en") -> dict:
    """Simplify text for dyslexic users"""
    
    if not client:
        return {
            "error": "Groq API key not configured.",
            "success": False
        }
    
    if not text.strip():
        return {
            "error": "Please provide text to simplify.",
            "success": False
        }
    
    language_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "hi": "Hindi", "ar": "Arabic",
        "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ru": "Russian"
    }
    lang_name = language_names.get(language, "English")
    
    # Generate type-specific prompt for simplification
    prompt = _get_simplification_prompt(text, dyslexia_type, lang_name)
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024
        )
        
        simplified = response.choices[0].message.content.strip()
        
        return {
            "original": text,
            "simplified": simplified,
            "dyslexia_type": dyslexia_type,
            "language": language,
            "success": True
        }
    except Exception as e:
        return {
            "error": f"Error simplifying text: {str(e)}",
            "success": False
        }

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
        response = await client.chat.completions.create(
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
