from typing import Any, Callable, Optional

def conditional_filter(
    items: list,
    min_val: Optional[Callable] = None,
    max_val: Optional[Callable] = None,
    predicate: Optional[Callable] = None
) -> list:
    """
    Filter items based on optional min, max, and custom predicate.

    """
    def passes_all_conditions(item):
        if min_val is not None and not min_val(item):
            return False
        if max_val is not None and not max_val(item):
            return False
        if predicate is not None and not predicate(item):
            return False
        return True

    return [item for item in items if passes_all_conditions(item)]
