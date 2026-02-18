"""
CLAUSE AI — UNIVERSAL FILE + URL LOADER
Supports:
✔ Multiple files
✔ PDF / DOCX / TXT
✔ URL loading
✔ Streamlit compatible
✔ Safe + no crash
"""

import logging
import requests
from typing import List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# optional imports
try:
    import docx
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not installed")

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not installed")


# =========================================================
# TXT
# =========================================================
def _read_txt(file) -> str:
    try:
        return file.read().decode("utf-8", errors="ignore")
    except:
        return ""


# =========================================================
# PDF
# =========================================================
def _read_pdf(file) -> str:
    if not PDF_AVAILABLE:
        return ""

    try:
        reader = PdfReader(file)
        pages = []

        for p in reader.pages:
            t = p.extract_text()
            if t:
                pages.append(t)

        return "\n".join(pages)

    except Exception as e:
        logger.error(f"PDF read error: {e}")
        return ""


# =========================================================
# DOCX
# =========================================================
def _read_docx(file) -> str:
    if not DOCX_AVAILABLE:
        return ""

    try:
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    except Exception as e:
        logger.error(f"DOCX read error: {e}")
        return ""


# =========================================================
# SINGLE FILE LOADER
# =========================================================
def load_uploaded_file(uploaded_file) -> str:

    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return _read_txt(uploaded_file)

    if name.endswith(".pdf"):
        return _read_pdf(uploaded_file)

    if name.endswith(".docx"):
        return _read_docx(uploaded_file)

    logger.warning(f"Unsupported file: {name}")
    return ""


# =========================================================
# MULTIPLE FILES
# =========================================================
def load_multiple_files(uploaded_files) -> List[str]:

    if not uploaded_files:
        return []

    texts = []

    for f in uploaded_files:
        try:
            t = load_uploaded_file(f)
            if t and t.strip():
                texts.append(t.strip())
        except Exception as e:
            logger.error(f"File load error: {e}")

    return texts


# =========================================================
# URL LOADER
# =========================================================
def load_from_url(url: str) -> str:

    if not url:
        return ""

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)

        if r.status_code != 200:
            logger.error(f"URL fetch failed: {r.status_code}")
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        for s in soup(["script", "style"]):
            s.extract()

        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 30]

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"URL load error: {e}")
        return ""


# =========================================================
# MERGE ALL SOURCES ⭐
# =========================================================
def load_all_sources(uploaded_files=None, url: str = "") -> str:
    """
    Combines:
    - multiple uploaded files
    - url content
    into single contract text
    """

    texts = []

    if uploaded_files:
        texts.extend(load_multiple_files(uploaded_files))

    if url:
        url_text = load_from_url(url)
        if url_text:
            texts.append(url_text)

    if not texts:
        return ""

    merged = "\n\n========== NEW DOCUMENT ==========\n\n".join(texts)
    return merged


# =========================================================
# TEST
# =========================================================
if __name__ == "__main__":
    print("ClauseAI loader ready")
