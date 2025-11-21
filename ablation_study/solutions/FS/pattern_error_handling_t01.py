from typing import Optional

def safe_divide(a: float, b: float, default: Optional[float] = None) -> Optional[float]:
    """
    Safely divide a by b, handling division by zero.

    FS Strategy: Simple try-except with type error handling.
    Pattern: Error handling is the dual of conditional logic - exceptional paths.
    """
    try:
        return a / b
    except (ZeroDivisionError, TypeError):
        return default
