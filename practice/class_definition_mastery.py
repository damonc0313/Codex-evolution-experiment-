"""
Class Definition Mastery - ACE Practice Task (Iteration 5)
===========================================================

Task: ace_practice_class_definition_20251107_063421
Objective: Improve class_definition proficiency from 29.3% → 80%

Object-oriented programming patterns for clean, maintainable code:
- Data encapsulation with properties
- Inheritance and composition
- Magic methods for operator overloading
- Class vs instance methods
- Abstract base classes and interfaces

Current: 29.3% → Target: 80% → Gap: 50.7% (priority rank: 5/5)
"""

from typing import Any, ClassVar, List, Optional, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import total_ordering


# Exercise 1: Basic class with encapsulation
# ==========================================

class BankAccount:
    """
    Bank account with encapsulated balance.

    Demonstrates: Private attributes, properties, methods
    """

    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self._account_number = account_number
        self._balance = initial_balance
        self._transaction_history: List[str] = []

    @property
    def balance(self) -> float:
        """Read-only access to balance"""
        return self._balance

    @property
    def account_number(self) -> str:
        """Read-only access to account number"""
        return self._account_number

    def deposit(self, amount: float) -> bool:
        """Deposit money into account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._transaction_history.append(f"Deposit: +${amount:.2f}")
        return True

    def withdraw(self, amount: float) -> bool:
        """Withdraw money from account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self._balance:
            return False

        self._balance -= amount
        self._transaction_history.append(f"Withdrawal: -${amount:.2f}")
        return True

    def get_transaction_history(self) -> List[str]:
        """Return copy of transaction history"""
        return self._transaction_history.copy()


# Exercise 2: Inheritance hierarchy
# =================================

class Vehicle:
    """Base vehicle class"""

    def __init__(self, brand: str, model: str, year: int):
        self.brand = brand
        self.model = model
        self.year = year

    def describe(self) -> str:
        return f"{self.year} {self.brand} {self.model}"

    def start_engine(self) -> str:
        return "Engine started"


class ElectricVehicle(Vehicle):
    """Electric vehicle with battery"""

    def __init__(self, brand: str, model: str, year: int, battery_capacity: float):
        super().__init__(brand, model, year)
        self.battery_capacity = battery_capacity
        self.charge_level = 100.0

    def start_engine(self) -> str:
        """Override parent method"""
        return "Electric motor activated"

    def charge(self, amount: float) -> None:
        """Charge battery"""
        self.charge_level = min(100.0, self.charge_level + amount)

    def describe(self) -> str:
        """Extend parent method"""
        return f"{super().describe()} (Electric, {self.battery_capacity}kWh)"


class HybridVehicle(Vehicle):
    """Hybrid vehicle with both engines"""

    def __init__(self, brand: str, model: str, year: int,
                 battery_capacity: float, fuel_capacity: float):
        super().__init__(brand, model, year)
        self.battery_capacity = battery_capacity
        self.fuel_capacity = fuel_capacity
        self.mode = "hybrid"

    def switch_mode(self, mode: str) -> None:
        """Switch between electric/fuel/hybrid"""
        if mode in ["electric", "fuel", "hybrid"]:
            self.mode = mode

    def start_engine(self) -> str:
        if self.mode == "electric":
            return "Electric motor activated"
        elif self.mode == "fuel":
            return "Fuel engine started"
        else:
            return "Hybrid system engaged"


# Exercise 3: Magic methods and operator overloading
# ==================================================

@total_ordering
class Money:
    """
    Money class with operator overloading.

    Demonstrates: __init__, __str__, __repr__, __add__, __eq__, __lt__
    """

    def __init__(self, amount: float, currency: str = "USD"):
        self.amount = amount
        self.currency = currency

    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.currency} ${self.amount:.2f}"

    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"Money({self.amount}, '{self.currency}')"

    def __add__(self, other: 'Money') -> 'Money':
        """Add two Money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract Money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> 'Money':
        """Multiply money by scalar"""
        return Money(self.amount * factor, self.currency)

    def __eq__(self, other: Any) -> bool:
        """Equality comparison"""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison"""
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount < other.amount

    def __hash__(self) -> int:
        """Make Money hashable for use in sets/dicts"""
        return hash((self.amount, self.currency))


