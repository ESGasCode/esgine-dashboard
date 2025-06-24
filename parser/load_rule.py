import yaml

def load_rule(rule_path):
    with open(rule_path, "r") as f:
        return yaml.safe_load(f)
