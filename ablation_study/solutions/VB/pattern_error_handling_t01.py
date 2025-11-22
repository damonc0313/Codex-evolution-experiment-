from typing import Optional

def safe_divide(a: float, b: float, default: Optional[float] = None) -> Optional[float]:
    """
    Safely divide a by b, handling division by zero.

    """
    try:
        return a / b
    except (ZeroDivisionError, TypeError):
        return default
