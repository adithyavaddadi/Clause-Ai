"""
Compliance Agent — HYBRID (GROQ + Ollama)
Stable working version
"""

import logging
import re
from utils.hybrid_llm import call_hybrid_llm   # use hybrid (NOT grok)

logger = logging.getLogger(__name__)


def compliance_agent(contract_text: str, contract_type: str, user_focus: str, memory_context: str = ""):
    """
    Hybrid compliance agent
    GROQ → Ollama → fallback
    """

    if not contract_text:
        return "No compliance content found."

    contract_text = str(contract_text).strip()

    if len(contract_text) < 15:
        return "Contract too short for compliance analysis."

    try:
        prompt = f"""
You are a GLOBAL CONTRACT COMPLIANCE AI.

Return STRICT structured output:

COMPLIANCE RISK LEVEL: Low/Medium/High

DATA PRIVACY ISSUES:
- point
- point

REGULATORY RISKS:
- point
- point

MISSING COMPLIANCE:
- audit clause
- security clause
- jurisdiction

FINAL VERDICT:
One professional line.

Max 120 words.

Contract Type: {contract_type}
User Focus: {user_focus}

CONTRACT:
{contract_text[:900]}
"""

        response = call_hybrid_llm(prompt)

        if not response:
            logger.warning("LLM empty → fallback")
            return _compliance_fallback(contract_text)

        return response.strip()

    except Exception as e:
        logger.error(f"Compliance agent error: {str(e)}")
        return _compliance_fallback(contract_text)


# ---------------- LOCAL FALLBACK ----------------
def _compliance_fallback(contract_text: str) -> str:

    text = contract_text.lower()

    privacy = (
        "Data protection clause present."
        if any(k in text for k in ["data", "privacy", "gdpr", "personal information"])
        else "No strong data protection clause."
    )

    regulatory = (
        "Regulatory references detected."
        if any(k in text for k in ["law", "compliance", "gst", "indian contract act"])
        else "Regulatory clarity missing."
    )

    audit = "Audit clause present." if "audit" in text else "Audit clause missing."

    breach = _extract_breach_window(contract_text)
    retention = _extract_retention_period(contract_text)

    return f"""
COMPLIANCE RISK LEVEL: Medium

DATA PRIVACY ISSUES:
- {privacy}
- {breach}

REGULATORY RISKS:
- {regulatory}
- Jurisdiction clarity needed

MISSING COMPLIANCE:
- {audit}
- Security standards missing
- {retention}

FINAL VERDICT:
Contract contains basic compliance but needs stronger regulatory clarity.
"""


def _extract_breach_window(contract_text: str) -> str:
    match = re.search(
        r"(?:notify|notification).{{0,40}}(\d{{1,3}})\s+days?",
        contract_text or "",
        flags=re.I | re.S,
    )
    if match:
        return f"Breach notice: {match.group(1)} days."
    return "No breach notification timeline."


def _extract_retention_period(contract_text: str) -> str:
    match = re.search(
        r"(?:retain|retention).{{0,40}}(\d{{1,3}})\s+(?:years?|months?)",
        contract_text or "",
        flags=re.I | re.S,
    )
    if match:
        return f"Retention defined: {match.group(1)}."
    return "No retention period defined."
