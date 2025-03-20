import fitz
from PyPDF2 import PdfReader
from backend.vec import store_embeddings

def extract_text(file):
    text = None

    if file.type == "application/pdf":
        reader = PdfReader(file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])

    elif file.type == "text/plain":
        text = file.read().decode("utf-8")

    if text:  
        store_embeddings(text)
    
    return text