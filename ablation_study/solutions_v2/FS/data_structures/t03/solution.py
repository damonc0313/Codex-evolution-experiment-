"""
Interval Tree implementation supporting overlap queries.
Uses an augmented AVL tree for O(log n) operations.
"""

from typing import Any, Optional


class _Node:
    """Internal node for the interval tree."""
    __slots__ = ('interval_id', 'start', 'end', 'data',
                 'max_end', 'height', 'left', 'right')

    def __init__(self, interval_id: int, start: int, end: int, data: Any):
        self.interval_id = interval_id
        self.start = start
        self.end = end
        self.data = data
        self.max_end = end  # Maximum end in this subtree
        self.height = 1
        self.left: Optional[_Node] = None
        self.right: Optional[_Node] = None


class IntervalTree:
    """
    Tree structure for efficient interval overlap queries.
    Uses AVL tree augmented with max_end for interval operations.
    """

    def __init__(self):
        """Initialize empty interval tree."""
        self._root: Optional[_Node] = None
        self._next_id = 0
        self._id_to_interval: dict[int, tuple[int, int, Any]] = {}

    def _height(self, node: Optional[_Node]) -> int:
        """Get height of node (0 if None)."""
        return node.height if node else 0

    def _max_end(self, node: Optional[_Node]) -> int:
        """Get max_end of node (-inf if None)."""
        return node.max_end if node else float('-inf')

    def _update_node(self, node: _Node) -> None:
        """Update height and max_end of a node based on children."""
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        node.max_end = max(node.end,
                          self._max_end(node.left),
                          self._max_end(node.right))

    def _balance_factor(self, node: Optional[_Node]) -> int:
        """Get balance factor of node."""
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _rotate_right(self, y: _Node) -> _Node:
        """Right rotation around y."""
        x = y.left
        t2 = x.right

        x.right = y
        y.left = t2

        self._update_node(y)
        self._update_node(x)

        return x

    def _rotate_left(self, x: _Node) -> _Node:
        """Left rotation around x."""
        y = x.right
        t2 = y.left

        y.left = x
        x.right = t2

        self._update_node(x)
        self._update_node(y)

        return y

    def _balance(self, node: _Node) -> _Node:
        """Balance the node if needed and return new subtree root."""
        self._update_node(node)
        balance = self._balance_factor(node)

        # Left heavy
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right heavy
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _insert(self, node: Optional[_Node], new_node: _Node) -> _Node:
        """Insert new_node into subtree rooted at node, return new root."""
        if not node:
            return new_node

        # Use (start, interval_id) as key for stable ordering
        if (new_node.start, new_node.interval_id) < (node.start, node.interval_id):
            node.left = self._insert(node.left, new_node)
        else:
            node.right = self._insert(node.right, new_node)

        return self._balance(node)

    def insert(self, start: int, end: int, data: Any = None) -> int:
        """
        Insert interval [start, end] with optional data.
        Returns interval ID for later reference.
        """
        interval_id = self._next_id
        self._next_id += 1

        self._id_to_interval[interval_id] = (start, end, data)
        new_node = _Node(interval_id, start, end, data)
        self._root = self._insert(self._root, new_node)

        return interval_id

    def _find_min(self, node: _Node) -> _Node:
        """Find node with minimum key in subtree."""
        while node.left:
            node = node.left
        return node

    def _delete(self, node: Optional[_Node], start: int, interval_id: int) -> Optional[_Node]:
        """Delete node with given start and interval_id, return new root."""
        if not node:
            return None

        key = (start, interval_id)
        node_key = (node.start, node.interval_id)

        if key < node_key:
            node.left = self._delete(node.left, start, interval_id)
        elif key > node_key:
            node.right = self._delete(node.right, start, interval_id)
        else:
            # Found the node to delete
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                # Node has two children
                successor = self._find_min(node.right)
                # Copy successor data to this node
                node.interval_id = successor.interval_id
                node.start = successor.start
                node.end = successor.end
                node.data = successor.data
                # Delete successor from right subtree
                node.right = self._delete(node.right, successor.start, successor.interval_id)

        return self._balance(node)

    def delete(self, interval_id: int) -> bool:
        """Delete interval by ID. Returns True if existed."""
        if interval_id not in self._id_to_interval:
            return False

        start, end, data = self._id_to_interval[interval_id]
        del self._id_to_interval[interval_id]
        self._root = self._delete(self._root, start, interval_id)

        return True

    def _overlaps(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        """Check if two closed intervals overlap."""
        return start1 <= end2 and start2 <= end1

    def _find_overlapping(self, node: Optional[_Node], start: int, end: int,
                          result: list[tuple[int, int, int, Any]]) -> None:
        """Find all intervals in subtree that overlap with [start, end]."""
        if not node:
            return

        # If max_end in this subtree is less than query start, no overlaps possible
        if node.max_end < start:
            return

        # Search left subtree
        self._find_overlapping(node.left, start, end, result)

        # Check current node
        if self._overlaps(node.start, node.end, start, end):
            result.append((node.interval_id, node.start, node.end, node.data))

        # If node.start > end, no need to search right (all intervals in right have start >= node.start)
        if node.start <= end:
            self._find_overlapping(node.right, start, end, result)

    def find_overlapping(self, start: int, end: int) -> list[tuple[int, int, int, Any]]:
        """
        Find all intervals overlapping with [start, end].
        Returns list of (interval_id, start, end, data).
        """
        result: list[tuple[int, int, int, Any]] = []
        self._find_overlapping(self._root, start, end, result)
        return result
