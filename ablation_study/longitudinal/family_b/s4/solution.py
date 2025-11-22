"""Session 4: All-Pairs Shortest Paths (Floyd-Warshall)"""


def floyd_warshall(graph: dict[int, list[tuple[int, int]]]) -> dict[tuple[int, int], int]:
    """
    Compute all-pairs shortest paths.

    Args:
        graph: Adjacency list (node -> list of (neighbor, weight))

    Returns:
        Dict mapping (src, dst) -> shortest distance
        Use float('inf') for unreachable pairs
    """
    # Get all nodes
    nodes = set(graph.keys())
    for neighbors in graph.values():
        for neighbor, _ in neighbors:
            nodes.add(neighbor)
    nodes = sorted(nodes)
    n = len(nodes)

    # Create node to index mapping
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize distance matrix
    dist = [[float('inf')] * n for _ in range(n)]

    # Distance to self is 0
    for i in range(n):
        dist[i][i] = 0

    # Initialize with direct edges
    for node, neighbors in graph.items():
        i = node_to_idx[node]
        for neighbor, weight in neighbors:
            j = node_to_idx[neighbor]
            dist[i][j] = min(dist[i][j], weight)

    # Floyd-Warshall algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Convert back to dictionary
    result = {}
    for i, src in enumerate(nodes):
        for j, dst in enumerate(nodes):
            result[(src, dst)] = dist[i][j]

    return result
