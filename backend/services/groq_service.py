from groq import AsyncGroq
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Dyslexia type specific guidelines
DYSLEXIA_GUIDELINES = {
    "phonological": {
        "name": "Phonological Dyslexia",
        "focus": "difficulty connecting sounds to letters",
        "guidelines": """
1. Use simple, phonetically regular words
2. Avoid words with silent letters or unusual spellings
3. Use consistent spelling patterns
4. Avoid homophones (words that sound alike)
5. Keep words intact; do NOT split words into syllables or use extra spaces within words."""
    },
    "surface": {
        "name": "Surface Dyslexia", 
        "focus": "difficulty recognizing whole word shapes",
        "guidelines": """
1. Use shorter, common words
2. Avoid irregular spellings
3. Keep consistent word patterns
4. Use words that look different from each other
5. Avoid similar-looking words together"""
    },
    "visual": {
        "name": "Visual Dyslexia",
        "focus": "difficulty processing visual text",
        "guidelines": """
1. Use very short sentences (8 to 10 words maximum)
2. Add extra spacing between ideas
3. Avoid crowded text
4. Use clear paragraph breaks
5. One idea per sentence"""
    },
    "auditory": {
        "name": "Auditory Dyslexia",
        "focus": "difficulty processing spoken language",
        "guidelines": """
1. Write for easy visual scanning
2. Use numbered lists (1, 2, 3) instead of bullets
3. Avoid words that sound similar
4. Use clear, simple sentence structure
5. Focus on visual clarity of the text"""
    },
    "mixed": {
        "name": "Mixed/Deep Dyslexia",
        "focus": "combination of multiple difficulties",
        "guidelines": """
1. Use the simplest possible words
2. Very short sentences (maximum 8 words)
3. One concept per paragraph
4. Use numbered steps for sequences
5. Repeat important information
6. Keep words intact; do NOT split words into syllables or use spaces within words."""
    },
    "general": {
        "name": "General Dyslexia Support",
        "focus": "general reading difficulties",
        "guidelines": """
1. Use simple, common words
2. Keep sentences short (maximum 15 words)
3. Use active voice
4. Clear paragraph structure
5. Avoid jargon"""
    }
}

