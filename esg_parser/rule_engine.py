import yaml
import json

def load_rule(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def load_report(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def validate(report, rule):
    results = []
    passed = 0
    failed = 0
    for check in rule.get("compliance_check", []):
        field = check["field"]
        required = check.get("must_exist", False)
        exists = field in report
        compliant = required == exists
        if compliant:
            passed += 1
        else:
            failed += 1
        results.append({
            "field": field,
            "must_exist": required,
            "exists": exists,
            "compliant": compliant,
            "description": check.get("description", f"Check for field '{field}'"),
            "status": compliant
        })
    score = round((passed / (passed + failed)) * 100, 2) if (passed + failed) > 0 else 0
    return {
        "score": score,
        "passed": passed,
        "failed": failed,
        "rules": results
    }

# ✅ This is what your Streamlit app expects
def run_rule_engine(data, rules):
    return validate(data, rules)
