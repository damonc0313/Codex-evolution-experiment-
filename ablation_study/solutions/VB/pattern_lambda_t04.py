from typing import Any, Callable
from functools import reduce

def custom_reduce(items: list, operation: str, initial: Any = None) -> Any:
    """
    Reduce list using specified operation.

    """
    # Define operations as lambdas
    operations = {
        "sum": (lambda a, b: a + b, 0),
        "product": (lambda a, b: a * b, 1),
        "concat": (lambda a, b: a + b, ""),
        "min": (lambda a, b: a if a < b else b, None),
        "max": (lambda a, b: a if a > b else b, None),
        "and": (lambda a, b: a and b, True),
        "or": (lambda a, b: a or b, False),
    }

    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")

    op_func, default_initial = operations[operation]

    if initial is None:
        initial = default_initial

    # Handle empty lists
    if not items:
        return initial

    # For min/max, use first element as initial if not provided
    if operation in ["min", "max"] and default_initial is None:
        return reduce(op_func, items[1:], items[0])

    return reduce(op_func, items, initial)
