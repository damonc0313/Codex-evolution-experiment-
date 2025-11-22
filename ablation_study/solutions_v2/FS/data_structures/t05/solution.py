class RollbackDSU:
    """
    Disjoint Set Union with operation history and rollback.

    Uses union-by-rank without path compression to enable efficient rollback.
    This gives O(log n) for find and union operations.
    """

    def __init__(self, n: int):
        """Initialize with n elements (0 to n-1)."""
        self.n = n
        self.parent = list(range(n))
        self.rank = [0] * n
        self.checkpoints = {}
        self.checkpoint_counter = 0

    def union(self, x: int, y: int) -> bool:
        """
        Union sets containing x and y.
        Returns True if they were in different sets.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        return True

    def find(self, x: int) -> int:
        """
        Find root of set containing x.

        Uses iterative traversal without path compression to support rollback.
        """
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def checkpoint(self) -> int:
        """
        Create checkpoint of current state.
        Returns checkpoint ID.
        """
        cp_id = self.checkpoint_counter
        self.checkpoint_counter += 1
        # Store a copy of the current state
        self.checkpoints[cp_id] = (self.parent.copy(), self.rank.copy())
        return cp_id

    def rollback(self, checkpoint_id: int) -> None:
        """Rollback to specified checkpoint state."""
        saved_parent, saved_rank = self.checkpoints[checkpoint_id]
        # Restore state from checkpoint
        self.parent = saved_parent.copy()
        self.rank = saved_rank.copy()

    def count_sets(self) -> int:
        """Return number of disjoint sets."""
        return sum(1 for i in range(self.n) if self.parent[i] == i)
