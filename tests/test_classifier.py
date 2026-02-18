import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents_llm.classifier_agent import classify_contract

contract = """
This employment agreement includes salary, termination policy,
and employee responsibilities.
"""

print("Contract Type:", classify_contract(contract))
