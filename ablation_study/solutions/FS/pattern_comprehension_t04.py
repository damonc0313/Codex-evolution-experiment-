from typing import Callable, Optional

def build_dict(
    keys: list,
    values: list,
    condition: Optional[Callable[[any, any], bool]] = None
) -> dict:
    """
    Build dictionary from keys and values, optionally filtering pairs.

    FS Strategy: Dict comprehension with zip and conditional filtering.
    Cross-pattern: Combines lambda t03 (conditional filter) with comprehension.
    """
    if condition is None:
        return {k: v for k, v in zip(keys, values)}

    return {k: v for k, v in zip(keys, values) if condition(k, v)}
