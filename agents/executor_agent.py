"""
MASTER EXECUTOR AGENT (Main Brain)
Runs classifier + all agents + final summary
Parallel + clean + fast
"""

from __future__ import annotations
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from agents.contract_classifier import ContractClassifier
from agents.clause_analyzer import ClauseAnalyzer

from agents_llm.legal_agent import legal_agent
from agents_llm.finance_agent import finance_agent
from agents_llm.compliance_agent import compliance_agent
from agents_llm.operations_agent import operations_agent
from agents_llm.summary_agent import summary_agent

logger = logging.getLogger(__name__)


class ExecutorAgent:
    def __init__(self, timeout_per_agent: int = 60):
        self.timeout = timeout_per_agent
        self.clause_analyzer = ClauseAnalyzer()
        self.classifier = ContractClassifier()

    # =====================================================
    # MAIN EXECUTION
    # =====================================================
    def execute_full_analysis(self, contract_text: str | None, user_focus: str = "") -> Dict[str, Any]:

        start_time = time.time()
        safe_text = (contract_text or "").strip()

        results: Dict[str, Any] = {
            "status": "started",
            "contract_type": "Other",
            "legal": "",
            "finance": "",
            "compliance": "",
            "operations": "",
            "clauses": [],
            "final_report": "",
            "risk_level": "Medium",
            "risk_score": 50,
            "execution_time": 0,
            "errors": []
        }

        if not safe_text:
            results["status"] = "failed"
            results["errors"].append("No contract text provided")
            return results

        try:
            # ================================
            # STEP 1: CLASSIFY CONTRACT
            # ================================
            results["contract_type"] = self.classifier.classify_simple(safe_text)

            # ================================
            # STEP 2: RUN AGENTS PARALLEL
            # ================================
            agent_outputs = self._run_parallel_agents(
                contract_text=safe_text,
                contract_type=results["contract_type"],
                user_focus=user_focus
            )

            results.update(agent_outputs)

            # ================================
            # STEP 3: CLAUSE ANALYSIS
            # ================================
            clauses = self.clause_analyzer.extract_clauses(safe_text)
            if clauses:
                results["clauses"] = self.clause_analyzer.analyze_clauses(clauses)

            # ================================
            # STEP 4: FINAL SUMMARY REPORT
            # ================================
            agent_dict = {
                "Legal": results["legal"],
                "Finance": results["finance"],
                "Compliance": results["compliance"],
                "Operations": results["operations"],
            }

            results["final_report"] = summary_agent(
                full_context=safe_text,
                agent_results=agent_dict,
                contract_type=results["contract_type"],
                user_focus=user_focus
            )

            # ================================
            # STEP 5: RISK SCORE
            # ================================
            results["risk_level"], results["risk_score"] = self._calculate_risk(results)

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
    def _run_parallel_agents(self, contract_text: str, contract_type: str, user_focus: str):

        outputs = {
            "legal": "",
            "finance": "",
            "compliance": "",
            "operations": ""
        }

        agents = {
            "legal": lambda: legal_agent(contract_text, contract_type, user_focus),
            "finance": lambda: finance_agent(contract_text, contract_type, user_focus),
            "compliance": lambda: compliance_agent(contract_text, contract_type, user_focus),
            "operations": lambda: operations_agent(contract_text),
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fn): name for name, fn in agents.items()}

            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result(timeout=self.timeout)
                    outputs[name] = result if isinstance(result, str) else str(result)
                except Exception as e:
                    outputs[name] = ""
                    logger.error(f"{name} agent failed: {e}")

        return outputs

    # =====================================================
    # RISK CALCULATION
    # =====================================================
    def _calculate_risk(self, results: Dict[str, Any]):

        base = 50
        clause_scores = []

        for c in results.get("clauses", []):
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
