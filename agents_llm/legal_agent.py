"""
LEGAL AGENT — HYBRID (GROQ + Ollama fallback)
Stable working version
"""

import logging
import re
from utils.hybrid_llm import call_hybrid_llm   # use hybrid (NOT grok)

logger = logging.getLogger(__name__)


def legal_agent(contract_text, contract_type=None, user_focus="", memory_context=""):

    if not contract_text:
        return "No contract text provided for legal analysis."

    text = str(contract_text).strip()

    if len(text) < 20:
        return "Contract too short for legal analysis."

    try:
        prompt = f"""
You are an ELITE CORPORATE LAWYER AI.

Return STRICT structured output:

LEGAL RISK LEVEL: Low/Medium/High

CRITICAL LEGAL RISKS:
- point
- point

MISSING OR WEAK CLAUSES:
- termination clarity
- liability cap
- indemnity
- jurisdiction

LIABILITY & TERMINATION INSIGHT:
1–2 short lines

FINAL LEGAL VERDICT:
One strong decision line.

Max 120 words.

Contract Type: {contract_type or "General"}
User Focus: {user_focus or "Legal risk"}

CONTRACT:
{text[:900]}
"""

        response = call_hybrid_llm(prompt)

        if not response:
            logger.warning("Legal agent → fallback")
            return _legal_fallback(text)

        return response.strip()

    except Exception as e:
        logger.error(f"Legal agent error: {str(e)}")
        return _legal_fallback(text)


# ---------------- LOCAL FALLBACK ----------------
def _legal_fallback(contract_text: str):

    text = contract_text.lower()

    has_termination = "termination" in text
    has_liability = "liability" in text
    has_indemnity = "indemn" in text
    has_jurisdiction = "jurisdiction" in text or "governing law" in text

    risk = "Low"
    if not has_liability or not has_termination:
        risk = "Medium"
    if not has_indemnity:
        risk = "High"

    notice = _extract_notice_period(contract_text)
    law = _extract_governing_law(contract_text)

    return f"""
LEGAL RISK LEVEL: {risk}

CRITICAL LEGAL RISKS:
- {notice}
- {law}

MISSING OR WEAK CLAUSES:
- Liability cap unclear
- Indemnity protection weak
- Jurisdiction clarity needed

LIABILITY & TERMINATION INSIGHT:
Contract contains basic structure but may expose one party to legal risk.

FINAL LEGAL VERDICT:
Legal review recommended before signing.
"""


def _extract_notice_period(contract_text: str):
    match = re.search(r"(\\d{{1,3}})\\s*days?\\s*(written)?\\s*notice", contract_text or "", re.I)
    if match:
        return f"Termination notice appears {match.group(1)} days."
    return "Termination notice not clearly defined."


def _extract_governing_law(contract_text: str):

    text = contract_text.lower()

    if "indian contract act" in text:
        return "Governed by Indian Contract Act."

    match = re.search(r"governed by ([a-zA-Z\\s]+)", text)
    if match:
        return f"Governing law appears {match.group(1).strip()}."

    return "Governing law not clearly mentioned."
