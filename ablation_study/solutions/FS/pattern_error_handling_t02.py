import json
from typing import Any

def parse_json(json_string: str, default: Any = None) -> Any:
    """
    Parse JSON string with error handling.

    FS Strategy: Catch all possible JSON parsing errors.
    Learning: Similar to t01 (safe_divide), fallback pattern is consistent.
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return default
