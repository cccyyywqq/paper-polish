import io
from typing import Optional
from docx import Document
from PyPDF2 import PdfReader


def extract_text_from_docx(file_content: bytes) -> str:
    doc = Document(io.BytesIO(file_content))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_pdf(file_content: bytes) -> str:
    pdf = PdfReader(io.BytesIO(file_content))
    text_parts = []

    for page in pdf.pages:
        text = page.extract_text()
        if text.strip():
            text_parts.append(text.strip())

    return "\n\n".join(text_parts)


def extract_text_from_txt(file_content: bytes) -> str:
    try:
        return file_content.decode("utf-8")
    except UnicodeDecodeError:
        return file_content.decode("gbk", errors="ignore")


def extract_text(file_content: bytes, filename: str) -> Optional[str]:
    filename_lower = filename.lower()

    if filename_lower.endswith(".docx"):
        return extract_text_from_docx(file_content)
    elif filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith(".txt"):
        return extract_text_from_txt(file_content)
    else:
        return None
