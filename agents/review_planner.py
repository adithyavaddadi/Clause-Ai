"""
Review Planner Agent - Plans and organizes the contract review process.
"""

import logging
from typing import Dict, List, Any
from utils.hybrid_llm import call_hybrid_llm

logger = logging.getLogger(__name__)


class ReviewPlanner:
    """
    Plans and organizes contract review process.
    Creates checklist + priority plan.
    """

    def __init__(self):
        self.default_review_areas = [
            "Termination Rights",
            "Liability and Indemnification",
            "Payment Terms",
            "Confidentiality",
            "Intellectual Property",
            "Governing Law",
            "Dispute Resolution",
            "Force Majeure",
            "Assignment",
            "Amendments"
        ]

    # =========================================================
    # CREATE REVIEW PLAN
    # =========================================================
    def create_review_plan(
        self,
        contract_text: str,
        contract_type: str = "",
        user_focus: str = ""
    ) -> Dict[str, Any]:

        if not contract_text or not contract_text.strip():
            return self._default_plan()

        try:
            prompt = f"""
You are a CONTRACT REVIEW PLANNER AI.

Create a clear review plan.

Contract Type: {contract_type or "Unknown"}
User Focus: {user_focus or "General"}

Return STRICT JSON only:

{{
"priority_areas": [],
"review_checklist": [],
"recommended_agents": [],
"focus_questions": [],
"estimated_time": "",
"risk_hotspots": []
}}

Default review areas:
{", ".join(self.default_review_areas)}

CONTRACT:
{contract_text[:2000]}
"""

            response = call_hybrid_llm(prompt, role="agent")

            if not response:
                return self._default_plan()

            parsed = self._parse_json(response)
            if parsed:
                return parsed

        except Exception as e:
            logger.error(f"ReviewPlanner error: {e}")

        return self._default_plan()

    # =========================================================
    # PRIORITIZE CLAUSES
    # =========================================================
    def prioritize_clauses(self, clauses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        if not clauses:
            return []

        try:
            prompt = "Prioritize these clauses by risk. Return JSON array.\n"

            for i, c in enumerate(clauses[:10], 1):
                prompt += f"\n{i}. {c.get('type')} → {c.get('text')[:150]}"

            response = call_hybrid_llm(prompt, role="agent")
            parsed = self._parse_json_array(response)

            if parsed:
                return parsed

        except Exception as e:
            logger.error(f"Clause prioritization error: {e}")

        # fallback
        return [
            {
                "clause": c.get("text","")[:100],
                "type": c.get("type","general"),
                "priority": "medium",
                "reason": "Default priority"
            }
            for c in clauses
        ]

    # =========================================================
    # GENERATE QUESTIONS
    # =========================================================
    def generate_review_questions(self, contract_type: str, risk_areas: List[str]) -> List[str]:

        try:
            prompt = f"""
Generate 5 review questions for {contract_type} contract.
Risk areas: {", ".join(risk_areas[:5])}
Return JSON array only.
"""

            response = call_hybrid_llm(prompt, role="agent")
            parsed = self._parse_json_array(response)

            if parsed:
                return parsed

        except Exception as e:
            logger.error(f"Question generation error: {e}")

        return self._default_questions(contract_type)

    # =========================================================
    # DEFAULT PLAN
    # =========================================================
    def _default_plan(self) -> Dict[str, Any]:
        return {
            "priority_areas": self.default_review_areas[:5],
            "review_checklist": [f"Review {a}" for a in self.default_review_areas],
            "recommended_agents": ["legal", "finance", "compliance"],
            "focus_questions": self._default_questions("Contract"),
            "estimated_time": "30-60 minutes",
            "risk_hotspots": []
        }

    def _default_questions(self, contract_type: str) -> List[str]:
        return [
            f"What are termination rights in this {contract_type}?",
            "What is liability exposure?",
            "Are payment terms safe?",
            "Any legal risks present?",
            "Is jurisdiction clear?"
        ]

    # =========================================================
    # JSON PARSERS
    # =========================================================
    def _parse_json(self, text: str):
        try:
            import json
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end < 0:
                return None
            return json.loads(text[start:end+1])
        except:
            return None

    def _parse_json_array(self, text: str):
        try:
            import json
            start = text.find("[")
            end = text.rfind("]")
            if start < 0 or end < 0:
                return None
            return json.loads(text[start:end+1])
        except:
            return None


# =========================================================
# STANDALONE FUNCTION
# =========================================================
def create_review_plan(contract_text: str, contract_type: str = "", user_focus: str = "") -> Dict[str, Any]:
    planner = ReviewPlanner()
    return planner.create_review_plan(contract_text, contract_type, user_focus)
