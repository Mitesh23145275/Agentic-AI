import os
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency fallback
    PdfReader = None


def extract_resume_text_from_pdf(pdf_path: Optional[str] = None) -> str:
    if not pdf_path:
        return ""

    if not os.path.exists(pdf_path):
        return ""

    if PdfReader is None:
        return "Resume extraction is unavailable because pypdf is not installed."

    try:
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(page for page in pages if page).strip()
    except Exception as exc:
        return f"Unable to read resume PDF: {exc}"
