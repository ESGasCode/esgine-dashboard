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
    for check in rule.get("compliance_check", []):
        field = check["field"]
        required = check.get("must_exist", False)
        exists = field in report
        results.append({
            "field": field,
            "must_exist": required,
            "exists": exists,
            "compliant": required == exists
        })
    return results

if __name__ == "__main__":
    rule = load_rule("rules/us-sec-esg.yaml")
    report = load_report("examples/sample_report.json")
    results = validate(report, rule)

    for result in results:
        print(result)
