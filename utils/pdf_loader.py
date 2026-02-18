"""
PDF loading & parsing utilities for ClauseAI
Supports:
- PyPDF2 (basic extraction)
- pdfplumber (better extraction)
- bytes upload (Streamlit/file uploader)
- metadata extraction
"""

import io
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# =========================================================
# OPTIONAL LIBRARIES
# =========================================================
try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not installed → pip install PyPDF2")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except Exception:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not installed → optional but recommended")


# =========================================================
# MAIN PDF LOADER (AUTO BEST METHOD)
# =========================================================
def load_pdf(file_path: str) -> str:
    """
    Smart PDF loader.
    Uses pdfplumber first (better), fallback to PyPDF2.
    """

    if PDFPLUMBER_AVAILABLE:
        text = _load_with_pdfplumber(file_path)
        if text.strip():
            return text

    if PYPDF2_AVAILABLE:
        return _load_with_pypdf2(file_path)

    logger.error("No PDF library installed.")
    return ""


# =========================================================
# LOAD FROM BYTES (STREAMLIT UPLOAD)
# =========================================================
def load_pdf_from_bytes(data: bytes) -> str:
    if not data:
        return ""

    try:
        if PDFPLUMBER_AVAILABLE:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
                return "\n\n".join(pages)

        if PYPDF2_AVAILABLE:
            reader = PdfReader(io.BytesIO(data))
            pages = [p.extract_text() or "" for p in reader.pages]
            return "\n\n".join(pages)

    except Exception as e:
        logger.error(f"PDF byte read error: {e}")

    return ""


# =========================================================
# PDFPLUMBER METHOD (BEST)
# =========================================================
def _load_with_pdfplumber(file_path: str) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            pages = []
            for page in pdf.pages:
                txt = page.extract_text() or ""
                if txt.strip():
                    pages.append(txt)

        logger.info(f"PDF loaded with pdfplumber ({len(pages)} pages)")
        return "\n\n".join(pages)

    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
        return ""


# =========================================================
# PYPDF2 METHOD (FALLBACK)
# =========================================================
def _load_with_pypdf2(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        pages = []

        for page in reader.pages:
            txt = page.extract_text() or ""
            if txt.strip():
                pages.append(txt)

        logger.info(f"PDF loaded with PyPDF2 ({len(pages)} pages)")
        return "\n\n".join(pages)

    except Exception as e:
        logger.error(f"PyPDF2 failed: {e}")
        return ""


# =========================================================
# METADATA
# =========================================================
def extract_pdf_metadata(file_path: str) -> Dict:
    meta = {
        "title": "",
        "author": "",
        "pages": 0
    }

    if not PYPDF2_AVAILABLE:
        return meta

    try:
        reader = PdfReader(file_path)
        meta["pages"] = len(reader.pages)

        if reader.metadata:
            meta["title"] = reader.metadata.get("/Title", "")
            meta["author"] = reader.metadata.get("/Author", "")

        return meta

    except Exception as e:
        logger.error(f"Metadata error: {e}")
        return meta


# =========================================================
# TABLE EXTRACTION (OPTIONAL)
# =========================================================
def extract_pdf_tables(file_path: str) -> List:
    if not PDFPLUMBER_AVAILABLE:
        return []

    try:
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)

        return tables

    except Exception as e:
        logger.error(f"Table extraction error: {e}")
        return []


# =========================================================
# TEST
# =========================================================
if __name__ == "__main__":
    print("PDF Loader Ready")

    if PYPDF2_AVAILABLE:
        print("✓ PyPDF2 installed")
    else:
        print("✗ PyPDF2 missing")

    if PDFPLUMBER_AVAILABLE:
        print("✓ pdfplumber installed (recommended)")
    else:
        print("⚠ pdfplumber optional but recommended")
