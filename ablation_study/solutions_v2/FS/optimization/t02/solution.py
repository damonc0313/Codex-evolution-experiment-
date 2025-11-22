def schedule_with_setup(
    jobs: list[int],  # Processing times
    setup_cost: dict[tuple[int, int], int]  # {(job_i, job_j): setup_time}
) -> tuple[int, list[int]]:
    """
    Schedule jobs to minimize total time including setup costs between jobs.

    Args:
        jobs: List of job processing times (index is job ID)
        setup_cost: Setup time needed when switching from job i to job j

    Returns:
        Tuple of (total_time, job_order)
        total_time = sum of (processing_times + setup_costs)
    """
    n = len(jobs)

    # Handle edge cases
    if n == 0:
        return (0, [])

    if n == 1:
        return (jobs[0], [0])

    # Total processing time is fixed (all jobs must be completed)
    total_processing = sum(jobs)

    # Use DP with bitmask (TSP-like approach)
    # dp[mask][last] = minimum setup cost to visit jobs in mask, ending at job 'last'
    INF = float('inf')

    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[(-1, -1)] * n for _ in range(1 << n)]  # (prev_mask, prev_last)

    # Initialize: start with each job (no setup cost for first job)
    for i in range(n):
        dp[1 << i][i] = 0

    # Fill DP table
    for mask in range(1, 1 << n):
        for last in range(n):
            # Skip if job 'last' is not in the mask
            if not (mask & (1 << last)):
                continue
            if dp[mask][last] == INF:
                continue

            # Try adding each unvisited job
            for next_job in range(n):
                if mask & (1 << next_job):
                    continue  # Already visited

                new_mask = mask | (1 << next_job)
                setup = setup_cost.get((last, next_job), 0)
                new_cost = dp[mask][last] + setup

                if new_cost < dp[new_mask][next_job]:
                    dp[new_mask][next_job] = new_cost
                    parent[new_mask][next_job] = (mask, last)

    # Find the best ending (minimum setup cost with all jobs visited)
    full_mask = (1 << n) - 1
    min_setup = INF
    best_last = -1

    for last in range(n):
        if dp[full_mask][last] < min_setup:
            min_setup = dp[full_mask][last]
            best_last = last

    # Reconstruct the path
    order = []
    mask = full_mask
    last = best_last

    while mask > 0:
        order.append(last)
        prev_mask, prev_last = parent[mask][last]
        mask = prev_mask
        last = prev_last

    order.reverse()

    total_time = total_processing + min_setup

    return (total_time, order)
