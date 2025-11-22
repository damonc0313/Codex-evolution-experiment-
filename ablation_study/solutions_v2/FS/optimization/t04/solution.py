import math
from itertools import combinations


def euclidean(p1: tuple[int, int], p2: tuple[int, int]) -> float:
    """Compute Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def facility_location(
    clients: list[tuple[int, int]],
    k: int,
    capacity: int,
    candidate_locations: list[tuple[int, int]]
) -> tuple[float, list[int], dict[int, int]]:
    """
    Choose k facilities to minimize total client-to-facility distance.

    Args:
        clients: Client locations
        k: Number of facilities to place
        capacity: Maximum clients assignable to one facility
        candidate_locations: Possible facility placements

    Returns:
        Tuple of (total_distance, facility_indices, assignments)
        facility_indices: which candidates selected
        assignments: dict mapping client_idx -> facility_idx
    """
    n_clients = len(clients)
    n_candidates = len(candidate_locations)

    # Handle edge cases
    if n_clients == 0 or n_candidates == 0 or k == 0:
        return (0.0, [], {})

    # Limit k to available candidates
    k = min(k, n_candidates)

    # Precompute all distances from clients to candidates
    distances = {}
    for i, client in enumerate(clients):
        for j, candidate in enumerate(candidate_locations):
            distances[(i, j)] = euclidean(client, candidate)

    def compute_assignment(selected_facilities: list[int]) -> tuple[float, dict[int, int]]:
        """
        Compute optimal assignment of clients to selected facilities.
        Uses greedy approach: repeatedly assign client-facility pair with minimum distance.
        """
        assignments = {}
        facility_remaining_capacity = {f: capacity for f in selected_facilities}

        total_dist = 0.0
        unassigned = set(range(n_clients))

        while unassigned:
            # Find the (client, facility) pair with minimum distance
            best_client = None
            best_facility = None
            best_dist = float('inf')

            for client_idx in unassigned:
                for f in selected_facilities:
                    if facility_remaining_capacity[f] > 0:
                        d = distances[(client_idx, f)]
                        if d < best_dist:
                            best_dist = d
                            best_client = client_idx
                            best_facility = f

            if best_facility is None:
                # No more capacity available
                break

            assignments[best_client] = best_facility
            facility_remaining_capacity[best_facility] -= 1
            total_dist += best_dist
            unassigned.remove(best_client)

        return total_dist, assignments

    best_total_dist = float('inf')
    best_facilities = []
    best_assignments = {}

    # If problem size is small enough, try all combinations for optimal solution
    if n_candidates <= 15 and k <= 6:
        for selected in combinations(range(n_candidates), k):
            total_dist, assignments = compute_assignment(list(selected))
            if total_dist < best_total_dist:
                best_total_dist = total_dist
                best_facilities = list(selected)
                best_assignments = assignments
    else:
        # Greedy facility selection for larger instances
        selected = []
        remaining = list(range(n_candidates))

        for _ in range(k):
            best_facility = None
            best_cost = float('inf')

            for candidate in remaining:
                test_selection = selected + [candidate]
                total_dist, _ = compute_assignment(test_selection)
                if total_dist < best_cost:
                    best_cost = total_dist
                    best_facility = candidate

            if best_facility is not None:
                selected.append(best_facility)
                remaining.remove(best_facility)

        total_dist, assignments = compute_assignment(selected)
        best_total_dist = total_dist
        best_facilities = selected
        best_assignments = assignments

    return (best_total_dist, best_facilities, best_assignments)
