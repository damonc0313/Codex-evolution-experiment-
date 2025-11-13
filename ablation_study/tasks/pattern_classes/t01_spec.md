# Task: Counter Class

Implement a Counter class that tracks incrementable values with history.

**Class specification:**
```python
class Counter:
    """A counter that tracks its value and history of changes."""

    def __init__(self, initial: int = 0):
        """Initialize counter with optional initial value."""
        pass

    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        pass

    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        pass

    def reset(self) -> None:
        """Reset counter to initial value."""
        pass

    @property
    def value(self) -> int:
        """Get current value."""
        pass

    def get_history(self) -> list[int]:
        """Get list of all values (including initial)."""
        pass
```

**Requirements:**
- Use instance variables for state
- Track all values in history list
- Property decorator for value getter
- Reset returns to initial value, not zero
