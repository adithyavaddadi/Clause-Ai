"""
CLAUSE AI — HYBRID LLM ENGINE
Priority:
1️⃣ GROQ (cloud fast)
2️⃣ OLLAMA (local fallback)
3️⃣ Safe fallback
"""

import os
import time
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# =========================================================
# 🔵 GROQ SETTINGS (PRIMARY)
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GSK_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TIMEOUT = 60

# =========================================================
# 🟢 OLLAMA SETTINGS (LOCAL FALLBACK)
# =========================================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT = 120

_last_local_call = 0

# =========================================================
# 🔵 GROQ CALL
# =========================================================
def call_groq(prompt: str, temperature: float = 0.2, max_tokens: int = 800):

    if not GROQ_API_KEY:
        logger.warning("❌ GROQ API key missing")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert contract analysis AI."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)

        if r.status_code != 200:
            logger.warning(f"GROQ error {r.status_code}: {r.text}")
            return None

        data = r.json()

        # safe parse
        if "choices" not in data:
            logger.warning(f"GROQ invalid response: {data}")
            return None

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.error(f"GROQ failed: {e}")
        return None


# =========================================================
# 🟢 OLLAMA LOCAL CALL
# =========================================================
def call_ollama(prompt: str):

    global _last_local_call

    if not prompt:
        return None

    # prevent overload
    if time.time() - _last_local_call < 1.2:
        time.sleep(1.2)

    _last_local_call = time.time()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt[:2000],
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )

        if r.status_code != 200:
            logger.warning(f"Ollama status {r.status_code}")
            return None

        return r.json().get("response", "").strip()

    except Exception as e:
        logger.warning(f"Ollama failed: {e}")
        return None


# =========================================================
# 🧠 MASTER HYBRID ROUTER
# =========================================================
def call_hybrid_llm(prompt: str, role: str = "analysis") -> str:
    """
    MASTER ROUTER

    1. Try GROQ
    2. Fallback to Ollama
    3. Safe fallback
    """

    if not prompt:
        return "No prompt provided"

    # 🔵 TRY GROQ FIRST
    groq_response = call_groq(prompt)

    if groq_response and len(groq_response) > 5:
        return groq_response

    logger.warning("⚠ Groq failed → switching to Ollama")

    # 🟢 TRY OLLAMA
    local_response = call_ollama(prompt)

    if local_response and len(local_response) > 5:
        return local_response

    # 🔴 FINAL SAFE FALLBACK
    logger.error("❌ Groq + Ollama both failed")

    if role in ["summary", "report"]:
        return "Final report unavailable. Please retry."

    return "Analysis unavailable. Please retry."
