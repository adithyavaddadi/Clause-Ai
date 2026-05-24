"""
CLAUSE AI — HYBRID LLM ROUTING ENGINE
Manages automatic failover between:
1️⃣ GROQ (high performance cloud LLM)
2️⃣ OLLAMA (secure offline local LLM)
3️⃣ Deterministic static fallback report
"""

import os
import time
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# =========================================================
# 🔵 GROQ SETTINGS (PRIMARY HIGH-SPEED CLOUD)
# =========================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GSK_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_TIMEOUT = 60

# =========================================================
# 🟢 OLLAMA SETTINGS (LOCAL OFFLINE SECURE ROUTING)
# =========================================================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_TIMEOUT = 120

_last_local_call = 0.0


# =========================================================
# 🔵 GROQ API CALL
# =========================================================
def call_groq(prompt: str, temperature: float = 0.2, max_tokens: int = 800) -> str | None:
    """Invokes the Groq cloud endpoint for inference.
    
    Args:
        prompt (str): Text prompt to run analysis on.
        temperature (float): Controls sampling randomness (default: 0.2).
        max_tokens (int): Maximum output tokens (default: 800).
        
    Returns:
        str | None: Decoded inference text on success, or None on failure.
    """
    if not GROQ_API_KEY:
        logger.warning("❌ GROQ API key missing in environment variables.")
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
            logger.warning(f"GROQ returned status code {r.status_code}: {r.text}")
            return None

        data = r.json()

        if "choices" not in data:
            logger.warning(f"GROQ invalid response payload: {data}")
            return None

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logger.error(f"GROQ connection failed: {e}")
        return None


# =========================================================
# 🟢 OLLAMA LOCAL CALL
# =========================================================
def call_ollama(prompt: str) -> str | None:
    """Invokes local secure offline model using Ollama REST API.
    
    Args:
        prompt (str): Text prompt to run offline analysis on.
        
    Returns:
        str | None: Offline inference response on success, or None on failure.
    """
    global _last_local_call

    if not prompt:
        return None

    # Throttling to prevent overloading the local system
    elapsed = time.time() - _last_local_call
    if elapsed < 1.2:
        time.sleep(1.2 - elapsed)

    _last_local_call = time.time()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt[:2000],  # Clamp prompt to fit typical small local contexts
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )

        if r.status_code != 200:
            logger.warning(f"Ollama local service returned status code {r.status_code}")
            return None

        return r.json().get("response", "").strip()

    except Exception as e:
        logger.warning(f"Ollama local connection failed: {e}")
        return None


# =========================================================
# 🧠 MASTER HYBRID ROUTER
# =========================================================
def call_hybrid_llm(prompt: str, role: str = "analysis") -> str:
    """Routes prompt to the best available LLM provider using an active fallback strategy.
    
    Args:
        prompt (str): Text prompt to route and execute.
        role (str): Contextual role ("analysis", "summary", "report").
        
    Returns:
        str: Analyzed response text from either cloud, local, or static fallback.
    """
    if not prompt or not prompt.strip():
        return "No prompt provided"

    # 1️⃣ TRY GROQ (PRIMARY CLOUD INSTANCE)
    groq_response = call_groq(prompt)
    if groq_response and len(groq_response) > 5:
        return groq_response

    logger.warning("⚠ Groq cloud inference failed or is unavailable → routing to local Ollama.")

    # 2️⃣ TRY OLLAMA (SECURE OFFLINE FALLBACK)
    local_response = call_ollama(prompt)
    if local_response and len(local_response) > 5:
        return local_response

    # 3️⃣ FINAL SECURE FALLBACK
    logger.error("❌ Groq cloud and local Ollama both failed. Executing deterministic fallback.")

    if role in ["summary", "report"]:
        return "Final report summary is currently unavailable. Please check backend LLM logs."

    return "Contract analysis context unavailable. Please review connection parameters and retry."
