import logging
import re
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# =========================================================
# RISK METRIC EXTRACTOR
# =========================================================
def extract_risk_metrics(report_text: str) -> Tuple[str, int]:
    """
    Extract risk level + risk percentage from report text.
    Always returns safe values.
    """

    if not report_text or not isinstance(report_text, str):
        return "Low", 25

    try:
        text_lower = report_text.lower()

        # ---------------- RISK LEVEL DETECTION ----------------
        if any(k in text_lower for k in ["high risk", "risk: high", "risk level: high"]):
            level = "High"
        elif any(k in text_lower for k in ["medium risk", "risk: medium", "risk level: medium"]):
            level = "Medium"
        elif any(k in text_lower for k in ["low risk", "risk: low", "risk level: low"]):
            level = "Low"
        else:
            level = "Medium"

        # ---------------- PERCENTAGE DETECTION ----------------
        percent_match = re.search(r'(\d{1,3})\s*%', report_text)

        if percent_match:
            percent = int(percent_match.group(1))
            percent = max(0, min(percent, 100))
        else:
            defaults = {"High": 75, "Medium": 50, "Low": 25}
            percent = defaults.get(level, 50)

        return level, percent

    except Exception as e:
        logger.error(f"Risk extraction failed: {e}")
        return "Low", 25


# =========================================================
# CLEAN AGENT OUTPUT FORMATTER
# =========================================================
def format_agent_output(agent_name: str, output: str, max_len: int = 700) -> str:
    """
    Clean + normalize agent output for UI/report.
    Prevent messy LLM output from breaking UI.
    """

    if not output:
        return f"{agent_name}: No analysis available."

    text = str(output).strip()

    # remove fallback markers
    text = text.replace("[HEURISTIC_FALLBACK]", "").strip()

    # model failure handling
    if text.lower().startswith("error") or "model unavailable" in text.lower():
        return f"{agent_name}: Model unavailable → fallback used."

    # trim long output
    if len(text) > max_len:
        text = text[:max_len].rstrip() + "..."

    return f"{agent_name}:\n{text}"


# =========================================================
# EXECUTIVE SUMMARY (SAFE FALLBACK)
# =========================================================
def create_executive_summary(
    contract_type: str,
    risk_level: str,
    agent_outputs: Dict[str, str]
) -> str:
    """
    Used if LLM summary fails.
    Generates professional deterministic summary.
    """

    contract = contract_type or "Contract"
    risk = risk_level or "Medium"

    active_agents = [
        name for name, value in (agent_outputs or {}).items()
        if value and isinstance(value, str) and value.strip()
    ]

    sources = ", ".join(active_agents) if active_agents else "AI analysis"

    return (
        f"This {contract} has been assessed as {risk} risk based on analysis from {sources}. "
        f"Key legal exposure, financial obligations, compliance requirements, and operational terms "
        f"should be carefully reviewed before signing or approval."
    )
