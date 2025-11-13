# Task: JSON Parser with Fallback

Implement a function that safely parses JSON with fallback handling.

**Function signature:**
```python
import json
from typing import Any

def parse_json(json_string: str, default: Any = None) -> Any:
    """
    Parse JSON string with error handling.

    Args:
        json_string: JSON string to parse
        default: Value to return on parse error

    Returns:
        Parsed JSON or default on error
    """
    pass
```

**Requirements:**
- Use try-except for json.JSONDecodeError
- Return default on any parsing error
- Handle empty strings
- Handle None input
- Preserve parsed data types (dict, list, etc.)
