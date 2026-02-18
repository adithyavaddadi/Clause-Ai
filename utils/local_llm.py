import os
import requests
import time
import logging

logger = logging.getLogger(__name__)

# ==============================
# OLLAMA SETTINGS
# ==============================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

TIMEOUT = 120
MAX_PROMPT = 1800

_last_call = 0


# =========================================================
# LOCAL LLM CALL (USED BY AGENTS)
# =========================================================
def call_local_llm(prompt: str) -> str:
    """
    Used for ALL AGENTS (legal, finance, compliance etc)
    Fast + safe + no crash
    """

    global _last_call

    if not prompt or not prompt.strip():
        return "No prompt provided"

    # ---- small delay to avoid overload ----
    if time.time() - _last_call < 1.2:
        time.sleep(1.2)

    _last_call = time.time()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt[:MAX_PROMPT],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            },
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            logger.warning(f"Ollama returned {response.status_code}")
            return "Local model unavailable. Please retry."

        text = response.json().get("response", "").strip()

        if not text:
            logger.warning("Ollama empty response")
            return "Model returned empty analysis."

        return text

    except requests.exceptions.ConnectionError:
        logger.error("Ollama not running")
        return "Local LLM not running. Start Ollama."

    except requests.exceptions.Timeout:
        logger.error("Ollama timeout")
        return "Local model timeout. Try smaller contract."

    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return "Local analysis failed. Retry."
