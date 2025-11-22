"""Session 3: Constrained Shortest Path"""
import heapq


def constrained_shortest(
    graph: dict[int, list[tuple[int, int]]],
    start: int,
    end: int,
    must_visit: set[int]
) -> tuple[int, list[int]]:
    """
    Find shortest path that visits all required nodes.

    Args:
        graph: Adjacency list (node -> list of (neighbor, weight))
        start: Starting node
        end: Target node
        must_visit: Set of nodes that must be on the path

    Returns:
        Tuple of (total_distance, path) or (-1, []) if impossible
    """
    # Build bidirectional graph (treat as undirected)
    bidir_graph = {}
    for node, neighbors in graph.items():
        if node not in bidir_graph:
            bidir_graph[node] = []
        for neighbor, weight in neighbors:
            bidir_graph[node].append((neighbor, weight))
            if neighbor not in bidir_graph:
                bidir_graph[neighbor] = []
            bidir_graph[neighbor].append((node, weight))

    # Remove start and end from must_visit (they're naturally visited)
    required = must_visit - {start, end}
    required_list = list(required)
    n_required = len(required_list)

    # Create mapping from required node to bit index
    node_to_bit = {node: i for i, node in enumerate(required_list)}

    # Full mask when all required nodes are visited
    full_mask = (1 << n_required) - 1

    # Get initial mask based on start node
    start_mask = 0
    if start in node_to_bit:
        start_mask |= (1 << node_to_bit[start])

    # State: (distance, node, visited_mask, path)
    # Use priority queue for Dijkstra
    pq = [(0, start, start_mask, [start])]

    # Track best distance for each (node, mask) state
    best = {(start, start_mask): 0}

    while pq:
        dist, node, mask, path = heapq.heappop(pq)

        # Skip if we've found a better path to this state
        if dist > best.get((node, mask), float('inf')):
            continue

        # Check if we've reached the end with all required nodes visited
        if node == end and mask == full_mask:
            return (dist, path)

        # Explore neighbors (using bidirectional graph)
        for neighbor, weight in bidir_graph.get(node, []):
            new_dist = dist + weight
            new_mask = mask

            # Update mask if neighbor is a required node
            if neighbor in node_to_bit:
                new_mask |= (1 << node_to_bit[neighbor])

            state = (neighbor, new_mask)
            if new_dist < best.get(state, float('inf')):
                best[state] = new_dist
                heapq.heappush(pq, (new_dist, neighbor, new_mask, path + [neighbor]))

    return (-1, [])
