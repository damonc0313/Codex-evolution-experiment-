class ShoppingCart:
    """
    Shopping cart with item management.

    FS Strategy: Dict-based storage for O(1) lookups, methods for consistency.
    Learning: Connects to comprehension t05 (grouping/aggregation) but with mutation.
    """

    def __init__(self):
        """Initialize empty cart."""
        self._items = {}  # {name: {'price': float, 'quantity': int}}

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        """Add item or increase quantity if already in cart."""
        if name in self._items:
            # Item exists, increase quantity
            self._items[name]['quantity'] += quantity
        else:
            # New item
            self._items[name] = {'price': price, 'quantity': quantity}

    def remove_item(self, name: str, quantity: int = 1) -> bool:
        """Remove quantity of item. Return True if successful, False if item not found."""
        if name not in self._items:
            return False

        self._items[name]['quantity'] -= quantity

        # Remove item if quantity reaches zero or below
        if self._items[name]['quantity'] <= 0:
            del self._items[name]

        return True

    def get_item_count(self, name: str) -> int:
        """Get quantity of specific item (0 if not in cart)."""
        if name not in self._items:
            return 0
        return self._items[name]['quantity']

    def get_total(self) -> float:
        """Calculate total cost of all items."""
        return sum(
            item['price'] * item['quantity']
            for item in self._items.values()
        )

    def get_items(self) -> dict[str, dict]:
        """Get all items as dict: {name: {'price': float, 'quantity': int}}"""
        return self._items.copy()

    def clear(self) -> None:
        """Remove all items from cart."""
        self._items.clear()
