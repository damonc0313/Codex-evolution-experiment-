def large_sccs(
    graph: dict[int, list[int]],  # Directed adjacency list
    min_size: int
) -> list[list[int]]:
    """
    Find all strongly connected components with at least min_size nodes.

    Args:
        graph: Directed graph as adjacency list
        min_size: Minimum component size to include

    Returns:
        List of SCCs (each SCC is sorted list of node IDs)
        SCCs sorted by size descending, then by smallest node ID
    """
    if not graph:
        return []

    # Tarjan's algorithm for finding SCCs
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []

    def strongconnect(node):
        # Set the depth index for this node
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True

        # Consider successors of node
        for neighbor in graph.get(node, []):
            if neighbor not in index:
                # Successor has not yet been visited; recurse on it
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif on_stack.get(neighbor, False):
                # Successor is on stack and hence in the current SCC
                lowlinks[node] = min(lowlinks[node], index[neighbor])

        # If node is a root node, pop the stack and generate an SCC
        if lowlinks[node] == index[node]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == node:
                    break
            sccs.append(scc)

    # Run Tarjan's algorithm on all nodes
    for node in graph:
        if node not in index:
            strongconnect(node)

    # Filter SCCs by min_size
    filtered_sccs = [scc for scc in sccs if len(scc) >= min_size]

    # Sort each SCC's nodes
    for scc in filtered_sccs:
        scc.sort()

    # Sort SCCs by size (descending), then by smallest node ID (ascending)
    filtered_sccs.sort(key=lambda scc: (-len(scc), scc[0]))

    return filtered_sccs
