def is_valid_llm_output(text):
    """
    Sanity-checks the LLM response before sending it to the UI.
    """
    if not text or not isinstance(text, str):
        return False
        
    text = text.strip()
    
    # Too short to be a real report
    if len(text) < 50:
        return False
        
    # Catch common API error bleed-throughs
    bad_phrases = ["I am an AI", "As a language model", "API Error", "502 Bad Gateway", "instructions"]
    for phrase in bad_phrases:
        if phrase.lower() in text.lower():
            return False
            
    return True