# Exercise 4: Class methods and static methods
# ============================================

class Temperature:
    """
    Temperature with multiple conversion methods.

    Demonstrates: Class methods, static methods, factory patterns
    """

    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> 'Temperature':
        """Factory method: create from Fahrenheit"""
        celsius = (fahrenheit - 32) * 5/9
        return cls(celsius)

    @classmethod
    def from_kelvin(cls, kelvin: float) -> 'Temperature':
        """Factory method: create from Kelvin"""
        celsius = kelvin - 273.15
        return cls(celsius)

    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Utility method: convert C to F"""
        return celsius * 9/5 + 32

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Utility method: convert F to C"""
        return (fahrenheit - 32) * 5/9


# Exercise 5: Abstract base classes and protocols
# ===============================================

class Shape(ABC):
    """Abstract base class for shapes"""

    @abstractmethod
    def area(self) -> float:
        """Calculate area"""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate perimeter"""
        pass

    def describe(self) -> str:
        """Default implementation"""
        return f"{self.__class__.__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Rectangle(Shape):
    """Concrete rectangle implementation"""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    """Concrete circle implementation"""

    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


# Protocol for duck typing (Python 3.8+)
class Drawable(Protocol):
    """Protocol for objects that can be drawn"""

    def draw(self) -> str:
        ...


class Canvas:
    """Canvas that accepts any drawable object"""

    def __init__(self):
        self.elements: List[Drawable] = []

    def add(self, element: Drawable) -> None:
        """Add drawable element"""
        self.elements.append(element)

    def render(self) -> List[str]:
        """Render all elements"""
        return [element.draw() for element in self.elements]


class Square:
    """Square implements Drawable protocol"""

    def __init__(self, size: float):
        self.size = size

    def draw(self) -> str:
        return f"Square({self.size})"


class Star:
    """Star implements Drawable protocol"""

    def __init__(self, points: int):
        self.points = points

    def draw(self) -> str:
        return f"Star({self.points} points)"


# Exercise 6: Dataclasses for concise definitions
# ===============================================

@dataclass
class Point:
    """2D point using dataclass"""
    x: float
    y: float

    def distance_to(self, other: 'Point') -> float:
        """Calculate distance to another point"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class Person:
    """Person with default values and type hints"""
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validation after initialization"""
        if self.age < 0:
            raise ValueError("Age cannot be negative")


@dataclass(frozen=True)
class Coordinate:
    """Immutable coordinate"""
    latitude: float
    longitude: float

    def __str__(self) -> str:
        return f"({self.latitude}, {self.longitude})"


# Exercise 7: Composition over inheritance
# ========================================

class Engine:
    """Engine component"""

    def __init__(self, horsepower: int):
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        self.running = True
        return f"Engine ({self.horsepower}hp) started"

    def stop(self) -> str:
        self.running = False
        return "Engine stopped"


class Transmission:
    """Transmission component"""

    def __init__(self, gears: int):
        self.gears = gears
        self.current_gear = 1

    def shift_up(self) -> None:
        if self.current_gear < self.gears:
            self.current_gear += 1

    def shift_down(self) -> None:
        if self.current_gear > 1:
            self.current_gear -= 1


class Car:
    """
    Car using composition instead of inheritance.

    Demonstrates: Composition pattern (has-a vs is-a)
    """

    def __init__(self, engine: Engine, transmission: Transmission):
        self.engine = engine
        self.transmission = transmission

    def start(self) -> str:
        return self.engine.start()

    def accelerate(self) -> str:
        if not self.engine.running:
            return "Engine not running"
        self.transmission.shift_up()
        return f"Accelerating (gear {self.transmission.current_gear})"


# Exercise 8: Singleton pattern
# =============================

class Singleton:
    """Singleton pattern implementation"""

    _instance: ClassVar[Optional['Singleton']] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.data = {}


class DatabaseConnection(Singleton):
    """Database connection as singleton"""

    def connect(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self.connected = True

    def query(self, sql: str) -> List[Any]:
        if not hasattr(self, 'connected') or not self.connected:
            raise RuntimeError("Not connected")
        return []


"""
CLASS DESIGN - BEST PRACTICES
==============================

