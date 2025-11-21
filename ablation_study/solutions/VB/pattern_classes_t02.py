class Temperature:
    """
    Temperature value with unit conversion.

    """

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
