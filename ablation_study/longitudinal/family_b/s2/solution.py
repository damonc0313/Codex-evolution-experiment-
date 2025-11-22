"""Session 2: Weighted Shortest Path (Dijkstra)"""
import heapq


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
    # Same node case
    if start == end:
        return (0, [start])

    # Distance from start to each node
    distances = {start: 0}
    # Track the predecessor for path reconstruction
    predecessors = {}
    # Priority queue: (distance, node)
    pq = [(0, start)]

    while pq:
        dist, node = heapq.heappop(pq)

        # Skip if we've found a better path already
        if dist > distances.get(node, float('inf')):
            continue

        # Found the target
        if node == end:
            # Reconstruct path
            path = [end]
            current = end
            while current in predecessors:
                current = predecessors[current]
                path.append(current)
            path.reverse()
            return (dist, path)

        # Explore neighbors
        for neighbor, weight in graph.get(node, []):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                predecessors[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))

    return (-1, [])
