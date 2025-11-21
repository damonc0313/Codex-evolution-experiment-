from typing import Callable
from functools import reduce

def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions into a single function.

    FS Strategy: Right-to-left composition using reduce.
    Deep insight: This is the essence of functional programming - functions as values.
    Connects to t01 (pipeline) but in reverse direction.
    """
    if not functions:
        # Identity function
        return lambda x: x

    if len(functions) == 1:
        return functions[0]

    # Compose right-to-left: compose(f, g, h)(x) = f(g(h(x)))
    def composed(x):
        # Apply functions in reverse order (right-to-left)
        return reduce(lambda val, func: func(val), reversed(functions), x)

    return composed
