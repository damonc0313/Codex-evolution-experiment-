# Session 1: Basic BFS Path Finding

## Task
Find a path from start to end using Breadth-First Search.

## Function Signature
```python
def bfs_path(graph: dict[int, list[int]], start: int, end: int) -> list[int]:
    """
    Find any path from start to end using BFS.

    Args:
        graph: Adjacency list (node -> list of neighbors)
        start: Starting node
        end: Target node

    Returns:
        Path as list of nodes from start to end, or [] if no path
    """
```

## Examples
```python
graph = {0: [1, 2], 1: [3], 2: [3], 3: []}
bfs_path(graph, 0, 3) == [0, 1, 3]  # or [0, 2, 3]
bfs_path(graph, 0, 4) == []  # Node 4 doesn't exist
```

## Learning Goal
Understand BFS queue mechanics and path reconstruction.
