"""
Contract Classifier Agent — HYBRID (GROQ + Ollama fallback)
FINAL WORKING VERSION
"""

from __future__ import annotations
import json
import logging
from typing import Any, Dict
from utils.hybrid_llm import call_hybrid_llm   # use hybrid NOT grok

logger = logging.getLogger(__name__)


class ContractClassifier:

    PRIMARY_CATEGORIES = [
        "Employment","NDA","Service Agreement","Vendor","Lease","Partnership",
        "Healthcare","Investor","Distributor","Dealer","License","SaaS",
        "Construction","Insurance","Other"
    ]

    INDUSTRIES = [
        "Technology","Healthcare","Finance","Legal","Real Estate",
        "Manufacturing","Retail","Education","Government","Non-Profit","Unknown"
    ]

    def __init__(self):
        self.categories = list(self.PRIMARY_CATEGORIES)
        self.industries = list(self.INDUSTRIES)
        self.cache: Dict[int, Dict[str, Any]] = {}

    # ---------------- MAIN ----------------
    def classify(self, contract_text: str | None) -> Dict[str, Any]:

        text = (contract_text or "").strip()

        if len(text) < 40:
            return self._default_response(self._heuristic_primary_category(text))

        key = hash(text[:800])
        if key in self.cache:
            return self.cache[key]

        try:
            prompt = f"""
Classify this contract.

Return STRICT JSON:

{{
"primary_category": "",
"industry": "",
"risk_level": "low/medium/high",
"complexity": "low/medium/high",
"summary": "one line purpose"
}}

Allowed primary_category: {", ".join(self.categories)}
Allowed industry: {", ".join(self.industries)}

Contract:
{text[:1400]}
"""

            response = call_hybrid_llm(prompt)
            result = self._extract_json(response) if response else None

            if result:
                self.cache[key] = result
                return result

        except Exception as exc:
            logger.error(f"Classification failed: {exc}")

        return self._default_response(self._heuristic_primary_category(text))

    # ---------------- SIMPLE ONLY TYPE ----------------
    def classify_simple(self, contract_text: str | None) -> str:
        return self.classify(contract_text).get("primary_category", "Other")

    # ---------------- JSON PARSE ----------------
    def _extract_json(self, text: str) -> Dict[str, Any] | None:
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end < 0:
                return None

            data = json.loads(text[start:end+1])

            primary = str(data.get("primary_category","Other")).strip()
            industry = str(data.get("industry","Unknown")).strip()

            if primary not in self.categories:
                primary = "Other"
            if industry not in self.industries:
                industry = "Unknown"

            return {
                "primary_category": primary,
                "industry": industry,
                "complexity": str(data.get("complexity","medium")).lower(),
                "risk_level": str(data.get("risk_level","medium")).lower(),
                "key_terms_summary": str(data.get("summary","")).strip()
            }

        except:
            return None

    # ---------------- HEURISTIC ----------------
    def _heuristic_primary_category(self, text: str) -> str:

        text_l = text.lower()
        head = " ".join(text.splitlines()[:20]).lower()

        if "service agreement" in head:
            return "Service Agreement"
        if "employment agreement" in head:
            return "Employment"
        if "non disclosure" in head or "nda" in head:
            return "NDA"
        if "lease agreement" in head:
            return "Lease"
        if "investment" in head:
            return "Investor"

        if "salary" in text_l or "employee" in text_l:
            return "Employment"
        if "rent" in text_l:
            return "Lease"
        if "confidential" in text_l:
            return "NDA"

        return "Other"

    # ---------------- DEFAULT ----------------
    def _default_response(self, primary="Other") -> Dict[str, Any]:
        return {
            "primary_category": primary,
            "industry": "Unknown",
            "complexity": "medium",
            "risk_level": "medium",
            "key_terms_summary": "Basic contract classification"
        }


def classify_contract(contract_text: str) -> str:
    return ContractClassifier().classify_simple(contract_text)
