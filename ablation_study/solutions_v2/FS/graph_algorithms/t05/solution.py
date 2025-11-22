"""
Bipartite Matching with Preferences

Finds maximum cardinality bipartite matching, using preference scores as tiebreaker.
Uses the Hungarian algorithm with weight transformation to prioritize cardinality.
"""

from typing import Dict, List, Tuple


def weighted_matching(
    left: List[str],
    right: List[str],
    edges: Dict[Tuple[str, str], int]
) -> Tuple[int, Dict[str, str]]:
    """
    Find maximum cardinality matching, maximizing total preference score as tiebreaker.

    Args:
        left: Nodes in left partition
        right: Nodes in right partition
        edges: Preference scores for each possible edge {(left_node, right_node): score}

    Returns:
        Tuple of (matching_size, matching_dict)
        matching_dict maps left_node -> right_node
    """
    if not left or not right or not edges:
        return (0, {})

    n = len(left)
    m = len(right)

    # Create index mappings
    left_to_idx = {node: i for i, node in enumerate(left)}
    right_to_idx = {node: i for i, node in enumerate(right)}

    # Determine large constant for cardinality priority
    # Adding LARGE to each edge weight ensures that any additional match
    # is always worth more than any weight difference
    max_weight = max(abs(w) for w in edges.values()) if edges else 1
    LARGE = max_weight * max(n, m) + 1

    # Build weight matrix for maximum weight matching
    # We'll use -weight for the Hungarian algorithm (which minimizes)
    size = max(n, m)

    # Use a large finite number for "infinity" to avoid float issues
    # This should be larger than any possible real edge cost
    BIG = LARGE * size + max_weight + 1

    # cost[i][j] represents the cost of matching left i to right j
    # For real edges: cost = -(weight + LARGE) to maximize
    # For non-edges/dummy edges: cost = BIG (effectively never chosen)
    cost = [[BIG] * size for _ in range(size)]

    # Track which edges actually exist
    has_edge = [[False] * size for _ in range(size)]

    for (l, r), w in edges.items():
        if l in left_to_idx and r in right_to_idx:
            i, j = left_to_idx[l], right_to_idx[r]
            cost[i][j] = -(w + LARGE)  # Negate for minimization
            has_edge[i][j] = True

    # Run Hungarian algorithm for minimum cost assignment
    assignment = _hungarian_algorithm(cost, size)

    # Extract valid matches from assignment
    matching = {}
    for i in range(n):
        j = assignment[i]
        if j < m and has_edge[i][j]:
            matching[left[i]] = right[j]

    return (len(matching), matching)


def _hungarian_algorithm(cost: List[List[float]], n: int) -> List[int]:
    """
    Hungarian algorithm for minimum cost perfect matching on n x n cost matrix.

    Returns assignment where assignment[i] = j means row i is matched to column j.
    """
    INF = float('inf')

    # Potentials for rows and columns (1-indexed for convenience)
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)

    # p[j] = row matched to column j (0 means unmatched, 1-indexed rows)
    p = [0] * (n + 1)

    # way[j] = previous column in augmenting path
    way = [0] * (n + 1)

    for i in range(1, n + 1):
        # Start augmenting path from row i
        p[0] = i
        j0 = 0  # Current column (0 is virtual starting point)

        minv = [INF] * (n + 1)  # Minimum reduced cost to reach each column
        used = [False] * (n + 1)  # Whether column has been visited

        # Find augmenting path
        while p[j0] != 0:
            used[j0] = True
            i0 = p[j0]  # Current row
            delta = INF
            j1 = 0  # Next column

            # Relax edges from current row
            for j in range(1, n + 1):
                if not used[j]:
                    # Reduced cost of edge (i0, j)
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            # Update potentials
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1

        # Augment along the path
        while j0 != 0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    # Build assignment array (0-indexed)
    assignment = [-1] * n
    for j in range(1, n + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1

    return assignment
