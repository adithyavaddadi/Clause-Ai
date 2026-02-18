"""
CLAUSE AI — TOKEN GUARD + COST ESTIMATOR
Works for:
✔ Groq (cloud)
✔ Ollama (local fallback)
✔ Prevents overload
✔ Smart routing
"""

import tiktoken
import logging

logger = logging.getLogger(__name__)

# =========================================================
# SETTINGS
# =========================================================
MAX_GROQ_TOKENS = 3500      # if prompt too big → use Ollama
MAX_SAFE_TOKENS = 6000      # beyond this = trim text
MODEL_NAME = "llama3"       # tokenizer reference

# cost approx for Groq (very cheap)
COST_PER_1K = 0.0002


# =========================================================
# TOKEN COUNTER
# =========================================================
def count_tokens(text: str, model: str = MODEL_NAME) -> int:
    """Count tokens safely"""

    if not text:
        return 0

    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")

    return len(enc.encode(text))


# =========================================================
# COST ESTIMATE
# =========================================================
def estimate_cost(tokens: int) -> float:
    return round((tokens / 1000) * COST_PER_1K, 6)


# =========================================================
# SMART TRIMMER
# =========================================================
def trim_prompt(prompt: str, max_tokens: int = MAX_SAFE_TOKENS) -> str:
    """Trim huge contracts automatically"""

    tokens = count_tokens(prompt)

    if tokens <= max_tokens:
        return prompt

    logger.warning(f"Prompt too large ({tokens}) → trimming")

    # rough trim
    chars = int(len(prompt) * (max_tokens / tokens))
    return prompt[:chars]


# =========================================================
# MAIN GUARD
# =========================================================
def token_guard(prompt: str) -> dict:
    """
    Decide:
    → use groq
    → use ollama
    → trim text
    """

    if not prompt:
        return {"use_groq": False, "tokens": 0, "cost": 0}

    tokens = count_tokens(prompt)
    cost = estimate_cost(tokens)

    logger.info(f"Tokens: {tokens} | Cost est: ${cost}")

    # too huge → trim first
    if tokens > MAX_SAFE_TOKENS:
        prompt = trim_prompt(prompt)
        tokens = count_tokens(prompt)

    # large → use ollama
    if tokens > MAX_GROQ_TOKENS:
        logger.warning("Large prompt → using Ollama")
        return {
            "use_groq": False,
            "tokens": tokens,
            "cost": cost,
            "prompt": prompt
        }

    # safe for groq
    return {
        "use_groq": True,
        "tokens": tokens,
        "cost": cost,
        "prompt": prompt
    }


# =========================================================
# DEBUG TEST
# =========================================================
if __name__ == "__main__":
    text = "This is a contract " * 500

    result = token_guard(text)

    print("\nTOKEN INFO")
    print(result)
