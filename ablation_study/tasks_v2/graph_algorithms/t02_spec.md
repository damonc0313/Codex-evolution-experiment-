# Task: Detect Cycle with Specific Pattern

Find if graph contains a cycle matching a specific node value pattern.

**Function signature:**
```python
def pattern_cycle(
    graph: dict[int, list[int]],  # Adjacency list
    node_values: dict[int, str],   # Node labels
    pattern: list[str]              # Pattern to match in cycle
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
    pass
```

**Requirements:**
- Pattern must appear consecutively in the cycle (wrapping allowed)
- Return any valid cycle, or empty list if none exists
- Cycle must be simple (no repeated nodes except start/end)
- Pattern matching is exact (case-sensitive)
- Handle graphs with no cycles

**Example:**
```python
graph = {0: [1], 1: [2], 2: [0, 3], 3: [1]}
values = {0: "A", 1: "B", 2: "C", 3: "D"}
pattern_cycle(graph, values, ["A", "B", "C"]) == [0, 1, 2]  # Cycle 0->1->2->0
pattern_cycle(graph, values, ["B", "C", "A"]) == [1, 2, 0]  # Same cycle, different start
pattern_cycle(graph, values, ["X", "Y"]) == []  # No match
```

**Difficulty:** Cycle detection with pattern matching
