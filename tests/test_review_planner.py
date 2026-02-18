"""
Tests for Review Planner Agent
"""

import pytest
import sys
import os

# -------------------------------------------------------
# ADD PROJECT ROOT
# -------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# -------------------------------------------------------
# SAFE IMPORT
# -------------------------------------------------------
try:
    from agents.review_planner import ReviewPlanner, create_review_plan
    PLANNER_AVAILABLE = True
except Exception:
    PLANNER_AVAILABLE = False


# =======================================================
# BASIC TESTS
# =======================================================
@pytest.mark.skipif(not PLANNER_AVAILABLE, reason="ReviewPlanner not implemented")
class TestReviewPlanner:

    def setup_method(self):
        self.planner = ReviewPlanner()

    def test_initialization(self):
        assert self.planner is not None
        assert hasattr(self.planner, "default_review_areas")

    def test_empty_text(self):
        result = self.planner.create_review_plan("")
        assert isinstance(result, dict)
        assert "priority_areas" in result

    def test_none_text(self):
        result = self.planner.create_review_plan(None)
        assert isinstance(result, dict)

    def test_nda_contract(self):
        nda = """
        NON DISCLOSURE AGREEMENT
        Confidential information must not be shared.
        Term is 2 years.
        """
        result = self.planner.create_review_plan(nda, contract_type="NDA")
        assert isinstance(result, dict)

    def test_with_focus(self):
        result = self.planner.create_review_plan(
            "Sample contract text",
            user_focus="data privacy"
        )
        assert isinstance(result, dict)

    def test_prioritize_empty(self):
        assert self.planner.prioritize_clauses([]) == []

    def test_prioritize_data(self):
        clauses = [
            {"type": "termination", "text": "Terminate with 30 days notice"},
            {"type": "liability", "text": "Liability capped"}
        ]
        result = self.planner.prioritize_clauses(clauses)
        assert isinstance(result, list)

    def test_generate_questions(self):
        questions = self.planner.generate_review_questions(
            "NDA", ["confidentiality", "term"]
        )
        assert isinstance(questions, list)
        assert len(questions) > 0

    def test_default_structure(self):
        result = self.planner._default_plan()

        required = [
            "priority_areas",
            "review_checklist",
            "recommended_agents",
            "focus_questions",
            "estimated_time",
            "risk_hotspots",
        ]

        for key in required:
            assert key in result

    def test_standalone_function(self):
        result = create_review_plan("test contract", "NDA")
        assert isinstance(result, dict)


# =======================================================
# INTEGRATION TEST (LLM)
# =======================================================
@pytest.mark.skipif(
    not PLANNER_AVAILABLE or not os.getenv("GROK_API_KEY"),
    reason="LLM not configured"
)
@pytest.mark.integration
def test_review_plan_with_llm():

    planner = ReviewPlanner()

    contract = """
    SERVICE AGREEMENT

    Client hires provider for software services.
    Payment monthly.
    Term: 12 months.
    Liability limited.
    """

    result = planner.create_review_plan(contract, contract_type="Service Agreement")

    assert isinstance(result, dict)
    assert "priority_areas" in result


# =======================================================
# MODULE EXISTENCE CHECK
# =======================================================
def test_planner_module_exists():
    assert PLANNER_AVAILABLE, (
        "agents/review_planner.py missing.\n"
        "Create ReviewPlanner agent."
    )


# =======================================================
# RUN DIRECTLY
# =======================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
