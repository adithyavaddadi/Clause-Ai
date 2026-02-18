from __future__ import annotations
import os
import requests
import logging
import time
from threading import Lock
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# =========================================================
# 🔵 GROQ SETTINGS (PRIMARY CLOUD FAST)
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
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "350"))

# retry safety
OLLAMA_RETRY = 2
OLLAMA_DELAY = 1.2

_lock = Lock()
_last_call = 0

# =========================================================
# 🔵 GROQ CALL
# =========================================================
def call_groq(prompt: str, temperature: float = 0.2, max_tokens: int = 900):

    if not GROQ_API_KEY:
        logger.warning("❌ GROQ API KEY missing")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional contract analysis AI."},
            {"role": "user", "content": prompt[:6000]},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)

        if r.status_code != 200:
            logger.warning(f"GROQ error {r.status_code}: {r.text[:200]}")
            return None

        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()

        if text:
            logger.info("✅ GROQ success")
            return text

        return None

    except Exception as e:
        logger.error(f"GROQ failed: {e}")
        return None


# =========================================================
# 🟢 OLLAMA CALL
# =========================================================
def call_ollama(prompt: str):

    global _last_call

    if not prompt:
        return None

    # small delay to prevent overload
    if time.time() - _last_call < 1.5:
        time.sleep(1.5)

    _last_call = time.time()

    try:
        with _lock:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt[:2200],
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": OLLAMA_NUM_PREDICT
                    }
                },
                timeout=OLLAMA_TIMEOUT
            )

        if r.status_code != 200:
            logger.warning(f"Ollama status {r.status_code}")
            return None

        text = r.json().get("response", "").strip()
        if text:
            logger.info("✅ Ollama success")
            return text

        return None

    except Exception as e:
        logger.warning(f"Ollama failed: {e}")
        return None


# =========================================================
# 🚀 MAIN HYBRID ROUTER
# =========================================================
def call_hybrid_llm(prompt: str, role: str = "analysis") -> str:
    """
    FINAL CLAUSEAI ROUTER

    Priority:
    1️⃣ GROQ (fast cloud)
    2️⃣ OLLAMA (local fallback)
    3️⃣ Safe fallback
    """

    if not prompt or not prompt.strip():
        return "No prompt provided"

    # =============================
    # 1️⃣ TRY GROQ FIRST
    # =============================
    response = call_groq(prompt)
    if response and len(response) > 5:
        return response

    logger.warning("⚠ Groq failed → switching to Ollama")

    # =============================
    # 2️⃣ TRY OLLAMA
    # =============================
    for _ in range(OLLAMA_RETRY):
        response = call_ollama(prompt)
        if response and len(response) > 5:
            return response
        time.sleep(OLLAMA_DELAY)

    # =============================
    # 3️⃣ FINAL SAFE FALLBACK
    # =============================
    logger.error("❌ Both Groq & Ollama failed")

    if role in ["summary", "report", "final"]:
        return "Final report unavailable. AI model not responding."

    return "Contract analysis unavailable. Please retry."
