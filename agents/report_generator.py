"""
Report Generator Agent
Creates final contract analysis report from all agents
Clean + simple + precise
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates final readable contract report
    """

    def generate_report(
        self,
        contract_type: str,
        legal_analysis: str = "",
        compliance_analysis: str = "",
        finance_analysis: str = "",
        clause_analyses: List[Dict] | None = None,
        user_focus: str = ""
    ) -> str:

        try:
            risk_level = self._detect_risk_level(
                legal_analysis, compliance_analysis, finance_analysis
            )

            clauses_text = self._format_clause_analyses(clause_analyses)

            report = f"""
====================================
FINAL CONTRACT INTELLIGENCE REPORT
====================================

Contract Type: {contract_type}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

------------------------------------
OVERALL RISK LEVEL: {risk_level}
------------------------------------

LEGAL ANALYSIS:
{legal_analysis or "No legal risks detected."}

------------------------------------

FINANCIAL ANALYSIS:
{finance_analysis or "No financial risks detected."}

------------------------------------

COMPLIANCE ANALYSIS:
{compliance_analysis or "No compliance risks detected."}

------------------------------------

CLAUSE RISK ANALYSIS:
{clauses_text}

------------------------------------

FINAL DECISION:
{self._final_decision(risk_level)}

====================================
End of Report
====================================
"""
            return report.strip()

        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return self._fallback_report(contract_type)

    # --------------------------------------------------
    # Detect risk from agents
    # --------------------------------------------------
    def _detect_risk_level(self, legal: str, compliance: str, finance: str) -> str:

        combined = f"{legal} {compliance} {finance}".lower()

        if "high" in combined:
            return "HIGH"
        if "medium" in combined:
            return "MEDIUM"
        return "LOW"

    # --------------------------------------------------
    # Clause formatting
    # --------------------------------------------------
    def _format_clause_analyses(self, clause_analyses: List[Dict] | None) -> str:

        if not clause_analyses:
            return "No clause analysis available."

        lines = []
        for i, c in enumerate(clause_analyses[:5], 1):
            ctype = c.get("clause_type", "general")
            score = c.get("risk_score", 50)
            issues = ", ".join(c.get("issues", []))

            lines.append(f"{i}. {ctype} clause → Risk {score}%")
            if issues:
                lines.append(f"   Issues: {issues}")

        return "\n".join(lines)

    # --------------------------------------------------
    # Final decision
    # --------------------------------------------------
    def _final_decision(self, risk: str) -> str:

        if risk == "HIGH":
            return "⚠ HIGH RISK — Legal review required before signing."
        if risk == "MEDIUM":
            return "⚠ REVIEW ADVISED — Some risks detected."
        return "✓ SAFE — Contract appears acceptable."

    # --------------------------------------------------
    # fallback
    # --------------------------------------------------
    def _fallback_report(self, contract_type: str) -> str:
        return f"""
Contract Report
Type: {contract_type}

Basic analysis completed.
Detailed report unavailable due to system issue.
"""


# --------------------------------------------------
# SIMPLE FUNCTION CALL
# --------------------------------------------------
def generate_contract_report(
    contract_type: str,
    legal_analysis: str = "",
    compliance_analysis: str = "",
    finance_analysis: str = "",
    clause_analyses: List[Dict] | None = None,
    user_focus: str = ""
) -> str:

    generator = ReportGenerator()
    return generator.generate_report(
        contract_type,
        legal_analysis,
        compliance_analysis,
        finance_analysis,
        clause_analyses,
        user_focus,
    )
