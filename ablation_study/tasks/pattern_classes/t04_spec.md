# Task: Shopping Cart

Implement a ShoppingCart class that manages items with quantities and calculates totals.

**Class specification:**
```python
class ShoppingCart:
    """Shopping cart with item management."""

    def __init__(self):
        """Initialize empty cart."""
        pass

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """Add item or increase quantity if already in cart."""
        pass

    def remove_item(self, name: str, quantity: int = 1) -> bool:
        """Remove quantity of item. Return True if successful, False if item not found."""
        pass

    def get_item_count(self, name: str) -> int:
        """Get quantity of specific item (0 if not in cart)."""
        pass

    def get_total(self) -> float:
        """Calculate total cost of all items."""
        pass

    def get_items(self) -> dict[str, dict]:
        """Get all items as dict: {name: {'price': float, 'quantity': int}}"""
        pass

    def clear(self) -> None:
        """Remove all items from cart."""
        pass
```

**Requirements:**
- Adding existing item increases quantity
- Removing more than available removes item completely
- Prices must be positive
- Quantities must be positive integers
- Total calculates sum of (price * quantity) for all items
