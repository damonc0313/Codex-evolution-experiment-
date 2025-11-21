import re
from typing import Optional

def match_and_extract(text: str, pattern: str) -> Optional[dict[str, str]]:
    """
    Match pattern against text and extract named groups.

    FS Strategy: Walrus for match-and-extract in single conditional.
    Cross-task insight: This is canonical walrus use case - "test result, use if truthy".
    """
    if (match := re.search(pattern, text)):
        return match.groupdict()
    return None
