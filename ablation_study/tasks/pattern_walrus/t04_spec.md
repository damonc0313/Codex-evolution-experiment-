# Task: Match and Extract Pattern

Implement a function that searches text for a regex pattern and returns extracted groups.

**Function signature:**
```python
import re
from typing import Optional

def match_and_extract(text: str, pattern: str) -> Optional[dict[str, str]]:
    """
    Match pattern against text and extract named groups.

    Args:
        text: Text to search
        pattern: Regex pattern with named groups

    Returns:
        Dict of group names to values, or None if no match
    """
    pass
```

**Requirements:**
- Use walrus operator to match and extract in one expression
- Return dictionary of named group matches
- Return None if no match found
- Handle patterns with multiple named groups
- Handle empty strings
