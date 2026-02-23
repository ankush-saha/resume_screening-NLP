import re

def normalize_email(text: str):
    match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    return match.group(0) if match else None

def normalize_phone(text: str):
    # Simple heuristic for phone numbers (international + local)
    match = re.search(r'(\+?\d[\d\s\-]{7,}\d)', text)
    return match.group(0) if match else None

def normalize_name(text: str):
    # Heuristic: look for lines starting with a capitalized name-like pattern
    # In production, use NER and resume layout cues
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        first_line = lines[0]
        # If first line is too long, skip
        if 2 <= len(first_line.split()) <= 6:
            return first_line
    return None
