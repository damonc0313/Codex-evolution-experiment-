# Session 3: Constrained Shortest Path

## Task
Find shortest path that must visit certain required nodes.

## Function Signature
```python
def constrained_shortest(
    graph: dict[int, list[tuple[int, int]]],
    start: int,
    end: int,
    must_visit: set[int]
) -> tuple[int, list[int]]:
    """
    Find shortest path that visits all required nodes.

    Args:
        graph: Adjacency list (node -> list of (neighbor, weight))
        start: Starting node
        end: Target node
        must_visit: Set of nodes that must be on the path

    Returns:
        Tuple of (total_distance, path) or (-1, []) if impossible
    """
```

## Learning Transfer
Combines Dijkstra (S2) with state tracking (like constrained LCS).
