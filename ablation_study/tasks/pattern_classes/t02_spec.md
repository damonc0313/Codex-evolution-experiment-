# Task: Temperature Converter

Implement a Temperature class that stores a temperature and converts between units.

**Class specification:**
```python
class Temperature:
    """Temperature value with unit conversion."""

    def __init__(self, celsius: float):
        """Initialize with temperature in Celsius."""
        pass

    @property
    def celsius(self) -> float:
        """Get temperature in Celsius."""
        pass

    @property
    def fahrenheit(self) -> float:
        """Get temperature in Fahrenheit."""
        pass

    @property
    def kelvin(self) -> float:
        """Get temperature in Kelvin."""
        pass

    def set_fahrenheit(self, fahrenheit: float) -> None:
        """Set temperature from Fahrenheit value."""
        pass

    def set_kelvin(self, kelvin: float) -> None:
        """Set temperature from Kelvin value."""
        pass

    def __str__(self) -> str:
        """Return string representation: '25.0°C'"""
        pass
```

**Requirements:**
- Store internally as Celsius
- Use properties for read-only unit conversions
- Conversion formulas:
  - F = C * 9/5 + 32
  - K = C + 273.15
- String format: "{celsius}°C"
