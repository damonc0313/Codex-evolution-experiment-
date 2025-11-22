def flatten(nested: list) -> list:
    """
    Flatten a nested list (one level deep) using comprehensions.

    Pattern recognition: Similar to walrus t01 (filtering), but with conditional expansion.
    """
    return [
        item
        for element in nested
        for item in (element if isinstance(element, list) else [element])
    ]
