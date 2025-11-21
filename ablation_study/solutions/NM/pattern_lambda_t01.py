from typing import Callable, Any
from functools import reduce

def transform_pipeline(data: list, *transforms: Callable) -> list:
    """
    Apply a sequence of transformations to each item in data.

    """
    if not transforms:
        return data.copy()

    def apply_all(item):
        return reduce(lambda x, f: f(x), transforms, item)

    return [apply_all(item) for item in data]
