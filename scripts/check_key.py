"""
ClauseAI - API Key Configuration Checker
Safe + clean + production ready
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

# load .env
load_dotenv(ROOT / ".env")


# =====================================================
# MASK KEY FOR DISPLAY
# =====================================================
def _mask_key(value: str) -> str:
    if not value:
        return "***"
    if len(value) <= 10:
        return "***"
    return value[:6] + "..." + value[-4:]


# =====================================================
# CHECK API KEYS
# =====================================================
def check_api_keys():

    print("\n" + "=" * 60)
    print("CLAUSE AI — API CONFIGURATION CHECK")
    print("=" * 60)

    optional_keys = [
        "GROK_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "PINECONE_API_KEY"
    ]

    found = []
    missing = []

    for key in optional_keys:
        val = os.getenv(key)

        if val:
            print(f"[OK] {key:<18} : {_mask_key(val)}")
            found.append(key)
        else:
            print(f"[--] {key:<18} : Not configured")
            missing.append(key)

    print("-" * 60)
    print(f"Configured: {len(found)}   Missing: {len(missing)}")

    # --------------------------------------------------
    # LLM CHECK
    # --------------------------------------------------
    if any(k in found for k in ["GROK_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]):
        print("\n[OK] LLM Provider detected → AI will work")
    else:
        print("\n[WARNING] No LLM API configured")
        print("Add GROK_API_KEY or OPENAI_API_KEY or GEMINI_API_KEY")

    # --------------------------------------------------
    # PINECONE CHECK
    # --------------------------------------------------
    if "PINECONE_API_KEY" in found:
        print("[OK] Vector memory enabled")
    else:
        print("[INFO] Pinecone not configured (optional)")

    print("=" * 60 + "\n")

    return True


# =====================================================
# MAIN
# =====================================================
def main():
    try:
        os.chdir(ROOT)
        check_api_keys()
    except Exception as e:
        print(f"Error checking keys: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