def _get_simplify_prompt(text: str, language: str, dyslexia_type: str, lang_name: str, dx_info: dict) -> str:
    """Generate dyslexia-type-specific simplification prompts"""
    
    # Language-specific instruction
    language_instruction = f"""CRITICAL LANGUAGE RULE:
- Output MUST be in {lang_name} ONLY.
- If the input text is in {lang_name}, keep it in {lang_name}.
- DO NOT translate to English.
- DO NOT transliterate ANY text (for example, do NOT convert Hindi देवनागरी to "Devnagari" or ज़िंदगी to "JINDAGI").
- Preserve the original script and writing system (Devanagari for Hindi, Arabic script for Arabic, Chinese characters for Chinese, etc.).
- Keep ALL text including headings, titles, and content in the SAME LANGUAGE and SAME SCRIPT as the input.
- If you need headings, use the ORIGINAL SCRIPT, not English transliteration."""
    
    # Base prompt structure for all types
    base_rules = """STRICT OUTPUT RULES:
1. ONLY output the simplified content.
2. DO NOT use special characters like asterisks, double asterisks, hashes, bullets, emojis, or symbols.
3. Use PLAIN TEXT only.
4. For headings, keep them in the ORIGINAL LANGUAGE AND SCRIPT (no transliteration).
5. Use numbered lists (1, 2, 3) ONLY when a list is necessary, NOT ALWAYS.
6. Do NOT use parentheses or brackets.
7. Do NOT include introductions, explanations, summaries, or meta-commentary.

CRITICAL SIMPLIFICATION RULES:
1. Focus on CHANGING WORDING to be easier, NOT shortening the text.
2. DO NOT summarize. Keep the same amount of information as the original.
3. Do NOT add interpretations, advice, or explanations not in the original.
4. Do NOT expand on ideas - only simplify existing ones.
5. Maintain the original semantic meaning and approximate length.
6. Make text EASIER to read by using simpler words and better structure.

CONTENT PRESERVATION RULES:
1. Keep ALL important information from the original text.
2. Do NOT remove meaning or details.
3. Do NOT add new information."""

    # Type-specific prompts
    type_specific_prompts = {
        "phonological": f"""You are an expert in helping people with PHONOLOGICAL DYSLEXIA read text.
People with phonological dyslexia struggle to connect sounds to letters and silent letters.

{language_instruction}

FOCUS:
1. Use phonetically regular words. Avoid irregular spellings.
2. Avoid words with silent letters (knight, psychology, ptero-).
3. Use consistent pronunciation patterns throughout.
4. Avoid homophones (to/too, there/their, one/won).
5. Keep words intact. Do NOT split words into syllables.
6. Use clear, direct language without sound-related tricks.

READABILITY RULES:
1. Use clear sentences. If a sentence is complex, SPLIT it into two or more sentences.
2. DO NOT REMOVE any information or details.
3. Use common, everyday words. Avoid jargon and complex vocabulary.
4. Maintain the original message completely.
5. Add an empty line between paragraphs.
6. Use consistent wording and active voice only.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):""",

        "surface": f"""You are an expert in helping people with SURFACE DYSLEXIA read text.
People with surface dyslexia struggle to recognize whole word shapes and irregular spellings.

{language_instruction}

FOCUS:
1. Use shorter, common words with regular spelling patterns.
2. Avoid irregular and unusual spellings.
3. Use words that look different from each other (avoid similar shapes like "desert" and "dessert").
4. Keep consistent word patterns and word shapes.
5. Avoid multiple words that look similar together.
6. Prefer phonetically regular words.

READABILITY RULES:
1. Use clear sentences. SPLIT complex sentences to keep them readable.
2. DO NOT REMOVE details. Keep all facts and information.
3. Use very common, everyday words only.
4. Add an empty line between paragraphs.
5. Make each word visually distinct.
6. Use active voice only.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):""",

        "visual": f"""You are an expert in helping people with VISUAL DYSLEXIA read text.
People with visual dyslexia struggle with visual crowding and letter/word recognition.

{language_instruction}

FOCUS:
1. Use VERY short sentences. Maximum 8 to 10 words per sentence.
2. Add extra space between ideas and paragraphs.
3. Avoid crowded text. Use generous line spacing.
4. One main idea per sentence.
5. Use clear paragraph breaks and white space.
6. Avoid similar-looking letters close together (b/d/p/q).

READABILITY RULES:
1. Break complex sentences into multiple VERY short sentences.
2. DO NOT SUMMARIZE. Preserve every single detail from the original.
3. Add blank lines between every 2-3 sentences.
4. Use active voice only and the simplest possible words.
5. Avoid complex structures but keep all information.
6. Make text visually scannable.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):""",

        "auditory": f"""You are an expert in helping people with AUDITORY DYSLEXIA read text.
People with auditory dyslexia struggle with similar-sounding words and phoneme processing.

{language_instruction}

FOCUS:
1. Avoid words that sound similar (accept/except, affect/effect).
2. Avoid complex phonemes and difficult-to-pronounce words.
3. Use words with clear, distinct sounds.
4. Avoid rhyming or sound-alike patterns.
5. Write for visual clarity over phonetic appeal.
6. Use numbered lists for sequences and steps.

READABILITY RULES:
1. Use clear sentences. If a sentence has similar-sounding words, REWORD it.
2. DO NOT REMOVE content. Maintain all information from the original.
3. Keep sentences under 12 words by splitting them.
4. Add visual structure with numbered lists when appropriate.
5. Use active voice only.
6. Ensure visual scanning is easy.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):""",

        "mixed": f"""You are an expert in helping people with MIXED/DEEP DYSLEXIA read text.
People with mixed dyslexia struggle with visual, auditory, and phonological challenges combined.

{language_instruction}

FOCUS:
1. Use the absolute simplest words and structures.
2. Very short sentences (8 words maximum).
3. One concept per paragraph.
4. Use numbered steps for sequences.
5. Repeat important information.
6. Keep words intact. Do NOT split words.
7. Use consistent wording throughout.
8. Extra white space and clear formatting.

READABILITY RULES:
1. Extreme simplicity and clarity. DO NOT REMOVE any information.
2. SPLIT complex sentences into multiple 8-word sentences.
3. Maximum visual separation between ideas but keep all facts.
4. Use only common, easy words and active voice.
5. Numbered lists for any sequences.
6. Preserve the full meaning of the original text.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):""",

        "general": f"""You are an expert in making text accessible for people with general reading difficulties.

{language_instruction}

READABILITY RULES:
1. Use clear sentences. SPLIT complex ideas into multiple sentences.
2. DO NOT SUMMARIZE. Keep all information and details.
3. Use common, everyday words. Avoid jargon.
4. Maintain the original semantic meaning completely.
5. Add an empty line between paragraphs.
6. Use active voice only.
7. Avoid abbreviations, idioms, or metaphors.

{base_rules}

TEXT TO SIMPLIFY:
{text}

SIMPLIFIED TEXT (PLAIN TEXT ONLY):"""
    }
    
    return type_specific_prompts.get(dyslexia_type, type_specific_prompts["general"])

