import heapq


def path_avoiding_pairs(
    graph: dict[int, list[tuple[int, int]]],  # {node: [(neighbor, weight), ...]}
    start: int,
    end: int,
    forbidden_pairs: set[tuple[int, int]]  # {(node1, node2), ...} - cannot traverse consecutively
) -> tuple[int, list[int]]:
    """
    Find shortest path where no two consecutive edges are in forbidden_pairs.

    Args:
        graph: Weighted adjacency list
        start: Start node
        end: End node
        forbidden_pairs: Set of (u, v) pairs - if edge to u is taken, cannot immediately take edge to v

    Returns:
        Tuple of (path_length, path_nodes) or (-1, []) if no valid path
    """
    # Handle case where start equals end
    if start == end:
        return (0, [start])

    # Priority queue: (distance, current_node, path)
    # Using Dijkstra's algorithm with forbidden edge checking
    pq = [(0, start, [start])]
    visited = set()

    while pq:
        dist, node, path = heapq.heappop(pq)

        # Found the destination
        if node == end:
            return (dist, path)

        # Skip if already visited
        if node in visited:
            continue
        visited.add(node)

        # Explore neighbors
        for neighbor, weight in graph.get(node, []):
            # Check if edge is forbidden and neighbor not yet visited
            if (node, neighbor) not in forbidden_pairs and neighbor not in visited:
                heapq.heappush(pq, (dist + weight, neighbor, path + [neighbor]))

    # No valid path found
    return (-1, [])
