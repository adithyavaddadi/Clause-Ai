from agents.report_generator import generate_contract_report

print(generate_contract_report(
    contract_type="Service Agreement",
    legal_analysis="LEGAL RISK: Medium",
    compliance_analysis="COMPLIANCE RISK: Low",
    finance_analysis="FINANCIAL RISK: Medium",
))
