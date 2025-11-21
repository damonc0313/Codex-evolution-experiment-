# Task: Job Scheduling with Setup Costs

Schedule jobs on a single machine to minimize total completion time plus setup costs.

**Function signature:**
```python
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
    pass
```

**Requirements:**
- All jobs must be completed exactly once
- Setup cost applies when switching between jobs
- No setup cost for first job
- This is a Traveling Salesman variant (NP-hard, use heuristic or exact for small inputs)
- Return job order as list of indices
- Handle single job and empty job list

**Example:**
```python
jobs = [10, 20, 15]
setup = {
    (0, 1): 5, (0, 2): 3,
    (1, 0): 5, (1, 2): 2,
    (2, 0): 3, (2, 1): 2
}
# Order [0, 2, 1]: time = 10 + 3 + 15 + 2 + 20 = 50
schedule_with_setup(jobs, setup) == (50, [0, 2, 1])
```

**Difficulty:** NP-hard optimization (use DP or heuristic)