async def simplify_text(text: str, language: str = "en", dyslexia_type: str = "general") -> str:
    """Simplify complex text for easier reading by people with dyslexia using type-specific prompts"""
    if not client:
        return "Error: Groq API key not configured. Please set GROQ_API_KEY in .env file."
    
    language_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "hi": "Hindi", "ar": "Arabic",
        "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ru": "Russian"
    }
    lang_name = language_names.get(language, "English")
    
    # Get dyslexia-specific guidelines
    dx_info = DYSLEXIA_GUIDELINES.get(dyslexia_type, DYSLEXIA_GUIDELINES["general"])
    
    # Generate type-specific prompt
    prompt = _get_simplify_prompt(text, language, dyslexia_type, lang_name, dx_info)

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05,  # Very low for strict rule following
            max_tokens=2048
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error simplifying text: {str(e)}"

def _get_summarize_prompt(text: str, language: str, dyslexia_type: str, lang_name: str, dx_info: dict) -> str:
    """Generate dyslexia-type-specific summarization prompts"""
    
    # Language-specific instruction
    language_instruction = f"""CRITICAL LANGUAGE RULE:
- Output MUST be in {lang_name} ONLY.
- If the input text is in {lang_name}, keep it in {lang_name}.
- DO NOT translate to English.
- DO NOT transliterate ANY text (for example, do NOT convert Hindi देवनागरी to "Devnagari" or ज़िंदगी to "JINDAGI").
- Preserve the original script and writing system (Devanagari for Hindi, Arabic script for Arabic, Chinese characters for Chinese, etc.).
- Keep ALL text including headings, titles, and content in the SAME LANGUAGE and SAME SCRIPT as the input.
- If you need headings, use the ORIGINAL SCRIPT, not English transliteration."""
    
    # Base prompt structure for all types
    base_rules = """STRICT OUTPUT RULES:
1. ONLY output the summary content.
2. DO NOT use special characters like asterisks, double asterisks, hashes, bullets, emojis, or symbols.
3. Use PLAIN TEXT only.
4. DO NOT use numbered lists or bullet points.
5. Write in continuous paragraph form with clear sentences.
6. Do NOT include titles, headings, introductions, explanations, or meta-commentary.
7. Do NOT use parentheses or brackets.

SUMMARY RULES:
1. CORE MESSAGE ONLY: Focus on main ideas and key facts.
2. CONDENSE: The output MUST be significantly shorter than the input (aim for 30-50% length).
3. REMOVE FLUFF: Remove minor details, examples, and filler words.
4. PRESERVE MEANING: Ensure the essential meaning is not changed.
5. CLARITY: Use simple sentences to explain core concepts briefly.
6. DO NOT repeat the entire text; extract only what is most important."""

    # Type-specific prompts
    type_specific_prompts = {
        "phonological": f"""You are an expert in creating summaries for people with PHONOLOGICAL DYSLEXIA.
People with phonological dyslexia struggle to connect sounds to letters.

{language_instruction}

FOCUS:
1. Use phonetically regular words with consistent pronunciation.
2. Avoid words with silent letters.
3. Keep point wording simple and phonetically clear.
4. Avoid homophones and confusing sound patterns.

READABILITY RULES:
1. Each point must be ONE short sentence (under 12 words).
2. Use common, phonetically regular words only.
3. Avoid jargon, idioms, and figurative language.
4. Use active voice only.
5. Use consistent wording throughout.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (PLAIN TEXT PARAGRAPH, SAME LANGUAGE AS INPUT):""",

        "surface": f"""You are an expert in creating summaries for people with SURFACE DYSLEXIA.
People with surface dyslexia struggle to recognize whole word shapes and irregular spellings.

{language_instruction}

FOCUS:
1. Use short, common words with regular spelling patterns.
2. Avoid irregular and unusual spellings.
3. Use words that look visually distinct from each other.
4. Keep consistent word patterns throughout.

READABILITY RULES:
1. Each point must be ONE short sentence (under 10 words).
2. Use only the most common, regular words.
3. Make each word visually distinct.
4. Avoid jargon and figurative language.
5. Use active voice only.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (PLAIN TEXT PARAGRAPH, SAME LANGUAGE AS INPUT):""",

        "visual": f"""You are an expert in creating summaries for people with VISUAL DYSLEXIA.
People with visual dyslexia struggle with visual crowding and letter/word recognition.

{language_instruction}

FOCUS:
1. Use VERY short sentences (maximum 8 words each).
2. One main idea per point.
3. Use the simplest words possible.
4. Separate ideas clearly and distinctly.

READABILITY RULES:
1. Each point is ONE ultra-short sentence (max 8 words).
2. Use the simplest possible words.
3. Create visual clarity through extreme simplicity.
4. Avoid complex structures.
5. Use active voice only.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (PLAIN TEXT PARAGRAPH, SAME LANGUAGE AS INPUT):""",

        "auditory": f"""You are an expert in creating summaries for people with AUDITORY DYSLEXIA.
People with auditory dyslexia struggle with similar-sounding words and phoneme processing.

{language_instruction}

FOCUS:
1. Avoid words that sound similar or rhyme.
2. Use words with clear, distinct sounds.
3. Write for visual clarity over phonetic appeal.
4. Use numbered lists for sequences.

READABILITY RULES:
1. Each point must be ONE short sentence (under 12 words).
2. Use words with distinct, clear sounds.
3. Avoid rhyming patterns and similar-sounding words.
4. Use active voice only.
5. Write for visual scanning ease.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (PLAIN TEXT PARAGRAPH, SAME LANGUAGE AS INPUT):""",

        "mixed": f"""You are an expert in creating summaries for people with MIXED/DEEP DYSLEXIA.
People with mixed dyslexia struggle with visual, auditory, and phonological challenges combined.

{language_instruction}

FOCUS:
1. Use the absolute simplest words and structures.
2. Very short sentences (8 words maximum).
3. One concept per point.
4. Extra clarity and visual separation.

READABILITY RULES:
1. Each point is ONE sentence (maximum 8 words).
2. Use only the most common words.
3. Extreme simplicity and clarity.
4. Use active voice only.
5. Ensure complete clarity and no ambiguity.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (PLAIN TEXT PARAGRAPH, SAME LANGUAGE AS INPUT):""",

        "general": f"""You are an expert in creating accessible summaries for people with general reading difficulties.

{language_instruction}

READABILITY RULES:
1. Each point must be ONE short sentence.
2. Keep sentences under 15 words when possible.
3. Use simple, common words.
4. Avoid jargon, idioms, metaphors, and figurative language.
5. Use active voice only.
6. Use consistent wording. Do not rename the same idea.
7. Avoid abbreviations unless they are very common.

{base_rules}

TEXT TO SUMMARIZE:
{text}

SUMMARY (NUMBERED LIST, PLAIN TEXT ONLY):"""
    }
    
    return type_specific_prompts.get(dyslexia_type, type_specific_prompts["general"])

