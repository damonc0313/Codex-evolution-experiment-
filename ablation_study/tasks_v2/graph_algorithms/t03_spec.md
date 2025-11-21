# Task: Minimum Spanning Tree with Required Edges

Find MST that must include specific required edges.

**Function signature:**
```python
def constrained_mst(
    edges: list[tuple[int, int, int]],  # (u, v, weight)
    n: int,  # number of nodes (0 to n-1)
    required: set[tuple[int, int]]  # edges that must be included (u, v)
) -> tuple[int, list[tuple[int, int]]]:
    """
    Find MST that includes all required edges, or determine if impossible.

    Args:
        edges: List of (node1, node2, weight) for undirected graph
        n: Number of nodes
        required: Set of (u, v) edges that must be in MST

    Returns:
        Tuple of (total_weight, mst_edges)
        Returns (-1, []) if no valid MST with required edges exists
    """
    pass
```

**Requirements:**
- MST must include ALL required edges
- If required edges form a cycle, return (-1, [])
- If graph becomes disconnected, return (-1, [])
- Use Kruskal's or Prim's algorithm with modifications
- Edges are undirected (u,v) same as (v,u)

**Example:**
```python
edges = [(0,1,1), (0,2,4), (1,2,2), (1,3,5), (2,3,3)]
n = 4
constrained_mst(edges, n, {(0,1), (2,3)}) == (6, [(0,1), (1,2), (2,3)])
constrained_mst(edges, n, {(0,1), (1,2), (0,2)}) == (-1, [])  # Forms cycle
```

**Difficulty:** MST with hard constraints
