"""
MASTER EXECUTOR AGENT (Main Brain)
Runs classifier + agents + final report
Parallel + stable + clean
"""

from __future__ import annotations
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from agents.contract_classifier import ContractClassifier
from agents.clause_analyzer import ClauseAnalyzer
from report.final_report import generate_final_report

from agents_llm.legal_agent import legal_agent
from agents_llm.finance_agent import finance_agent
from agents_llm.compliance_agent import compliance_agent
from agents_llm.operations_agent import operations_agent

logger = logging.getLogger(__name__)


class ExecutorAgent:

    def __init__(self, timeout_per_agent: int = 60):
        self.timeout = timeout_per_agent
        self.clause_analyzer = ClauseAnalyzer()
        self.contract_classifier = ContractClassifier()

    # =====================================================
    # QUICK MODE (for tests / fast)
    # =====================================================
    def execute_quick_analysis(self, contract_text: str | None, user_focus: str = "") -> Dict[str, Any]:
        return self.execute_full_analysis(
            contract_text=contract_text,
            user_focus=user_focus,
            run_parallel=True,
            run_clause_analysis=False
        )

    # =====================================================
    # MAIN EXECUTION
    # =====================================================
    def execute_full_analysis(
        self,
        contract_text: str | None,
        user_focus: str = "",
        run_parallel: bool = True,
        run_clause_analysis: bool = True,
    ) -> Dict[str, Any]:

        start_time = time.time()
        safe_text = (contract_text or "").strip()

        results: Dict[str, Any] = {
            "status": "started",
            "contract_type": "Other",
            "legal_analysis": "",
            "finance_analysis": "",
            "compliance_analysis": "",
            "operations_analysis": "",
            "clause_analyses": [],
            "report": "",
            "risk_level": "Medium",
            "risk_percentage": 50,
            "execution_time": 0,
            "errors": [],
        }

        if not safe_text:
            results["status"] = "failed"
            results["errors"].append("No contract text provided")
            return results

        try:
            # --------------------------------------------------
            # STEP 1: CLASSIFY CONTRACT
            # --------------------------------------------------
            results["contract_type"] = self.contract_classifier.classify_simple(safe_text)

            # --------------------------------------------------
            # STEP 2: RUN AGENTS
            # --------------------------------------------------
            if run_parallel:
                self._run_parallel_agents(safe_text, results, user_focus)
            else:
                self._run_sequential_agents(safe_text, results, user_focus)

            # --------------------------------------------------
            # STEP 3: CLAUSE ANALYSIS
            # --------------------------------------------------
            if run_clause_analysis:
                clauses = self.clause_analyzer.extract_clauses(safe_text)
                if clauses:
                    results["clause_analyses"] = self.clause_analyzer.analyze_clauses(clauses)

            # --------------------------------------------------
            # STEP 4: FINAL REPORT
            # --------------------------------------------------
            results["report"] = generate_final_report(
                contract_type=results["contract_type"],
                legal=results["legal_analysis"],
                finance=results["finance_analysis"],
                compliance=results["compliance_analysis"],
                operations=results["operations_analysis"],
                user_focus=user_focus
            )

            # --------------------------------------------------
            # STEP 5: RISK CALCULATION
            # --------------------------------------------------
            results["risk_level"], results["risk_percentage"] = self._calculate_risk(results)

            results["status"] = "completed"

        except Exception as e:
            logger.error(f"Executor error: {e}", exc_info=True)
            results["status"] = "failed"
            results["errors"].append(str(e))

        results["execution_time"] = round(time.time() - start_time, 2)
        return results

    # =====================================================
    # PARALLEL AGENTS
    # =====================================================
    def _run_parallel_agents(self, contract_text: str, results: Dict[str, Any], user_focus: str):

        agents = {
            "legal": lambda: legal_agent(contract_text, results["contract_type"], user_focus),
            "finance": lambda: finance_agent(contract_text, results["contract_type"], user_focus),
            "compliance": lambda: compliance_agent(contract_text, results["contract_type"], user_focus),
            "operations": lambda: operations_agent(contract_text),
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fn): name for name, fn in agents.items()}

            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result(timeout=self.timeout)
                    results[f"{name}_analysis"] = result if isinstance(result, str) else str(result)
                except Exception as e:
                    logger.error(f"{name} agent failed: {e}")
                    results[f"{name}_analysis"] = ""

    # =====================================================
    # SEQUENTIAL AGENTS
    # =====================================================
    def _run_sequential_agents(self, contract_text: str, results: Dict[str, Any], user_focus: str):

        for name, fn in (
            ("legal", legal_agent),
            ("finance", finance_agent),
            ("compliance", compliance_agent),
            ("operations", operations_agent),
        ):
            try:
                if name == "operations":
                    result = fn(contract_text)
                else:
                    result = fn(contract_text, results["contract_type"], user_focus)

                results[f"{name}_analysis"] = result if isinstance(result, str) else str(result)

            except Exception as e:
                logger.error(f"{name} failed: {e}")
                results[f"{name}_analysis"] = ""

    # =====================================================
    # RISK CALCULATION
    # =====================================================
    def _calculate_risk(self, results: Dict[str, Any]):

        base = 50
        clause_scores = []

        for c in results.get("clause_analyses", []):
            try:
                clause_scores.append(int(c.get("risk_score", 50)))
            except:
                pass

        if clause_scores:
            base = int((base + sum(clause_scores)/len(clause_scores)) / 2)

        base = max(0, min(100, base))

        if base < 30:
            return "Low", base
        elif base < 70:
            return "Medium", base
        return "High", base


# =====================================================
# SIMPLE CALL FUNCTION
# =====================================================
def analyze_contract(contract_text: str, user_focus: str = "") -> Dict[str, Any]:
    executor = ExecutorAgent()
    return executor.execute_full_analysis(contract_text, user_focus)
