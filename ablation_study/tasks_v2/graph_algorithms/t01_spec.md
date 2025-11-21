# Task: Shortest Path with Forbidden Edges

Implement shortest path algorithm that avoids forbidden edge pairs.

**Function signature:**
```python
def path_avoiding_pairs(
    graph: dict[int, list[tuple[int, int]]],  # {node: [(neighbor, weight), ...]}
    start: int,
    end: int,
    forbidden_pairs: set[tuple[int, int]]  # {(node1, node2), ...} - cannot traverse consecutively
) -> tuple[int, list[int]]:
    """
    Find shortest path where no two consecutive edges are in forbidden_pairs.

    Args:
        graph: Weighted adjacency list
        start: Start node
        end: End node
        forbidden_pairs: Set of (u, v) pairs - if edge to u is taken, cannot immediately take edge to v

    Returns:
        Tuple of (path_length, path_nodes) or (-1, []) if no valid path
    """
    pass
```

**Requirements:**
- Modified Dijkstra or dynamic programming
- Forbidden pairs are ordered: (u, v) means "if currently at u, cannot go to v next"
- Path length is sum of edge weights
- Return actual path, not just distance
- Handle disconnected graphs (return -1)
- Self-loops and duplicate edges possible

**Example:**
```python
graph = {
    0: [(1, 5), (2, 10)],
    1: [(2, 3), (3, 20)],
    2: [(3, 2)],
    3: []
}
path_avoiding_pairs(graph, 0, 3, set()) == (10, [0, 2, 3])
path_avoiding_pairs(graph, 0, 3, {(2, 3)}) == (25, [0, 1, 3])  # Must avoid 2->3
```

**Difficulty:** Modified shortest path with state tracking
