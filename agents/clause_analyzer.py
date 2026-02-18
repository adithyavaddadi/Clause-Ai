"""
Clause Analyzer Agent — HYBRID (GROQ + Ollama fallback)
FINAL WORKING VERSION
"""

from __future__ import annotations
import json
import logging
import re
from typing import Any, Dict, List

from utils.hybrid_llm import call_hybrid_llm   # use hybrid NOT grok

logger = logging.getLogger(__name__)


class ClauseAnalyzer:

    def analyze_clause(self, clause_text: str | None, clause_type: str = "general") -> Dict[str, Any]:

        if not clause_text or not clause_text.strip():
            return self._default_response(clause_type, 0, ["No clause text provided"])

        try:
            prompt = f"""
You are a CONTRACT CLAUSE RISK ANALYZER.

Return STRICT JSON:

{{
"risk_score": 0-100,
"risk_level": "Low/Medium/High",
"issues": ["short issue"],
"fix": ["clear improvement"],
"red_flags": ["high risk warning"]
}}

Clause Type: {clause_type}

Clause:
{clause_text[:1200]}
"""

            response = call_hybrid_llm(prompt)

            parsed = self._parse_json_safe(response)

            if parsed:
                return {
                    "clause_type": clause_type,
                    "risk_score": self._to_score(parsed.get("risk_score")),
                    "risk_level": parsed.get("risk_level", "Medium"),
                    "issues": self._to_list(parsed.get("issues")),
                    "fix": self._to_list(parsed.get("fix")),
                    "red_flags": self._to_list(parsed.get("red_flags")),
                }

        except Exception as exc:
            logger.error(f"Clause analysis failed: {exc}")

        return self._default_response(clause_type)

    # =========================================================
    def analyze_clauses(self, clauses: List[Dict[str, str]] | None) -> List[Dict[str, Any]]:
        if not clauses:
            return []

        results = []
        for clause in clauses:
            text = clause.get("text", "")
            ctype = clause.get("type", "general")
            results.append(self.analyze_clause(text, ctype))

        return results

    # =========================================================
    def extract_clauses(self, contract_text: str | None) -> List[Dict[str, str]]:
        if not contract_text:
            return []

        try:
            prompt = f"""
Extract key clauses from contract.

Return JSON array:
[{{"type":"termination","text":"clause"}}]

Contract:
{contract_text[:3000]}
"""

            response = call_hybrid_llm(prompt)

            parsed = self._parse_json_array_safe(response)

            cleaned = []

            if parsed and isinstance(parsed, list):
                for item in parsed:
                    if not isinstance(item, dict):
                        continue

                    cleaned.append({
                        "type": str(item.get("type", "general")).strip(),
                        "text": str(item.get("text", "")).strip()
                    })

            return cleaned

        except Exception as exc:
            logger.error(f"Clause extraction failed: {exc}")

        return []

    # =========================================================
    def _default_response(self, clause_type: str, risk_score: int = 50, findings: List[str] | None = None):

        return {
            "clause_type": clause_type,
            "risk_score": risk_score,
            "risk_level": "Medium",
            "issues": findings if findings else ["Manual review needed"],
            "fix": ["Add clearer legal protection"],
            "red_flags": []
        }

    # =========================================================
    def _parse_json_safe(self, text: str):
        if not text:
            return None
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                return None
            return json.loads(match.group(0))
        except:
            return None

    def _parse_json_array_safe(self, text: str):
        if not text:
            return None
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if not match:
                return None
            return json.loads(match.group(0))
        except:
            return None

    @staticmethod
    def _to_list(value: Any):
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]
        if value:
            return [str(value).strip()]
        return []

    @staticmethod
    def _to_score(value: Any):
        try:
            v = int(value)
            return max(0, min(100, v))
        except:
            return 50


def analyze_clause(clause_text: str, clause_type: str = "general"):
    analyzer = ClauseAnalyzer()
    return analyzer.analyze_clause(clause_text, clause_type)
