"""
Heuristic-based contract risk analyzer (FINAL STABLE VERSION)
"""

import re
from typing import Dict, List, Any


class RiskHeuristic:
    def __init__(self):

        # ---------------- HIGH RISK ----------------
        self.high_risk_patterns = [
            (r"unlimited\s+liability", "Unlimited Liability", "High"),
            (r"unlimited\s+indemnif", "Unlimited Indemnity", "High"),
            (r"perpetual", "Perpetual Obligation", "High"),
            (r"irrevocable", "Irrevocable Commitment", "High"),
        ]

        # ---------------- MEDIUM ----------------
        self.medium_risk_patterns = [
            (r"penalty", "Penalty Clause", "Medium"),
            (r"liquidated\s+damages", "Liquidated Damages", "Medium"),
            (r"auto.?renew", "Auto Renewal", "Medium"),
            (r"termination\s+fee", "Termination Fee", "Medium"),
            (r"non.?compete", "Non Compete", "Medium"),
            (r"non.?solicit", "Non Solicitation", "Medium"),
        ]

        # ---------------- POSITIVE ----------------
        self.protective_patterns = [
            (r"mutual", "Mutual Terms"),
            (r"liability\s+cap", "Liability Cap"),
            (r"limit.*liability", "Liability Limited"),
            (r"notice\s+period", "Notice Period"),
            (r"governing\s+law", "Governing Law"),
            (r"dispute\s+resolution", "Dispute Resolution"),
        ]

    # =====================================================
    # CLAUSE ANALYSIS
    # =====================================================
    def analyze_clause(self, clause_text: str) -> Dict[str, Any]:

        result = {
            "risks": [],
            "protections": [],
            "risk_score": 0,
            "risk_level": "Low"
        }

        if not clause_text:
            return result

        text = clause_text.lower()

        # ---------- HIGH ----------
        for pattern, desc, severity in self.high_risk_patterns:
            if re.search(pattern, text):
                result["risks"].append(desc)
                result["risk_score"] += 25

        # ---------- MEDIUM ----------
        for pattern, desc, severity in self.medium_risk_patterns:
            if re.search(pattern, text):
                result["risks"].append(desc)
                result["risk_score"] += 12

        # ---------- PROTECTION ----------
        for pattern, desc in self.protective_patterns:
            if re.search(pattern, text):
                result["protections"].append(desc)
                result["risk_score"] -= 5

        # ---------- FINAL LEVEL ----------
        score = max(0, result["risk_score"])

        if score >= 40:
            level = "High"
        elif score >= 18:
            level = "Medium"
        else:
            level = "Low"

        result["risk_score"] = score
        result["risk_level"] = level
        return result

    # =====================================================
    # FULL CONTRACT ANALYSIS
    # =====================================================
    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:

        if not contract_text:
            return {
                "risk_level": "Low",
                "risk_score": 0,
                "risks": [],
                "protections": [],
            }

        clauses = re.split(r'[.;\n]', contract_text)

        total_score = 0
        all_risks: List[str] = []
        all_protect: List[str] = []

        valid_clauses = [c for c in clauses if len(c.strip()) > 25]

        for clause in valid_clauses:
            res = self.analyze_clause(clause)
            total_score += res["risk_score"]
            all_risks.extend(res["risks"])
            all_protect.extend(res["protections"])

        if not valid_clauses:
            avg_score = 0
        else:
            avg_score = total_score / len(valid_clauses)

        # ---------- LEVEL ----------
        if avg_score >= 40:
            level = "High"
        elif avg_score >= 18:
            level = "Medium"
        else:
            level = "Low"

        return {
            "risk_level": level,
            "risk_score": int(avg_score),
            "total_risks": len(all_risks),
            "protections": len(all_protect),
            "top_risks": list(set(all_risks))[:8],
            "positive_terms": list(set(all_protect))[:8],
        }

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================
    def get_recommendations(self, risk_result: Dict) -> List[str]:

        rec = []

        if risk_result["risk_level"] == "High":
            rec.append("High risk contract — legal review required before signing.")

        if "Unlimited Liability" in risk_result.get("top_risks", []):
            rec.append("Add liability cap to limit financial exposure.")

        if "Auto Renewal" in risk_result.get("top_risks", []):
            rec.append("Add manual renewal control.")

        if risk_result.get("protections", 0) > 3:
            rec.append("Contract includes some protective clauses.")

        if not rec:
            rec.append("No critical risks detected. Standard review recommended.")

        return rec


# =====================================================
# QUICK FUNCTION
# =====================================================
def analyze_contract_risk(contract_text: str) -> Dict[str, Any]:
    analyzer = RiskHeuristic()
    return analyzer.analyze_contract(contract_text)
