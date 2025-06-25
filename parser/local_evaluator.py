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

    for check in rule.get("compliance_check", []):
        field = check.get("field")
        must_exist = check.get("must_exist", False)
        must_contain = check.get("must_contain", [])

        value_exists = False
        value_contains = True

        # Step 1: Check if field exists
        if isinstance(report, dict):
            value = report.get(field, "")
            value_exists = field in report
        elif isinstance(report, str):
            value = report
            value_exists = field.lower() in report.lower()

        # Step 2: Check if required keywords are present
        if must_contain:
            for keyword in must_contain:
                if keyword.lower() not in str(value).lower():
                    value_contains = False
                    break

        # Step 3: Append result
        if must_exist and not value_exists:
            results.append({"field": field, "status": False, "description": "❌ Missing required field"})
        elif must_contain and not value_contains:
            results.append({"field": field, "status": False, "description": f"❌ Missing keywords: {must_contain}"})
        else:
            results.append({"field": field, "status": True, "description": "✅ Compliant"})

    return results

# Example usage
if __name__ == "__main__":
    rule = load_yaml_rule("rules/issb/ifrs-s1-s2.yaml")
    report = load_json_report("examples/sample_report.json")
    result = evaluate_rule(rule, report)
    for r in result:
        print(f"{r['field']}: {r['status']}")
