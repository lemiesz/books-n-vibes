import json

def safe_json(value):
    try:
        return json.loads(value)
    except Exception:
        return {}
