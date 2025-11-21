import json
from typing import Any

def parse_json(json_string: str, default: Any = None) -> Any:
    """
    Parse JSON string with error handling.

    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return default
