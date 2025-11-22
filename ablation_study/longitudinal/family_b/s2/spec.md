# Session 2: Weighted Shortest Path (Dijkstra)

## Task
Find the shortest weighted path using Dijkstra's algorithm.

## Function Signature
```python
def dijkstra(graph: dict[int, list[tuple[int, int]]], start: int, end: int) -> tuple[int, list[int]]:
    """
    Find shortest weighted path from start to end.

    Args:
        graph: Adjacency list (node -> list of (neighbor, weight))
        start: Starting node
        end: Target node

    Returns:
        Tuple of (total_distance, path) or (-1, []) if no path
    """
```

## Examples
```python
graph = {0: [(1, 5), (2, 2)], 1: [(3, 1)], 2: [(1, 1), (3, 7)], 3: []}
dijkstra(graph, 0, 3) == (4, [0, 2, 1, 3])  # 2 + 1 + 1 = 4
```

## Learning Transfer
Extends BFS with priority queue for weighted edges.
