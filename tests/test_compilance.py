import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents_llm.compliance_agent import compliance_agent

contract = """
This agreement includes data privacy terms, audit rights,
and breach notification within 30 days.
"""

print(compliance_agent(contract, "Service Agreement", "risk"))
