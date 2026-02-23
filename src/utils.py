import re
from pathlib import Path

def read_text_file(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def clean_text(text: str) -> str:
    # Basic cleanup: normalize whitespace, remove control chars
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def safe_get(d: dict, key: str, default=None):
    return d.get(key, default)

def is_pdf(filename: str) -> bool:
    return filename.lower().endswith(".pdf")

def is_docx(filename: str) -> bool:
    return filename.lower().endswith(".docx")
