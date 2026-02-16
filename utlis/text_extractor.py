import os
import PyPDF2
import docx

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        return extract_txt(filepath)

    elif ext == ".pdf":
        return extract_pdf(filepath)

    elif ext == ".docx":
        return extract_docx(filepath)

    else:
        return ""


def extract_txt(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_pdf(filepath):
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    return text


def extract_docx(filepath):
    doc = docx.Document(filepath)
    return " ".join([para.text for para in doc.paragraphs])
