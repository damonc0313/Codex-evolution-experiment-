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
    # Union-Find data structure
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]

    def union(x: int, y: int) -> bool:
        """Union two sets. Returns False if already in same set (would form cycle)."""
        px, py = find(x), find(y)
        if px == py:
            return False  # Already connected - would form cycle
        # Union by rank
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True

    # Build edge lookup with weights (handle both directions)
    edge_weights = {}
    for u, v, w in edges:
        key = (min(u, v), max(u, v))
        if key not in edge_weights:
            edge_weights[key] = w
        else:
            edge_weights[key] = min(edge_weights[key], w)  # Take minimum if duplicates

    mst_edges = []
    total_weight = 0

    # Step 1: Add all required edges first
    for u, v in required:
        key = (min(u, v), max(u, v))

        # Check if edge exists in graph
        if key not in edge_weights:
            return (-1, [])  # Required edge doesn't exist

        # Check if adding this edge would form a cycle
        if not union(u, v):
            return (-1, [])  # Required edges form a cycle

        mst_edges.append((u, v))
        total_weight += edge_weights[key]

    # Normalize required edges for comparison
    required_normalized = {(min(u, v), max(u, v)) for u, v in required}

    # Step 2: Sort remaining edges by weight and add using Kruskal's algorithm
    remaining_edges = []
    for (u, v), w in edge_weights.items():
        if (u, v) not in required_normalized:
            remaining_edges.append((w, u, v))

    remaining_edges.sort()  # Sort by weight

    for w, u, v in remaining_edges:
        if union(u, v):  # If adding this edge doesn't form a cycle
            mst_edges.append((u, v))
            total_weight += w

    # Step 3: Check if MST is complete (should have n-1 edges)
    if len(mst_edges) != n - 1:
        return (-1, [])  # Graph is disconnected

    return (total_weight, mst_edges)
