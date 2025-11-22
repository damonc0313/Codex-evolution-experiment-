"""Session 5: TSP Nearest Neighbor Heuristic"""


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
    # Get all nodes from distances
    nodes = set()
    for (a, b) in distances.keys():
        nodes.add(a)
        nodes.add(b)

    # Handle single node case
    if not nodes:
        return (0, [start])

    # Add start to nodes if not present
    nodes.add(start)

    # Initialize tour
    tour = [start]
    visited = {start}
    total_distance = 0

    # Greedily select nearest unvisited node
    current = start
    while len(visited) < len(nodes):
        nearest = None
        nearest_dist = float('inf')

        for node in nodes:
            if node not in visited:
                # Check distance from current to node
                dist = distances.get((current, node), float('inf'))
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = node

        if nearest is None or nearest_dist == float('inf'):
            break

        tour.append(nearest)
        visited.add(nearest)
        total_distance += nearest_dist
        current = nearest

    # Return to start
    if len(tour) > 1:
        return_dist = distances.get((current, start), 0)
        total_distance += return_dist
        tour.append(start)

    return (total_distance, tour)
