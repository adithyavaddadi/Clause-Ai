"""
Final report helper utilities
Used for dashboard, summary and agent formatting
"""

import re
from typing import Tuple, Dict, Any


# =========================================================
# EXTRACT RISK LEVEL + %
# (used in dashboard meter)
# =========================================================
def extract_risk_metrics(report_text: str) -> Tuple[str, int]:
    """
    Extract risk level and percentage from final report text.
    Always returns safe values.
    """

    if not report_text or not isinstance(report_text, str):
        return "Medium", 50

    text = report_text.lower()

    # -------- risk level --------
    if "high risk" in text:
        level = "High"
    elif "low risk" in text:
        level = "Low"
    else:
        level = "Medium"

    # -------- risk percentage --------
    percent_match = re.search(r'(\d{1,3})\s*%', report_text)

    if percent_match:
        percent = int(percent_match.group(1))
        percent = max(0, min(percent, 100))
    else:
        defaults = {
            "High": 75,
            "Medium": 50,
            "Low": 25
        }
        percent = defaults[level]

    return level, percent


# =========================================================
# EXECUTIVE SUMMARY (TOP BOX IN UI)
# =========================================================
def create_executive_summary(legal: Dict, finance: Dict, compliance: Dict) -> str:
    """Generate executive summary for final report"""

    legal_risk = legal.get("risk_level", "Medium")
    finance_risk = finance.get("risk_level", "Medium")
    compliance_risk = compliance.get("risk_level", "Medium")

    summary = f"""
📊 EXECUTIVE SUMMARY

ClauseAI analyzed the contract using multiple AI agents.

Legal Risk: {legal_risk}
Financial Risk: {finance_risk}
Compliance Risk: {compliance_risk}

The contract contains potential legal, financial, and regulatory
risks that should be reviewed before final approval.

Recommendation:
Revise unclear clauses, strengthen liability protection,
and ensure compliance alignment before signing.
"""

    return summary.strip()


# =========================================================
# FORMAT EACH AGENT OUTPUT CLEANLY
# =========================================================
def format_agent_output(agent_name: str, agent_result: Dict[str, Any]) -> str:
    """Format agent output for final report"""

    if not isinstance(agent_result, dict):
        return f"{agent_name} agent returned invalid data."

    risk = agent_result.get("risk_level", "UNKNOWN")
    issues = agent_result.get("issues", [])
    missing = agent_result.get("missing_clauses", [])
    insight = agent_result.get("insight", "")

    text = f"\n🤖 {agent_name.upper()} AGENT\n"
    text += f"Risk Level: {risk}\n"

    if issues:
        text += "\nCritical Issues:\n"
        for i in issues:
            text += f"• {i}\n"

    if missing:
        text += "\nMissing/Weak Clauses:\n"
        for m in missing:
            text += f"• {m}\n"

    if insight:
        text += f"\nInsight:\n{insight}\n"

    return text.strip()
