"""
Risk scoring utilities for ClauseAI (PRODUCTION VERSION)
Used by:
- final_report.py
- executor_agent.py
- Heuristic fallback managers
"""

import re
from typing import Dict, List, Tuple

# =========================================================
# KEYWORDS & SIGNALS CONFIGURATION
# =========================================================
HIGH_RISK_KEYWORDS = [
    "unlimited liability",
    "unlimited indemn",
    "perpetual",
    "irrevocable",
    "liquidated damages",
    "sole discretion",
    "waive",
]

MEDIUM_RISK_KEYWORDS = [
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

PROTECTIVE_KEYWORDS = [
    "liability cap",
    "limited liability",
    "governing law",
    "arbitration",
    "notice period",
    "data protection",
    "encrypted",
    "backup",
]


# =========================================================
# MAIN RISK SCORE CALCULATOR
# =========================================================
def calculate_risk_score(contract_text: str, analysis_results: Dict | None = None) -> Tuple[str, int]:
    """Calculates a deterministic contract risk rating based on semantic token matches.
    
    Args:
        contract_text (str): Raw contract text corpus.
        analysis_results (Dict | None): Optional agent outputs.
        
    Returns:
        Tuple[str, int]: The risk level classification ("Low", "Medium", "High") and the numerical score (5–100).
    """
    if not contract_text or not isinstance(contract_text, str):
        return "Low", 25

    text_lower = contract_text.lower()
    score = 35  # Base score for balanced agreements

    # Apply scoring weights based on keywords
    for word in HIGH_RISK_KEYWORDS:
        if _contains_term(text_lower, word):
            score += 15

    for word in MEDIUM_RISK_KEYWORDS:
        if _contains_term(text_lower, word):
            score += 6

    for word in PROTECTIVE_KEYWORDS:
        if _contains_term(text_lower, word):
            score -= 5

    # Clamp the final risk rating
    score = max(5, min(score, 100))

    # Determine risk category boundaries
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
    """Extracts key risk signals and outputs their severity levels.
    
    Args:
        contract_text (str): Contract text corpus.
        
    Returns:
        List[Dict[str, str]]: Array of matched risk factors.
    """
    if not contract_text or not isinstance(contract_text, str):
        return []

    text = contract_text.lower()
    factors: List[Dict[str, str]] = []

    # Map patterns to their description and severity levels
    patterns = [
        (r"unlimited\s+liability", "High", "Unlimited liability exposure detected"),
        (r"indemnif", "High", "Active indemnification obligation"),
        (r"liquidated\s+damages", "Medium", "Liquidated damages enforcement clause"),
        (r"penalty", "Medium", "Monetary penalty clause"),
        (r"sole\s+discretion", "Medium", "Unilateral sole discretion clause"),
        (r"perpetual", "High", "Perpetual duration obligation"),
        (r"auto.?renew", "Medium", "Automatic auto-renewal clause"),
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
def compare_risk_scores(text1: str, text2: str) -> Dict[str, Dict[str, str | int] | int | str]:
    """Compares risk profiles between two contracts.
    
    Args:
        text1 (str): First contract text corpus.
        text2 (str): Second contract text corpus.
        
    Returns:
        Dict: Structured comparison results.
    """
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
    """Verifies existence of keyword while avoiding semantic negations.
    
    Example:
        'no unlimited liability' will NOT trigger a match.
        
    Args:
        text_lower (str): Lowercase contract text corpus.
        keyword (str): The keyword token to search.
        
    Returns:
        bool: True if matched without any negations, False otherwise.
    """
    if not text_lower:
        return False

    pattern = re.escape(keyword)

    for match in re.finditer(pattern, text_lower):
        start = max(0, match.start() - 25)
        prefix = text_lower[start:match.start()]

        # Ignore occurrence if negated within pre-existing 25-character boundary
        if any(neg in prefix for neg in ["no ", "not ", "without ", "absence of "]):
            continue

        return True

    return False


# =========================================================
# LOCAL VERIFICATION RUNNER
# =========================================================
if __name__ == "__main__":
    test_context = """
    This agreement includes unlimited liability and indemnity.
    Liquidated damages apply.
    Governing law is India.
    """

    level, calculated_score = calculate_risk_score(test_context)
    print("Risk Level:", level)
    print("Risk Score:", calculated_score)

    print("\nRisk Factors:")
    for f in extract_risk_factors(test_context):
        print("-", f["description"])