ENCAPSULATION:
- Use private attributes (_attribute)
- Provide properties for controlled access
- Validate in setters or __post_init__

INHERITANCE:
- Keep hierarchies shallow (2-3 levels max)
- Follow Liskov Substitution Principle
- Override methods intentionally
- Call super() when extending behavior

COMPOSITION:
- Prefer composition over inheritance
- Use has-a relationships
- More flexible than inheritance
- Easier to test and modify

MAGIC METHODS:
- __init__: Initialization
- __str__: User-friendly string
- __repr__: Developer-friendly string
- __eq__, __lt__: Comparisons
- __add__, __mul__: Operators
- __len__, __getitem__: Container protocol
- __enter__, __exit__: Context manager

CLASS VS INSTANCE:
- Instance methods: operate on self
- Class methods: operate on class, factory patterns
- Static methods: utility functions, no self/cls

ABSTRACT CLASSES:
- Use ABC for interfaces
- Force subclasses to implement methods
- Document expected behavior
- Use @abstractmethod decorator

DATACLASSES:
- Use for data containers
- Auto-generates __init__, __repr__, __eq__
- frozen=True for immutability
- field() for complex defaults

DESIGN PATTERNS:
- Factory: Class methods for construction
- Singleton: Single instance globally
- Strategy: Composition for algorithms
- Observer: Event notification
- Builder: Step-by-step construction
"""


# Test suite
def test_class_definition_mastery():
    """Test all class definition patterns."""

    # Exercise 1: Encapsulation
    account = BankAccount("ACC001", 100.0)
    assert account.balance == 100.0
    account.deposit(50.0)
    assert account.balance == 150.0
    assert account.withdraw(30.0) is True
    assert account.balance == 120.0

    # Exercise 2: Inheritance
    ev = ElectricVehicle("Tesla", "Model 3", 2023, 75.0)
    assert "Electric" in ev.describe()
    assert "activated" in ev.start_engine()

    hybrid = HybridVehicle("Toyota", "Prius", 2023, 1.3, 43.0)
    hybrid.switch_mode("electric")
    assert "Electric" in hybrid.start_engine()

    # Exercise 3: Magic methods
    m1 = Money(100.0, "USD")
    m2 = Money(50.0, "USD")
    m3 = m1 + m2
    assert m3.amount == 150.0
    assert m1 > m2
    assert m1 * 2 == Money(200.0, "USD")

    # Exercise 4: Class/static methods
    t1 = Temperature(0.0)
    assert t1.fahrenheit == 32.0

    t2 = Temperature.from_fahrenheit(212.0)
    assert abs(t2.celsius - 100.0) < 0.01

    assert Temperature.celsius_to_fahrenheit(0.0) == 32.0

    # Exercise 5: Abstract classes
    rect = Rectangle(10.0, 5.0)
    assert rect.area() == 50.0
    assert rect.perimeter() == 30.0

    circle = Circle(5.0)
    assert circle.area() > 78.0 and circle.area() < 79.0

    # Protocols
    canvas = Canvas()
    canvas.add(Square(10))
    canvas.add(Star(5))
    rendered = canvas.render()
    assert len(rendered) == 2

    # Exercise 6: Dataclasses
    p1 = Point(0.0, 0.0)
    p2 = Point(3.0, 4.0)
    assert p2.distance_to(p1) == 5.0

    person = Person("Alice", 30, "alice@example.com")
    assert person.name == "Alice"

    coord = Coordinate(40.7128, -74.0060)
    # coord.latitude = 50.0  # Would raise error (frozen)

    # Exercise 7: Composition
    engine = Engine(200)
    transmission = Transmission(6)
    car = Car(engine, transmission)
    assert "started" in car.start()
    assert "gear 2" in car.accelerate()

    # Exercise 8: Singleton
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    assert db1 is db2  # Same instance

    print("✅ All class definition tests passed!")
    return True


if __name__ == "__main__":
    print("Class Definition Mastery - ACE Practice Task (Iteration 5)")
    print("=" * 65)
    print("\nExecuting test suite...\n")
    test_class_definition_mastery()
    print("\n✅ Practice task complete!")
    print("Class definition proficiency: 29.3% → [measuring...]")
