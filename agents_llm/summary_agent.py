import logging
from utils.hybrid_llm import call_hybrid_llm

logger = logging.getLogger(__name__)


def summary_agent(full_context, agent_results, contract_type, user_focus=""):
    """
    FINAL EXECUTIVE REPORT
    OpenAI first → fallback Ollama
    Includes agent analysis inside report
    """

    if not full_context:
        full_context = "No contract provided"

    if not isinstance(agent_results, dict):
        agent_results = {}

    contract_type = contract_type or "General"

    try:
        prompt = f"""
You are a CHIEF CONTRACT ANALYSIS AI.

Generate a PROFESSIONAL FINAL CONTRACT REPORT.

==============================
FINAL CONTRACT INTELLIGENCE REPORT
==============================

1. CONTRACT OVERVIEW
Explain contract purpose in simple business English.

2. OVERALL RISK SCORE
Give:
- Risk Score (0-100%)
- Risk Level: Low/Medium/High
- 1 line justification

3. KEY LEGAL RISKS
Summarize from legal agent.

4. FINANCIAL RISKS
Summarize from finance agent.

5. COMPLIANCE RISKS
Summarize from compliance agent.

6. CRITICAL MISSING CLAUSES
What protections are missing.

7. FINAL EXECUTIVE SUMMARY
Clear decision: Safe / Review / High Risk.

IMPORTANT:
- Professional business tone
- Clear headings
- Not too long
- No generic advice

==============================
AGENT ANALYSIS
==============================

LEGAL:
{agent_results.get("Legal","")}

FINANCE:
{agent_results.get("Finance","")}

COMPLIANCE:
{agent_results.get("Compliance","")}

OPERATIONS:
{agent_results.get("Operations","")}

==============================
CONTRACT
==============================
{full_context[:5000]}
"""

        logger.info("Generating final executive report...")
        response = call_hybrid_llm(prompt, role="summary")

        if not response or not isinstance(response, str):
            return _summary_fallback(agent_results, contract_type)

        return response.strip()

    except Exception as e:
        logger.error(f"Summary error: {str(e)}")
        return _summary_fallback(agent_results, contract_type)


# ---------------- FALLBACK REPORT ----------------
def _summary_fallback(agent_results, contract_type):
    return f"""
FINAL CONTRACT INTELLIGENCE REPORT

Contract Type: {contract_type}

OVERALL RISK: Medium (Fallback Analysis)

LEGAL:
{agent_results.get("Legal","No data")}

FINANCIAL:
{agent_results.get("Finance","No data")}

COMPLIANCE:
{agent_results.get("Compliance","No data")}

FINAL DECISION:
Contract requires careful review before signing.
"""
