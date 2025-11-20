import pytest
from solution import Temperature

def test_initialization():
    t = Temperature(0)
    assert t.celsius == 0

def test_celsius_property():
    t = Temperature(25)
    assert t.celsius == 25

def test_fahrenheit_conversion():
    t = Temperature(0)
    assert t.fahrenheit == 32

    t = Temperature(100)
    assert t.fahrenheit == 212

    t = Temperature(25)
    assert t.fahrenheit == pytest.approx(77.0)

def test_kelvin_conversion():
    t = Temperature(0)
    assert t.kelvin == pytest.approx(273.15)

    t = Temperature(100)
    assert t.kelvin == pytest.approx(373.15)

    t = Temperature(-273.15)
    assert t.kelvin == pytest.approx(0)

def test_set_fahrenheit():
    t = Temperature(0)
    t.set_fahrenheit(32)
    assert t.celsius == pytest.approx(0)

    t.set_fahrenheit(212)
    assert t.celsius == pytest.approx(100)

    t.set_fahrenheit(77)
    assert t.celsius == pytest.approx(25, rel=1e-5)

def test_set_kelvin():
    t = Temperature(0)
    t.set_kelvin(273.15)
    assert t.celsius == pytest.approx(0)

    t.set_kelvin(373.15)
    assert t.celsius == pytest.approx(100)

def test_negative_temperatures():
    t = Temperature(-40)
    assert t.celsius == -40
    assert t.fahrenheit == pytest.approx(-40)  # -40C == -40F

def test_string_representation():
    t = Temperature(25)
    assert str(t) == "25.0°C"

    t = Temperature(0)
    assert str(t) == "0.0°C"

    t = Temperature(-10.5)
    assert str(t) == "-10.5°C"

def test_round_trip():
    t = Temperature(100)
    fahrenheit = t.fahrenheit
    t.set_fahrenheit(fahrenheit)
    assert t.celsius == pytest.approx(100)

    kelvin = t.kelvin
    t.set_kelvin(kelvin)
    assert t.celsius == pytest.approx(100)

def test_properties_are_readonly():
    t = Temperature(25)
    # Properties should not be settable directly
    with pytest.raises(AttributeError):
        t.celsius = 30
    with pytest.raises(AttributeError):
        t.fahrenheit = 100
    with pytest.raises(AttributeError):
        t.kelvin = 300
