import fitz
from pdf2image import convert_from_path
import pytesseract
import httpx
import json

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    doc.close()
    if len(text.strip()) < 100:  # Fallback to OCR for scanned datasheets
        images = convert_from_path(pdf_path, dpi=300)
        text = "".join(pytesseract.image_to_string(img) for img in images)
    return text

def extract_specs_with_ollama(raw_text: str) -> dict:
    prompt = """Extract hardware specs into strict JSON. No units in quantitative fields.
    SCHEMA: {"quantitative": {"total_ports": <num>, "poe_budget_w": <num>, "uplink_speed_gbps": <num>}, "boolean_features": {"l2_plus_routing": <bool>, "fanless": <bool>}, "misc": {"form_factor": "<str>"}}"""
    
    payload = {
        "model": "llama3",
        "prompt": prompt + "\n\n--- TEXT ---\n" + raw_text,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
    
    with httpx.Client(timeout=120.0) as client:
        response = client.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return json.loads(result.get("response", "{}"))
