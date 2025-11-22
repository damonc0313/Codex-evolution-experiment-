class RangeQueryTree:
    """
    Data structure for efficient range sum queries and point updates.
    Uses a segment tree to achieve O(log n) for all operations.
    """

    def __init__(self, arr: list[int]):
        """Initialize with array."""
        self.n = len(arr)
        if self.n == 0:
            self.sum_tree = []
            self.max_tree = []
            return

        # Size of segment tree array (4 * n is safe upper bound)
        self.size = 4 * self.n
        self.sum_tree = [0] * self.size
        self.max_tree = [float('-inf')] * self.size
        self.arr = arr[:]

        # Build the segment tree
        self._build(0, 0, self.n - 1)

    def _build(self, node: int, start: int, end: int) -> None:
        """Build segment tree recursively."""
        if start == end:
            # Leaf node
            self.sum_tree[node] = self.arr[start]
            self.max_tree[node] = self.arr[start]
        else:
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2

            self._build(left_child, start, mid)
            self._build(right_child, mid + 1, end)

            self.sum_tree[node] = self.sum_tree[left_child] + self.sum_tree[right_child]
            self.max_tree[node] = max(self.max_tree[left_child], self.max_tree[right_child])

    def update(self, index: int, value: int) -> None:
        """Set arr[index] = value."""
        if self.n == 0 or index < 0 or index >= self.n:
            return
        self.arr[index] = value
        self._update(0, 0, self.n - 1, index, value)

    def _update(self, node: int, start: int, end: int, index: int, value: int) -> None:
        """Update segment tree recursively."""
        if start == end:
            # Leaf node
            self.sum_tree[node] = value
            self.max_tree[node] = value
        else:
            mid = (start + end) // 2
            left_child = 2 * node + 1
            right_child = 2 * node + 2

            if index <= mid:
                self._update(left_child, start, mid, index, value)
            else:
                self._update(right_child, mid + 1, end, index, value)

            self.sum_tree[node] = self.sum_tree[left_child] + self.sum_tree[right_child]
            self.max_tree[node] = max(self.max_tree[left_child], self.max_tree[right_child])

    def range_sum(self, left: int, right: int) -> int:
        """Return sum of arr[left:right+1] (inclusive)."""
        if self.n == 0 or left > right:
            return 0
        return self._range_sum(0, 0, self.n - 1, left, right)

    def _range_sum(self, node: int, start: int, end: int, left: int, right: int) -> int:
        """Query range sum recursively."""
        # No overlap
        if right < start or left > end:
            return 0

        # Complete overlap
        if left <= start and end <= right:
            return self.sum_tree[node]

        # Partial overlap
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2

        left_sum = self._range_sum(left_child, start, mid, left, right)
        right_sum = self._range_sum(right_child, mid + 1, end, left, right)

        return left_sum + right_sum

    def range_max(self, left: int, right: int) -> int:
        """Return max of arr[left:right+1] (inclusive)."""
        if self.n == 0 or left > right:
            return float('-inf')
        return self._range_max(0, 0, self.n - 1, left, right)

    def _range_max(self, node: int, start: int, end: int, left: int, right: int) -> int:
        """Query range max recursively."""
        # No overlap
        if right < start or left > end:
            return float('-inf')

        # Complete overlap
        if left <= start and end <= right:
            return self.max_tree[node]

        # Partial overlap
        mid = (start + end) // 2
        left_child = 2 * node + 1
        right_child = 2 * node + 2

        left_max = self._range_max(left_child, start, mid, left, right)
        right_max = self._range_max(right_child, mid + 1, end, left, right)

        return max(left_max, right_max)
