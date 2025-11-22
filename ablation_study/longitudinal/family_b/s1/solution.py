"""Session 1: Basic BFS Path Finding"""
from collections import deque


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
    # Same node case
    if start == end:
        return [start]

    # Check if start exists in graph
    if start not in graph:
        return []

    # BFS with path tracking
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()

        for neighbor in graph.get(node, []):
            if neighbor == end:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []
