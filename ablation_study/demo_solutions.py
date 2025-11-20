#!/usr/bin/env python3
"""
Proof-of-concept: Manual solutions for demonstration tasks.

This demonstrates that the harness infrastructure works by providing
hand-crafted solutions for a subset of tasks.
"""

# Solutions for pattern_walrus tasks

def walrus_t01_solution():
    """Solution for walrus/t01: Process Valid Lines"""
    return '''
def process_valid_lines(lines: list[str]) -> list[str]:
    """Process lines, returning only those longer than 5 characters in uppercase."""
    return [
        line_upper
        for line in lines
        if len(line) > 5 and (line_upper := line.upper())
    ]
'''

def walrus_t02_solution():
    """Solution for walrus/t02: Parse Config with Defaults"""
    return '''
def parse_config(config: dict, key: str, default: int = 0, min_val: int = 0) -> int:
    """Parse a config value, applying default and minimum validation."""
    if (val := config.get(key)) is not None and isinstance(val, int) and val >= min_val:
        return val
    return default
'''


# Solutions for pattern_lambda tasks

def lambda_t01_solution():
    """Solution for lambda/t01: Transform Pipeline"""
    return '''
from typing import Callable, Any
from functools import reduce

def transform_pipeline(data: list, *transforms: Callable) -> list:
    """Apply a sequence of transformations to each item in data."""
    if not transforms:
        return data.copy()

    def apply_all(item):
        return reduce(lambda x, f: f(x), transforms, item)

    return [apply_all(item) for item in data]
'''

def lambda_t02_solution():
    """Solution for lambda/t02: Custom Sorter"""
    return '''
from typing import Any, Callable

def multi_sort(items: list[dict], *criteria: tuple[str, bool]) -> list[dict]:
    """Sort items by multiple criteria."""
    if not criteria:
        return items.copy()

    result = items.copy()

    # Sort by criteria in reverse order (last criterion applied first)
    for key_name, reverse in reversed(criteria):
        result.sort(
            key=lambda item: (item.get(key_name) is None, item.get(key_name)),
            reverse=reverse
        )

    return result
'''


# Solutions for pattern_comprehension tasks

def comprehension_t01_solution():
    """Solution for comprehension/t01: Nested List Flattening"""
    return '''
def flatten(nested: list) -> list:
    """Flatten a nested list (one level deep) using comprehensions."""
    return [
        item
        for element in nested
        for item in (element if isinstance(element, list) else [element])
    ]
'''

def comprehension_t02_solution():
    """Solution for comprehension/t02: Dictionary Inversion"""
    return '''
def invert_dict(d: dict) -> dict:
    """Invert dictionary, swapping keys and values."""
    return {value: key for key, value in d.items()}
'''


# Solutions for pattern_error_handling tasks

def error_handling_t01_solution():
    """Solution for error_handling/t01: Safe Division"""
    return '''
from typing import Optional

def safe_divide(a: float, b: float, default: Optional[float] = None) -> Optional[float]:
    """Safely divide a by b, handling division by zero."""
    try:
        return a / b
    except (ZeroDivisionError, TypeError):
        return default
'''

def error_handling_t02_solution():
    """Solution for error_handling/t02: JSON Parser with Fallback"""
    return '''
import json
from typing import Any

def parse_json(json_string: str, default: Any = None) -> Any:
    """Parse JSON string with error handling."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return default
'''


# Solutions for pattern_classes tasks

def classes_t01_solution():
    """Solution for classes/t01: Counter Class"""
    return '''
class Counter:
    """A counter that tracks its value and history of changes."""

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
'''

def classes_t02_solution():
    """Solution for classes/t02: Temperature Converter"""
    return '''
class Temperature:
    """Temperature value with unit conversion."""

    def __init__(self, celsius: float):
        """Initialize with temperature in Celsius."""
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        """Get temperature in Celsius."""
        return self._celsius

    @property
    def fahrenheit(self) -> float:
        """Get temperature in Fahrenheit."""
        return self._celsius * 9/5 + 32

    @property
    def kelvin(self) -> float:
        """Get temperature in Kelvin."""
        return self._celsius + 273.15

    def set_fahrenheit(self, fahrenheit: float) -> None:
        """Set temperature from Fahrenheit value."""
        self._celsius = (fahrenheit - 32) * 5/9

    def set_kelvin(self, kelvin: float) -> None:
        """Set temperature from Kelvin value."""
        self._celsius = kelvin - 273.15

    def __str__(self) -> str:
        """Return string representation: '25.0°C'"""
        return f"{self._celsius:.1f}°C"
'''


# Registry of demo solutions
DEMO_SOLUTIONS = {
    "pattern_walrus_t01": walrus_t01_solution(),
    "pattern_walrus_t02": walrus_t02_solution(),
    "pattern_lambda_t01": lambda_t01_solution(),
    "pattern_lambda_t02": lambda_t02_solution(),
    "pattern_comprehension_t01": comprehension_t01_solution(),
    "pattern_comprehension_t02": comprehension_t02_solution(),
    "pattern_error_handling_t01": error_handling_t01_solution(),
    "pattern_error_handling_t02": error_handling_t02_solution(),
    "pattern_classes_t01": classes_t01_solution(),
    "pattern_classes_t02": classes_t02_solution(),
}


def get_demo_solution(task_id: str) -> str:
    """Get a demo solution if available."""
    return DEMO_SOLUTIONS.get(task_id)
