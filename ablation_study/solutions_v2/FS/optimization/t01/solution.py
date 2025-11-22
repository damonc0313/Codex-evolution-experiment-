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
    if not tasks:
        return (0, [])

    n = len(tasks)

    # Create indexed tasks and filter by resource constraint
    # (original_index, task)
    indexed_tasks = []
    for i, task in enumerate(tasks):
        if task["resources_needed"] <= resources:
            indexed_tasks.append((i, task))

    if not indexed_tasks:
        return (0, [])

    # Sort by end time
    indexed_tasks.sort(key=lambda x: x[1]["end"])

    m = len(indexed_tasks)

    def find_latest_compatible(j):
        """Find the latest task index that ends <= start of task j (binary search)."""
        start = indexed_tasks[j][1]["start"]
        lo, hi = 0, j - 1
        result = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if indexed_tasks[mid][1]["end"] <= start:
                result = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return result

    # dp[i] = (max_value, list of selected original indices)
    # dp[i] represents the optimal solution considering first i tasks (after sorting)
    dp = [(0, []) for _ in range(m + 1)]

    for j in range(1, m + 1):
        orig_idx, task = indexed_tasks[j - 1]
        p = find_latest_compatible(j - 1)

        # Option 1: don't include this task
        opt1_value, opt1_selected = dp[j - 1]

        # Option 2: include this task
        if p == -1:
            opt2_value = task["value"]
            opt2_selected = [orig_idx]
        else:
            opt2_value = dp[p + 1][0] + task["value"]
            opt2_selected = dp[p + 1][1] + [orig_idx]

        if opt2_value > opt1_value:
            dp[j] = (opt2_value, opt2_selected)
        else:
            dp[j] = (opt1_value, opt1_selected)

    max_value, selected = dp[m]
    return (max_value, sorted(selected))
