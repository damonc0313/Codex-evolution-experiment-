# Task: Strongly Connected Components with Size Constraint

Find all strongly connected components with at least k nodes.

**Function signature:**
```python
def large_sccs(
    graph: dict[int, list[int]],  # Directed adjacency list
    min_size: int
) -> list[list[int]]:
    """
    Find all strongly connected components with at least min_size nodes.

    Args:
        graph: Directed graph as adjacency list
        min_size: Minimum component size to include

    Returns:
        List of SCCs (each SCC is sorted list of node IDs)
        SCCs sorted by size descending, then by smallest node ID
    """
    pass
```

**Requirements:**
- Use Tarjan's or Kosaraju's algorithm
- Only return SCCs with size >= min_size
- Sort results by size (descending), breaking ties by smallest node in component
- Each component's nodes should be sorted
- Handle empty graph

**Example:**
```python
graph = {
    0: [1], 1: [2], 2: [0],  # SCC: {0,1,2}
    3: [4], 4: [3],           # SCC: {3,4}
    5: []                      # SCC: {5}
}
large_sccs(graph, 2) == [[0,1,2], [3,4]]  # Size >=2
large_sccs(graph, 3) == [[0,1,2]]         # Size >=3
```

**Difficulty:** SCC detection with filtering and sorting
