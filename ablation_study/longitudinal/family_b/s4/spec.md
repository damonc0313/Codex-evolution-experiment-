# Session 4: All-Pairs Shortest Paths (Floyd-Warshall)

## Task
Compute shortest paths between all pairs of nodes.

## Function Signature
```python
def floyd_warshall(graph: dict[int, list[tuple[int, int]]]) -> dict[tuple[int, int], int]:
    """
    Compute all-pairs shortest paths.

    Args:
        graph: Adjacency list (node -> list of (neighbor, weight))

    Returns:
        Dict mapping (src, dst) -> shortest distance
        Use float('inf') for unreachable pairs
    """
```

## Learning Transfer
Generalizes single-source (Dijkstra) to all pairs.
