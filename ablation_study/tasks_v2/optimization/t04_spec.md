# Task: Facility Location with Capacity

Locate k facilities to minimize total distance to clients, respecting capacity.

**Function signature:**
```python
def facility_location(
    clients: list[tuple[int, int]],  # (x, y) coordinates
    k: int,  # number of facilities to place
    capacity: int,  # max clients per facility
    candidate_locations: list[tuple[int, int]]  # possible facility locations
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
    pass
```

**Requirements:**
- Distance is Euclidean: sqrt((x1-x2)^2 + (y1-y2)^2)
- Each facility serves at most `capacity` clients
- Minimize sum of distances from clients to assigned facilities
- Use greedy heuristic or local search (NP-hard problem)
- All clients must be assigned

**Example:**
```python
clients = [(0,0), (10,0), (0,10), (10,10)]
candidates = [(5,0), (0,5), (5,10)]
k = 2
capacity = 2

# Choose facilities at (5,0) and (5,10)
# Assign clients optimally
facility_location(clients, k, capacity, candidates)
# Returns (total_dist, [0, 2], {0:0, 1:0, 2:2, 3:2})
```

**Difficulty:** NP-hard placement and assignment
