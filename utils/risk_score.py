"""
Risk scoring utilities for ClauseAI (FINAL PRODUCTION VERSION)
Used by:
- final_report
- executor agent
- fallback mode
"""

import re
from typing import Dict, List, Tuple


# =========================================================
# MAIN RISK SCORE CALCULATOR
# =========================================================
def calculate_risk_score(contract_text: str, analysis_results: Dict = None) -> Tuple[str, int]:
    """
    Calculate overall contract risk score.

    Returns:
        (risk_level, risk_percentage)
    """

    if not contract_text or not isinstance(contract_text, str):
        return "Low", 25

    text_lower = contract_text.lower()
    score = 35  # balanced base score

    # ---------------- HIGH RISK ----------------
    high_risk_keywords = [
        "unlimited liability",
        "unlimited indemn",
        "perpetual",
        "irrevocable",
        "liquidated damages",
        "sole discretion",
        "waive",
    ]

    # ---------------- MEDIUM ----------------
    medium_risk_keywords = [
        "termination",
        "breach",
        "penalty",
        "interest",
        "indemnity",
        "confidential",
        "non-compete",
        "non solicitation",
        "assignment",
        "auto-renew",
    ]

    # ---------------- PROTECTION ----------------
    protective_keywords = [
        "liability cap",
        "limited liability",
        "governing law",
        "arbitration",
        "notice period",
        "data protection",
        "encrypted",
        "backup",
    ]

    # ---------- APPLY SCORING ----------
    for word in high_risk_keywords:
        if _contains_term(text_lower, word):
            score += 15

    for word in medium_risk_keywords:
        if _contains_term(text_lower, word):
            score += 6

    for word in protective_keywords:
        if _contains_term(text_lower, word):
            score -= 5

    # clamp score
    score = max(5, min(score, 100))

    # ---------- LEVEL ----------
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return level, int(score)


# =========================================================
# EXTRACT RISK FACTORS
# =========================================================
def extract_risk_factors(contract_text: str) -> List[Dict[str, str]]:
    """Extract key risk signals from contract"""

    if not contract_text or not isinstance(contract_text, str):
        return []

    text = contract_text.lower()
    factors: List[Dict[str, str]] = []

    patterns = [
        (r"unlimited\s+liability", "High", "Unlimited liability exposure"),
        (r"indemnif", "High", "Indemnification obligation"),
        (r"liquidated\s+damages", "Medium", "Liquidated damages clause"),
        (r"penalty", "Medium", "Penalty clause"),
        (r"sole\s+discretion", "Medium", "Sole discretion clause"),
        (r"perpetual", "High", "Perpetual obligation"),
        (r"auto.?renew", "Medium", "Auto renewal risk"),
    ]

    for pattern, severity, desc in patterns:
        if re.search(pattern, text):
            factors.append({
                "severity": severity,
                "description": desc
            })

    return factors[:10]


# =========================================================
# COMPARE TWO CONTRACTS
# =========================================================
def compare_risk_scores(text1: str, text2: str) -> Dict:
    """Compare risk between two contracts"""

    level1, score1 = calculate_risk_score(text1 or "")
    level2, score2 = calculate_risk_score(text2 or "")

    return {
        "contract1": {"level": level1, "score": score1},
        "contract2": {"level": level2, "score": score2},
        "difference": abs(score1 - score2),
        "higher_risk": "contract1" if score1 > score2 else "contract2",
    }


# =========================================================
# SAFE TERM DETECTOR
# =========================================================
def _contains_term(text_lower: str, keyword: str) -> bool:
    """
    Detect keyword but avoid negation:
    'no unlimited liability'
    'not auto-renew'
    """

    if not text_lower:
        return False

    pattern = re.escape(keyword)

    for match in re.finditer(pattern, text_lower):
        start = max(0, match.start() - 25)
        prefix = text_lower[start:match.start()]

        # avoid negation context
        if any(x in prefix for x in ["no ", "not ", "without ", "absence of "]):
            continue

        return True

    return False


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    test = """
    This agreement includes unlimited liability and indemnity.
    Liquidated damages apply.
    Governing law is India.
    """

    level, score = calculate_risk_score(test)
    print("Risk Level:", level)
    print("Risk Score:", score)

    print("\nRisk Factors:")
    for f in extract_risk_factors(test):
        print("-", f["description"])
