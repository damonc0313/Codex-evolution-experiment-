# Task: Resource Allocation with Time Windows

Allocate limited resources to tasks with time windows to maximize value.

**Function signature:**
```python
def allocate_resources(
    resources: int,
    tasks: list[dict]  # {"start": int, "end": int, "resources_needed": int, "value": int}
) -> tuple[int, list[int]]:
    """
    Allocate resources to non-overlapping tasks to maximize total value.

    Args:
        resources: Total available resources
        tasks: List of tasks with time windows and resource requirements

    Returns:
        Tuple of (max_value, list_of_selected_task_indices)
    """
    pass
```

**Requirements:**
- Tasks selected must not overlap in time
- Total resources used cannot exceed limit
- Resources are reusable after task completes
- Maximize total value of completed tasks
- Return indices of selected tasks in sorted order
- Handle empty tasks list

**Example:**
```python
tasks = [
    {"start": 0, "end": 3, "resources_needed": 2, "value": 10},
    {"start": 1, "end": 4, "resources_needed": 3, "value": 15},
    {"start": 3, "end": 6, "resources_needed": 2, "value": 12}
]
allocate_resources(3, tasks) == (22, [0, 2])  # Task 0 and 2 don't overlap
```

**Difficulty:** Interval scheduling with resource constraints
