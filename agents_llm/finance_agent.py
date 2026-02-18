"""
Finance Agent — HYBRID (GROQ + Ollama fallback)
Working stable version
"""

import logging
import re
from utils.hybrid_llm import call_hybrid_llm   # use hybrid (NOT grok)

logger = logging.getLogger(__name__)


def finance_agent(contract_text, contract_type=None, user_focus="", memory_context=""):

    if not contract_text:
        return "No financial content found."

    text = str(contract_text).strip()
    if len(text) < 15:
        return "Contract too short for financial analysis."

    contract_type_text = contract_type or "General"
    user_focus_text = user_focus or "Financial risk"

    try:
        prompt = f"""
You are a SENIOR CONTRACT FINANCIAL ANALYST AI.

Return STRICT structured output:

FINANCIAL RISK LEVEL: Low/Medium/High

PAYMENT TERMS:
- point
- point

PENALTIES/LOSSES:
- point
- point

FINANCIAL EXPOSURE:
Low/Medium/High with reason

FINAL VERDICT:
One strong professional line.

Max 120 words.

Contract Type: {contract_type_text}
User Focus: {user_focus_text}

CONTRACT:
{text[:900]}
"""

        response = call_hybrid_llm(prompt)

        if not response:
            logger.warning("Finance agent → fallback")
            return _finance_fallback(text)

        return response.strip()

    except Exception as e:
        logger.error(f"Finance agent error: {str(e)}")
        return _finance_fallback(text)


# ---------------- LOCAL FALLBACK ----------------
def _finance_fallback(text: str) -> str:

    lower = text.lower()

    payment = (
        "Payment terms detected."
        if "payment" in lower or "invoice" in lower
        else "Payment schedule unclear."
    )

    penalties = (
        "Penalty clauses present."
        if "penalty" in lower or "late fee" in lower
        else "Penalty terms missing."
    )

    liability = (
        "Liability cap present."
        if "liability" in lower
        else "No clear liability cap."
    )

    renewal = (
        "Auto-renewal present."
        if "renewal" in lower
        else "No renewal clause."
    )

    amounts = _extract_currency(text)
    due = _extract_due(text)

    return f"""
FINANCIAL RISK LEVEL: Medium

PAYMENT TERMS:
- {payment}
- {due}
- {amounts}

PENALTIES/LOSSES:
- {penalties}
- Interest/late fee clarity needed

FINANCIAL EXPOSURE:
Medium — {liability}

FINAL VERDICT:
Contract contains financial structure but requires clearer liability and payment protections.
"""


def _extract_currency(text: str):
    matches = re.findall(r"(?:₹|\$|USD|INR)\s?[\d,]+", text)
    if matches:
        return f"Monetary values detected: {', '.join(matches[:3])}"
    return "No clear monetary value."


def _extract_due(text: str):
    match = re.search(r"(?:within|net)\s*(\d{1,3})\s*days", text.lower())
    if match:
        return f"Payment due within {match.group(1)} days."
    return "No clear payment due window."
