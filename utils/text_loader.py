"""
CLAUSE AI — TEXT FILE LOADER (FINAL PRODUCTION VERSION)

Supports:
✔ txt files
✔ multiple files
✔ streamlit uploads
✔ URL loading
✔ safe save
✔ stats
✔ production logging
"""

import logging
import os
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)


# =========================================================
# LOAD SINGLE FILE
# =========================================================
def load_text_file(file_path: str, encoding: str = "utf-8") -> str:
    """Load text safely from local file"""

    if not file_path:
        logger.warning("Empty file path")
        return ""

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""

    try:
        with open(file_path, "r", encoding=encoding, errors="ignore") as f:
            text = f.read()

        logger.info(f"Loaded file: {file_path}")
        return text

    except Exception as e:
        logger.error(f"Error loading file: {e}")
        return ""


# =========================================================
# LOAD MULTIPLE FILES
# =========================================================
def load_multiple_text_files(file_paths: List[str]) -> Dict[str, str]:
    """Load multiple files → returns dict"""

    results: Dict[str, str] = {}

    if not file_paths:
        return results

    for path in file_paths:
        text = load_text_file(path)
        if text:
            results[os.path.basename(path)] = text

    logger.info(f"Loaded {len(results)} files")
    return results


# =========================================================
# LOAD FROM BYTES (Streamlit upload)
# =========================================================
def load_text_from_bytes(data: bytes, encoding="utf-8") -> str:
    """Used for st.file_uploader"""

    if not data:
        return ""

    try:
        return data.decode(encoding, errors="ignore")
    except Exception as e:
        logger.error(f"Decode error: {e}")
        return ""


# =========================================================
# LOAD FROM URL
# =========================================================
def load_text_from_url(url: str) -> str:
    """Load text from contract URL"""

    if not url:
        return ""

    try:
        r = requests.get(url, timeout=20)

        if r.status_code != 200:
            logger.error(f"URL load failed: {r.status_code}")
            return ""

        return r.text

    except Exception as e:
        logger.error(f"URL error: {e}")
        return ""


# =========================================================
# SAVE FILE
# =========================================================
def save_text_file(content: str, file_path: str) -> bool:
    """Save text safely"""

    if content is None:
        return False

    try:
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Saved file: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Save error: {e}")
        return False


# =========================================================
# APPEND FILE
# =========================================================
def append_to_file(content: str, file_path: str) -> bool:
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Append error: {e}")
        return False


# =========================================================
# FILE STATS
# =========================================================
def count_words(text: str) -> int:
    return len(text.split()) if text else 0


def count_lines(text: str) -> int:
    return len(text.splitlines()) if text else 0


def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    print("Text loader test")

    sample = "Clause AI contract test\nHello world"
    path = "test.txt"

    save_text_file(sample, path)

    text = load_text_file(path)
    print("Loaded:", text)

    print("Words:", count_words(text))
    print("Lines:", count_lines(text))

    os.remove(path)
    print("Done")
