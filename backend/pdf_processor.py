import fitz
import os
from backend.config import PDF_FOLDER, MAX_PDFS

def save_pdf(file):
    os.makedirs(PDF_FOLDER, exist_ok=True)

    existing = os.listdir(PDF_FOLDER)
    if len(existing) >= MAX_PDFS:
        raise Exception("PDF upload limit reached (30). Delete older PDFs to upload new ones.")

    file_path = f"{PDF_FOLDER}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path


def extract_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    # Detect scanned or empty PDFs
    if len(text.strip()) < 30:
        return "IMAGE_ONLY_PDF"

    return text



def chunk_text(text, size=400):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]
