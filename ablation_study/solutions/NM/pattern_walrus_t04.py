import re
from typing import Optional

def match_and_extract(text: str, pattern: str) -> Optional[dict[str, str]]:
    """
    Match pattern against text and extract named groups.

    """
    if (match := re.search(pattern, text)):
        return match.groupdict()
    return None
