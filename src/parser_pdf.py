import pdfplumber
from io import BytesIO
from PIL import Image
import pytesseract

def parse_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                # Try native text extraction
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    # Fallback to OCR if no text
                    img = page.to_image(resolution=300).original
                    text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        print(f"PDF parsing error: {e}")
    return text.strip()