async def summarize_text(text: str, language: str = "en", dyslexia_type: str = "general") -> str:
    """Create a concise summary of the text using type-specific prompts"""
    if not client:
        return "Error: Groq API key not configured. Please set GROQ_API_KEY in .env file."
    
    language_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "hi": "Hindi", "ar": "Arabic",
        "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ru": "Russian"
    }
    lang_name = language_names.get(language, "English")
    
    # Get dyslexia-specific guidelines
    dx_info = DYSLEXIA_GUIDELINES.get(dyslexia_type, DYSLEXIA_GUIDELINES["general"])
    
    # Generate type-specific prompt
    prompt = _get_summarize_prompt(text, language, dyslexia_type, lang_name, dx_info)

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def get_dyslexia_types():
    """Return list of supported dyslexia types"""
    return [
        {"code": "phonological", "name": "Phonological Dyslexia", "description": "Difficulty connecting sounds to letters"},
        {"code": "surface", "name": "Surface Dyslexia", "description": "Difficulty recognizing whole word shapes"},
        {"code": "visual", "name": "Visual Dyslexia", "description": "Difficulty processing visual text"},
        {"code": "auditory", "name": "Auditory Dyslexia", "description": "Difficulty processing spoken language"},
        {"code": "mixed", "name": "Mixed/Deep Dyslexia", "description": "Combination of multiple difficulties"},
        {"code": "general", "name": "Not Sure / General", "description": "General reading support"}
    ]

