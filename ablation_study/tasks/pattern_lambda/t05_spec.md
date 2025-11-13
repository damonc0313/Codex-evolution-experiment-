# Task: Function Composer

Implement a function that composes multiple functions into a single function.

**Function signature:**
```python
from typing import Callable

def compose(*functions: Callable) -> Callable:
    """
    Compose multiple functions into a single function.

    Functions are applied right-to-left (mathematical composition).
    compose(f, g, h)(x) == f(g(h(x)))

    Args:
        *functions: Functions to compose

    Returns:
        Composed function
    """
    pass
```

**Requirements:**
- Use lambda functions and/or reduce
- Apply functions right-to-left (mathematical composition order)
- Handle empty function list (return identity function)
- Handle single function (return that function)
- Composed function should work with any input type
