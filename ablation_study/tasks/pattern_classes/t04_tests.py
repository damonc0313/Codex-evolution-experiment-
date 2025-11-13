import pytest
from solution import ShoppingCart

def test_initialization():
    cart = ShoppingCart()
    assert cart.get_total() == 0
    assert cart.get_items() == {}

def test_add_single_item():
    cart = ShoppingCart()
    cart.add_item("Apple", 1.50)
    assert cart.get_item_count("Apple") == 1
    assert cart.get_total() == 1.50

def test_add_multiple_quantity():
    cart = ShoppingCart()
    cart.add_item("Orange", 2.00, quantity=5)
    assert cart.get_item_count("Orange") == 5
    assert cart.get_total() == 10.00

def test_add_existing_item():
    cart = ShoppingCart()
    cart.add_item("Banana", 0.50, quantity=2)
    cart.add_item("Banana", 0.50, quantity=3)
    assert cart.get_item_count("Banana") == 5
    assert cart.get_total() == 2.50

def test_remove_item():
    cart = ShoppingCart()
    cart.add_item("Apple", 1.50, quantity=5)
    result = cart.remove_item("Apple", quantity=2)
    assert result is True
    assert cart.get_item_count("Apple") == 3

def test_remove_all_of_item():
    cart = ShoppingCart()
    cart.add_item("Orange", 2.00, quantity=3)
    cart.remove_item("Orange", quantity=3)
    assert cart.get_item_count("Orange") == 0
    assert "Orange" not in cart.get_items()

def test_remove_more_than_available():
    cart = ShoppingCart()
    cart.add_item("Banana", 0.50, quantity=2)
    cart.remove_item("Banana", quantity=10)
    assert cart.get_item_count("Banana") == 0

def test_remove_nonexistent_item():
    cart = ShoppingCart()
    result = cart.remove_item("Ghost")
    assert result is False

def test_get_items():
    cart = ShoppingCart()
    cart.add_item("Apple", 1.50, quantity=2)
    cart.add_item("Orange", 2.00, quantity=1)

    items = cart.get_items()
    assert items == {
        "Apple": {"price": 1.50, "quantity": 2},
        "Orange": {"price": 2.00, "quantity": 1}
    }

def test_total_calculation():
    cart = ShoppingCart()
    cart.add_item("Item1", 10.00, quantity=2)
    cart.add_item("Item2", 5.50, quantity=3)
    cart.add_item("Item3", 1.25, quantity=4)

    expected = (10.00 * 2) + (5.50 * 3) + (1.25 * 4)
    assert cart.get_total() == pytest.approx(expected)

def test_clear():
    cart = ShoppingCart()
    cart.add_item("Apple", 1.50, quantity=5)
    cart.add_item("Orange", 2.00, quantity=3)
    cart.clear()

    assert cart.get_total() == 0
    assert cart.get_items() == {}
    assert cart.get_item_count("Apple") == 0

def test_decimal_prices():
    cart = ShoppingCart()
    cart.add_item("Item", 1.99, quantity=3)
    assert cart.get_total() == pytest.approx(5.97)

def test_item_count_nonexistent():
    cart = ShoppingCart()
    assert cart.get_item_count("Nonexistent") == 0
