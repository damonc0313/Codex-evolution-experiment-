from typing import Any, Callable

def multi_sort(items: list[dict], *criteria: tuple[str, bool]) -> list[dict]:
    """
    Sort items by multiple criteria.

    FS Strategy: Lambda-based sort keys with stable sort for multiple criteria.
    Learning: Similar to walrus t02 (config parsing) in handling missing keys.
    """
    if not criteria:
        return items.copy()

    result = items.copy()

    # Sort by criteria in reverse order (last criterion applied first due to stable sort)
    for key_name, reverse in reversed(criteria):
        result.sort(
            key=lambda item: (item.get(key_name) is None, item.get(key_name)),
            reverse=reverse
        )

    return result
