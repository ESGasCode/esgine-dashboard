def run_esg_checks(data, rule_choice):
    # This is a stub. In production, you'd load YAML rules from ESG-as-Code
    rules = {
        "UK – FCA": ["climate_disclosure", "risk_management"],
        "EU – SFDR": ["principal_adverse_impacts", "sustainability_risks"],
        "US – SEC": ["scope_1_2_emissions"],
        "Global – ISSB": ["ifrs_s1", "ifrs_s2"]
    }

    required_fields = rules.get(rule_choice, [])
    results = []

    for field in required_fields:
        if field in data:
            results.append(f"✅ {field}: Present")
        else:
            results.append(f"❌ {field}: Missing")

    return results