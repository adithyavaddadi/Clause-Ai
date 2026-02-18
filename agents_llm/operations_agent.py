"""
OPERATIONS AGENT — HYBRID (GROQ + Ollama fallback)
Detect execution & operational risks
"""

import logging
from utils.hybrid_llm import call_hybrid_llm   # use hybrid (NOT grok)

logger = logging.getLogger(__name__)


def operations_agent(clause: str):
    """
    Operations risk analysis
    GROQ → Ollama → fallback
    """

    if not clause:
        return "No operational risk identified."

    clause = str(clause).strip()

    if len(clause) < 15:
        return "Clause too short for operational analysis."

    try:
        prompt = f"""
You are an OPERATIONS RISK ANALYST AI.

Return ONLY one concise professional line.

Focus:
- timelines
- responsibilities
- execution risk
- dependencies

Max 25 words.
One line only.

CLAUSE:
{clause[:700]}
"""

        response = call_hybrid_llm(prompt)

        if not response:
            logger.warning("Operations agent → fallback")
            return _operations_fallback(clause)

        response = response.strip().split("\n")[0]

        if len(response) > 200:
            response = response[:200]

        return response

    except Exception as e:
        logger.error(f"Operations agent error: {str(e)}")
        return _operations_fallback(clause)


# ---------------- LOCAL FALLBACK ----------------
def _operations_fallback(clause: str):

    text = clause.lower()

    if "delay" in text or "timeline" in text or "delivery" in text:
        return "Timeline dependency may create delivery or execution risk."

    if "responsibility" in text or "party shall" in text:
        return "Unclear responsibility allocation may cause operational disputes."

    if "approval" in text or "consent" in text:
        return "Approval dependency may delay execution."

    if "dependency" in text or "third party" in text:
        return "Third-party dependency may create execution risk."

    return "Operational responsibilities and timelines should be clearly defined."
