from pdfminer.high_level import extract_text as pdf_extract
from docx import Document as DocxDocument
from pdf2image import convert_from_path
import pytesseract
import os

def extract_text(file_path, file_type):
    if file_type == "pdf":
        text = pdf_extract(file_path)

        # fallback to OCR if text is empty
        if text.strip():
            return text

        images = convert_from_path(file_path)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img)

        return ocr_text

    elif file_type == "docx":
        doc = DocxDocument(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    elif file_type == "txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    return ""
