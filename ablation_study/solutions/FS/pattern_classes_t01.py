class Counter:
    """
    A counter that tracks its value and history of changes.

    FS Strategy: Encapsulation with property decorators for clean interface.
    Pattern: State management through instance variables - OOP fundamental.
    """

    def __init__(self, initial: int = 0):
        """Initialize counter with optional initial value."""
        self._initial = initial
        self._value = initial
        self._history = [initial]

    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        self._value += amount
        self._history.append(self._value)
        return self._value

    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        self._value -= amount
        self._history.append(self._value)
        return self._value

    def reset(self) -> None:
        """Reset counter to initial value."""
        self._value = self._initial
        self._history.append(self._value)

    @property
    def value(self) -> int:
        """Get current value."""
        return self._value

    def get_history(self) -> list[int]:
        """Get list of all values (including initial)."""
        return self._history.copy()
