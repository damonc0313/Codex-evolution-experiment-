import pytest
import math
from solution import facility_location


def euclidean(p1, p2):
    """Helper to compute Euclidean distance."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def test_simple_placement():
    """Two clients, one facility."""
    clients = [(0, 0), (10, 0)]
    candidates = [(5, 0), (0, 0), (10, 0)]
    k = 1
    capacity = 2
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Best: facility at (5,0) serves both
    assert len(facilities) == 1
    assert facilities[0] == 0  # Candidate (5,0)
    assert total_dist == 10.0  # 5 + 5


def test_capacity_constraint():
    """Capacity forces multiple facilities."""
    clients = [(0, 0), (1, 0), (2, 0)]
    candidates = [(0, 0), (2, 0)]
    k = 2
    capacity = 2
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Must use both facilities due to capacity
    assert len(facilities) == 2
    assert set(facilities) == {0, 1}
    # All clients assigned
    assert len(assignments) == 3


def test_single_client():
    """One client - pick nearest facility."""
    clients = [(5, 5)]
    candidates = [(0, 0), (5, 5), (10, 10)]
    k = 1
    capacity = 1
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    assert total_dist == 0.0  # Exact match at candidate 1
    assert facilities == [1]
    assert assignments == {0: 1}


def test_all_clients_assigned():
    """Every client has an assignment."""
    clients = [(i, i) for i in range(5)]
    candidates = [(0, 0), (2, 2), (4, 4)]
    k = 2
    capacity = 3
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    assert len(assignments) == 5
    assert set(assignments.keys()) == {0, 1, 2, 3, 4}


def test_assignment_respects_capacity():
    """No facility exceeds capacity."""
    clients = [(i, 0) for i in range(10)]
    candidates = [(5, 0)]
    k = 1
    capacity = 5
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Count clients per facility
    facility_counts = {}
    for client_idx, facility_idx in assignments.items():
        facility_counts[facility_idx] = facility_counts.get(facility_idx, 0) + 1
    for count in facility_counts.values():
        assert count <= capacity


def test_optimal_greedy():
    """Greedy heuristic finds reasonable solution."""
    clients = [(0, 0), (10, 0), (0, 10), (10, 10)]
    candidates = [(5, 0), (0, 5), (5, 10), (10, 5)]
    k = 2
    capacity = 2
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Should pick good facilities
    assert len(facilities) == 2
    assert total_dist < 40  # Better than worst case


def test_k_exceeds_candidates():
    """Handle k larger than available candidates."""
    clients = [(0, 0), (1, 1)]
    candidates = [(0, 0)]
    k = 3
    capacity = 5
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Can only use 1 facility
    assert len(facilities) <= len(candidates)


def test_distance_calculation():
    """Verify Euclidean distance used."""
    clients = [(0, 0), (3, 4)]
    candidates = [(0, 0)]
    k = 1
    capacity = 2
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Distance from (3,4) to (0,0) is 5.0
    assert total_dist == 5.0


def test_multiple_facilities():
    """Multiple facilities reduce total distance."""
    clients = [(0, 0), (100, 0)]
    candidates = [(0, 0), (100, 0), (50, 0)]
    k = 2
    capacity = 1
    total_dist, facilities, assignments = facility_location(clients, k, capacity, candidates)
    # Best: use facilities at (0,0) and (100,0)
    assert total_dist == 0.0
    assert set(facilities) == {0, 1}
