# Session 5: TSP Nearest Neighbor Heuristic

## Task
Approximate solution to Traveling Salesman Problem using nearest neighbor heuristic.

## Function Signature
```python
def tsp_nearest_neighbor(
    distances: dict[tuple[int, int], int],
    start: int
) -> tuple[int, list[int]]:
    """
    Find approximate TSP tour using nearest neighbor heuristic.

    Args:
        distances: Dict mapping (node_a, node_b) -> distance
                   (symmetric: d[a,b] == d[b,a])
        start: Starting node for the tour

    Returns:
        Tuple of (total_distance, tour)
        Tour is a list of nodes visited in order, ending back at start
    """
```

## Learning Transfer
Applies graph traversal concepts to optimization problem.
Uses path finding concepts from all previous sessions.
