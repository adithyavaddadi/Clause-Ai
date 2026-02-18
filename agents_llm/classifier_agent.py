import logging
from utils.hybrid_llm import call_hybrid_llm   # use hybrid instead of grok

logger = logging.getLogger(__name__)

ALLOWED_CLASSES = [
    "Employment",
    "NDA",
    "Service Agreement",
    "Vendor",
    "Lease",
    "Partnership",
    "Healthcare",
    "Investor",
    "Distributor",
    "Dealer",
    "Other"
]


def classify_contract(contract_text: str) -> str:
    """
    HYBRID classifier:
    GROQ → Ollama → heuristic fallback
    """

    if not contract_text:
        return _heuristic_classify("")

    contract_text = str(contract_text).strip()

    if len(contract_text) < 15:
        return _heuristic_classify(contract_text)

    prompt = f"""
You are a contract classification AI.

Choose ONLY ONE category:

Employment
NDA
Service Agreement
Vendor
Lease
Partnership
Healthcare
Investor
Distributor
Dealer
Other

Return only category name.

CONTRACT:
{contract_text[:800]}
"""

    try:
        response = call_hybrid_llm(prompt)

        if not response:
            return _heuristic_classify(contract_text)

        response = response.strip().split("\n")[0].replace(".", "").strip()

        for label in ALLOWED_CLASSES:
            if response.lower() == label.lower():
                logger.info(f"[Classifier] Contract classified: {label}")
                return label

        return _heuristic_classify(contract_text)

    except Exception as e:
        logger.error(f"[Classifier] classification error: {str(e)}")
        return _heuristic_classify(contract_text)


# ---------------- HEURISTIC FALLBACK ----------------
def _heuristic_classify(text: str) -> str:

    text_l = (text or "").lower()
    head = " ".join((text or "").splitlines()[:25]).lower()

    if "service agreement" in head:
        return "Service Agreement"
    if "employment agreement" in head:
        return "Employment"
    if "non-disclosure" in head or "nda" in head:
        return "NDA"
    if "investment" in head or "investor" in head:
        return "Investor"

    weighted_rules = {
        "Service Agreement": [("service", 5)],
        "Investor": [("investment", 6), ("equity", 5)],
        "NDA": [("confidential", 6)],
        "Employment": [("salary", 5), ("employee", 6)],
        "Lease": [("rent", 6), ("tenant", 5)],
        "Vendor": [("vendor", 6), ("supplier", 5)],
        "Partnership": [("partnership", 6)],
        "Healthcare": [("medical", 5)],
        "Distributor": [("distributor", 6)],
        "Dealer": [("dealer", 6)],
    }

    scores = {k: 0 for k in weighted_rules}

    for label, terms in weighted_rules.items():
        for term, weight in terms:
            if term in text_l:
                scores[label] += weight

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Other"
