def balanced_partition(arr: list[int], k: int) -> list[list[int]]:
    """
    Partition array into k subsets with equal sum, minimizing max subset size.

    Args:
        arr: List of positive integers
        k: Number of subsets

    Returns:
        List of k subsets (each a list of array indices)
        Returns [] if no valid equal-sum partition exists
    """
    n = len(arr)

    # Edge case: empty array
    if n == 0:
        return [[]] if k == 1 else []

    total = sum(arr)

    # Check if sum is divisible by k
    if total % k != 0:
        return []

    target = total // k

    # Check if any single element exceeds target (impossible to partition)
    if any(x > target for x in arr):
        return []

    # Try to find k subsets each summing to target
    # Use iterative deepening on max subset size to minimize it
    min_max_size = (n + k - 1) // k  # ceil(n/k)

    for max_size in range(min_max_size, n + 1):
        result = _try_partition(arr, k, target, max_size)
        if result is not None:
            return result

    return []


def _try_partition(arr: list[int], k: int, target: int, max_size: int) -> list[list[int]] | None:
    """
    Try to find a valid k-partition where all subsets sum to target
    and no subset exceeds max_size elements.
    """
    n = len(arr)
    result = [[] for _ in range(k)]
    sums = [0] * k

    # Sort indices by value descending for better pruning (larger elements first)
    indices = sorted(range(n), key=lambda i: -arr[i])

    def backtrack(idx: int) -> bool:
        if idx == n:
            # All elements assigned, check if all subsets sum to target
            return all(s == target for s in sums)

        elem_idx = indices[idx]
        elem_val = arr[elem_idx]

        # Calculate remaining sum and elements
        remaining_sum = sum(arr[indices[j]] for j in range(idx, n))

        tried_empty = False
        for i in range(k):
            # Skip if subset is full
            if len(result[i]) >= max_size:
                continue

            # Skip if adding this element exceeds target
            if sums[i] + elem_val > target:
                continue

            # Pruning: if current subset needs more sum than remaining, skip
            needed = target - sums[i] - elem_val
            if needed > remaining_sum - elem_val:
                continue

            # Don't try multiple empty buckets (symmetry breaking)
            if len(result[i]) == 0:
                if tried_empty:
                    continue
                tried_empty = True

            # Try assigning element to this subset
            result[i].append(elem_idx)
            sums[i] += elem_val

            if backtrack(idx + 1):
                return True

            result[i].pop()
            sums[i] -= elem_val

        return False

    if backtrack(0):
        return result
    return None
