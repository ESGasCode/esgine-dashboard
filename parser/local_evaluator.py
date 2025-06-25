# parser/local_evaluator.py

import yaml
import json

def load_yaml_rule(filepath):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

def load_json_report(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def evaluate_rule(rule, report):
    results = []
    is_text = isinstance(report, str)

    for check in rule.get("compliance_check", []):
        keyword = check.get("field")
        must_exist = check.get("must_exist", False)

        if is_text:
            found = keyword.lower() in report.lower()
        else:
            found = keyword in report

        results.append({
            "field": keyword,
            "status": "✅ OK" if found else "❌ MISSING"
        })

    return results

# Example usage
if __name__ == "__main__":
    rule = load_yaml_rule("rules/issb/ifrs-s1-s2.yaml")
    report = load_json_report("examples/sample_report.json")
    result = evaluate_rule(rule, report)
    for r in result:
        print(f"{r['field']}: {r['status']}")
