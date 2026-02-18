# utils/parallel_runner.py
# CLAUSE AI PARALLEL AGENT EXECUTION (FINAL PRODUCTION SAFE)

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import logging
import time
from typing import Callable, List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# =========================================================
# GENERIC PARALLEL TASK RUNNER
# =========================================================
def run_parallel_tasks(
    tasks: List[Callable],
    max_workers: int = 4,
    timeout_per_task: Optional[int] = None
) -> List[Any]:
    """
    Run list of functions in parallel.

    Args:
        tasks: list of callable functions
        max_workers: number of threads
        timeout_per_task: timeout per task in seconds

    Returns:
        list of results
    """

    if not tasks:
        return []

    results: List[Any] = []

    logger.info(f"⚡ Running {len(tasks)} tasks in parallel...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for task in tasks]

        for future in as_completed(futures):
            try:
                result = future.result(timeout=timeout_per_task)
                results.append(result)
            except TimeoutError:
                logger.error("Parallel task timeout")
                results.append("TIMEOUT")
            except Exception as e:
                logger.error(f"Parallel task failed: {e}")
                results.append("ERROR")

    logger.info(f"⚡ Parallel finished in {round(time.time()-start_time,2)}s")
    return results


# =========================================================
# PARALLEL DICT RUNNER (FOR AGENTS)
# =========================================================
def run_parallel_dict(
    task_dict: Dict[str, Callable],
    max_workers: int = 4,
    timeout_per_task: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run named tasks in parallel.

    Example:
        {
          "legal": lambda: legal_agent(text),
          "finance": lambda: finance_agent(text)
        }
    """

    if not task_dict:
        return {}

    results: Dict[str, Any] = {}

    logger.info(f"⚡ Running {len(task_dict)} agents in parallel")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(func): name for name, func in task_dict.items()}

        for future in as_completed(future_map):
            name = future_map[future]

            try:
                results[name] = future.result(timeout=timeout_per_task)
            except TimeoutError:
                logger.error(f"{name} agent timeout")
                results[name] = "TIMEOUT"
            except Exception as e:
                logger.error(f"{name} agent failed: {e}")
                results[name] = "ERROR"

    logger.info(f"⚡ All agents completed in {round(time.time()-start_time,2)}s")
    return results


# =========================================================
# CLAUSE AI AGENTS PARALLEL (MAIN USE)
# =========================================================
def run_agents_parallel(
    legal_fn: Callable,
    finance_fn: Callable,
    compliance_fn: Callable,
    operations_fn: Optional[Callable] = None,
    timeout: int = 90
) -> Dict[str, Any]:
    """
    Run ClauseAI core agents in parallel safely.

    Returns:
        {
          legal: "...",
          finance: "...",
          compliance: "...",
          operations: "..."
        }
    """

    task_map: Dict[str, Callable] = {
        "legal": legal_fn,
        "finance": finance_fn,
        "compliance": compliance_fn,
    }

    if operations_fn:
        task_map["operations"] = operations_fn

    return run_parallel_dict(
        task_map,
        max_workers=4,
        timeout_per_task=timeout
    )
