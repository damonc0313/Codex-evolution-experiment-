# Task: Bipartite Matching with Preferences

Find maximum bipartite matching considering preference scores.

**Function signature:**
```python
def weighted_matching(
    left: list[str],   # Left partition node IDs
    right: list[str],  # Right partition node IDs
    edges: dict[tuple[str, str], int]  # {(left_node, right_node): preference_score}
) -> tuple[int, dict[str, str]]:
    """
    Find maximum cardinality matching, maximizing total preference score as tiebreaker.

    Args:
        left: Nodes in left partition
        right: Nodes in right partition
        edges: Preference scores for each possible edge

    Returns:
        Tuple of (matching_size, matching_dict)
        matching_dict maps left_node -> right_node
    """
    pass
```

**Requirements:**
- Maximize matching size FIRST (cardinality)
- Among max-cardinality matchings, pick one with highest total preference score
- Use Hungarian algorithm, augmenting paths, or similar
- Each node matched at most once
- Return empty dict if no matching possible

**Example:**
```python
left = ["A1", "A2"]
right = ["B1", "B2"]
edges = {
    ("A1", "B1"): 10, ("A1", "B2"): 5,
    ("A2", "B1"): 3,  ("A2", "B2"): 8
}
# Max cardinality = 2
# Best matching: A1->B1(10) + A2->B2(8) = 18
weighted_matching(left, right, edges) == (2, {"A1": "B1", "A2": "B2"})
```

**Difficulty:** Bipartite matching with optimization
