def pattern_cycle(
    graph: dict[int, list[int]],
    node_values: dict[int, str],
    pattern: list[str]
) -> list[int]:
    """
    Find a cycle in directed graph where node values match the pattern sequence.

    Args:
        graph: Directed graph as adjacency list
        node_values: Mapping from node to its string label
        pattern: Sequence of labels to find in cycle (can wrap around)

    Returns:
        List of nodes forming cycle matching pattern, or [] if none exists
    """
    if not pattern:
        return []

    def check_pattern_match(cycle: list[int]) -> tuple[bool, list[int]]:
        """Check if pattern appears consecutively in cycle (can wrap around)."""
        n = len(cycle)
        if n < len(pattern):
            return False, []

        cycle_values = [node_values.get(node, "") for node in cycle]

        # Try each starting position in the cycle
        for start in range(n):
            match = True
            for i in range(len(pattern)):
                if cycle_values[(start + i) % n] != pattern[i]:
                    match = False
                    break
            if match:
                # Return cycle rotated to start at matching position
                rotated = [cycle[(start + i) % n] for i in range(n)]
                return True, rotated

        return False, []

    # Check for self-loops first (special case: single node cycle)
    for node in graph:
        if node in graph.get(node, []):
            if len(pattern) == 1 and node_values.get(node) == pattern[0]:
                return [node]

    # Find cycles using DFS from each starting node
    for start in graph:
        def find_cycles(node, path, visited):
            """Generator that yields all simple cycles starting and ending at 'start'."""
            for neighbor in graph.get(node, []):
                if neighbor == start and len(path) > 1:
                    # Found a cycle back to start
                    yield path[:]
                elif neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    yield from find_cycles(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        for cycle in find_cycles(start, [start], {start}):
            match, rotated = check_pattern_match(cycle)
            if match:
                return rotated

    return []
