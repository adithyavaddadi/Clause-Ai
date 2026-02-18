"""
ClauseAI - Full Environment Check
Verifies system readiness before running AI agents
Safe + clean + production ready
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# =========================================================
# PYTHON VERSION
# =========================================================
def check_python_version():
    print("Checking Python version...")
    v = sys.version_info

    if v.major >= 3 and v.minor >= 8:
        print(f"[OK] Python {v.major}.{v.minor}.{v.micro}")
        return True

    print(f"[X] Python {v.major}.{v.minor} detected — Requires 3.8+")
    return False


# =========================================================
# DEPENDENCY CHECK
# =========================================================
def check_dependencies():
    print("\nChecking dependencies...")

    required = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("dotenv", "Python-dotenv"),
        ("PyPDF2", "PyPDF2"),
        ("docx", "python-docx"),
        ("reportlab", "ReportLab"),
        ("bs4", "BeautifulSoup"),
    ]

    optional = [
        ("pinecone", "Pinecone"),
        ("numpy", "NumPy"),
    ]

    all_ok = True

    for mod, name in required:
        try:
            __import__(mod)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[X] {name} missing → pip install {mod}")
            all_ok = False

    for mod, name in optional:
        try:
            __import__(mod)
            print(f"[OK] {name} (optional)")
        except ImportError:
            print(f"- {name} (optional not installed)")

    return all_ok


# =========================================================
# ENV VARIABLES
# =========================================================
def check_env():
    print("\nChecking API keys...")

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    grok = os.getenv("GROK_API_KEY")
    openai = os.getenv("OPENAI_API_KEY")
    gemini = os.getenv("GEMINI_API_KEY")
    pinecone = os.getenv("PINECONE_API_KEY")

    if grok:
        print("[OK] GROK_API_KEY")
    else:
        print("- GROK_API_KEY not set")

    if openai:
        print("[OK] OPENAI_API_KEY")
    else:
        print("- OPENAI_API_KEY not set")

    if gemini:
        print("[OK] GEMINI_API_KEY")
    else:
        print("- GEMINI_API_KEY not set")

    if pinecone:
        print("[OK] PINECONE_API_KEY (vector memory enabled)")
    else:
        print("- PINECONE_API_KEY not set (optional)")

    # must have at least one LLM
    if grok or openai or gemini:
        print("\n[OK] At least one LLM configured")
        return True

    print("\n[X] No LLM configured → AI will not work")
    return False


# =========================================================
# PROJECT STRUCTURE
# =========================================================
def check_structure():
    print("\nChecking project structure...")

    required_dirs = ["agents_llm", "utils", "report"]
    required_files = ["streamlit_app.py"]

    ok = True

    for d in required_dirs:
        if (ROOT / d).exists():
            print(f"[OK] {d}/")
        else:
            print(f"[X] Missing folder: {d}")
            ok = False

    for f in required_files:
        if (ROOT / f).exists():
            print(f"[OK] {f}")
        else:
            print(f"[X] Missing file: {f}")
            ok = False

    return ok


# =========================================================
# MAIN
# =========================================================
def main():
    os.chdir(ROOT)

    print("=" * 60)
    print("CLAUSE AI — SYSTEM ENVIRONMENT CHECK")
    print("=" * 60)

    results = [
        ("Python", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("API Keys", check_env()),
        ("Project Structure", check_structure()),
    ]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_ok = True
    for name, status in results:
        print(f"{name:<20}: {'PASS' if status else 'FAIL'}")
        if not status:
            all_ok = False

    print("=" * 60)

    if all_ok:
        print("\n[READY] ClauseAI system fully operational")
        return 0

    print("\n[WARNING] Fix above issues before running ClauseAI")
    return 1


if __name__ == "__main__":
    sys.exit(main())
