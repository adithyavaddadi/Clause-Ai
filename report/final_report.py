import logging
import os
import re
from typing import Dict

from utils.hybrid_llm import call_hybrid_llm
from utils.risk_score import calculate_risk_score
from utils.risk_formatter import create_executive_summary

logger = logging.getLogger(__name__)


# =========================================================
# MAIN FINAL REPORT
# =========================================================
def generate_final_report(
    contract_type: str,
    legal: str,
    finance: str,
    compliance: str,
    operations: str = "",
    user_focus: str = ""
) -> str:

    try:
        logger.info("Generating final executive report")

        contract_type = contract_type or "Contract"
        legal = legal or ""
        finance = finance or ""
        compliance = compliance or ""
        operations = operations or ""
        user_focus = user_focus or "General review"

        # =====================================================
        # PROMPT FOR GROK
        # =====================================================
        prompt = f"""
You are a WORLD-CLASS CONTRACT ANALYSIS AI.

Create a PROFESSIONAL FINAL CONTRACT REPORT.

Keep output CLEAR + SIMPLE + PRECISE.

FORMAT:

FINAL CONTRACT INTELLIGENCE REPORT

1. Contract Overview (2 lines)
2. Key Obligations
3. Legal Risks
4. Financial Risks
5. Compliance Risks
6. Overall Risk (Level + %)
7. Final Recommendation

INPUT:

Contract Type: {contract_type}

LEGAL:
{legal}

FINANCE:
{finance}

COMPLIANCE:
{compliance}

OPERATIONS:
{operations}

USER FOCUS:
{user_focus}
"""

        # Skip LLM if env forced
        if os.getenv("CLAUSEAI_SKIP_SUMMARY_LLM") == "1":
            return _fallback_report(contract_type, legal, finance, compliance)

        response = call_hybrid_llm(prompt, role="summary")

        if not response or "unavailable" in response.lower():
            logger.warning("LLM failed → fallback report")
            return _fallback_report(contract_type, legal, finance, compliance)

        return response.strip()

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return _fallback_report(contract_type, legal, finance, compliance)


# =========================================================
# FALLBACK REPORT (100% SAFE)
# =========================================================
def _fallback_report(contract_type: str, legal: str, finance: str, compliance: str) -> str:

    combined = f"{legal}\n{finance}\n{compliance}"

    risk_level, risk_pct = calculate_risk_score(combined)

    summary = create_executive_summary(
        contract_type=contract_type,
        risk_level=risk_level,
        agent_outputs={
            "Legal": legal,
            "Finance": finance,
            "Compliance": compliance
        }
    )

    return f"""
====================================
FINAL CONTRACT INTELLIGENCE REPORT
====================================

Contract Type: {contract_type}

OVERALL RISK LEVEL: {risk_level} ({risk_pct}%)

------------------------------------
EXECUTIVE SUMMARY:
{summary}

------------------------------------
LEGAL:
{_clean(legal)}

------------------------------------
FINANCE:
{_clean(finance)}

------------------------------------
COMPLIANCE:
{_clean(compliance)}

------------------------------------
FINAL DECISION:
Review recommended before signing.

====================================
""".strip()


# =========================================================
# CLEAN TEXT
# =========================================================
def _clean(text: str) -> str:
    if not text:
        return "No issues detected."

    lines = []
    for l in text.splitlines():
        c = re.sub(r"^[\-\*\•\s]+", "", l).strip()
        if c:
            lines.append(c)

    return "\n".join(lines[:6])
