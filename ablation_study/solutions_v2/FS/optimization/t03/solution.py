def balanced_knapsack(
    capacity: int,
    items: list[tuple[int, int]]  # (weight, value)
) -> tuple[int, float, list[int]]:
    """
    Select items to maximize value while minimizing weight variance.

    Args:
        capacity: Maximum total weight
        items: List of (weight, value) tuples

    Returns:
        Tuple of (total_value, weight_variance, selected_indices)
        Among solutions with max value, pick one with minimum weight variance
    """
    n = len(items)

    if n == 0:
        return (0, 0.0, [])

    best_value = 0
    best_variance = 0.0
    best_selected = []

    # Enumerate all non-empty subsets using bitmask
    for mask in range(1, 1 << n):
        selected = [i for i in range(n) if mask & (1 << i)]

        total_weight = sum(items[i][0] for i in selected)
        if total_weight > capacity:
            continue

        total_value = sum(items[i][1] for i in selected)

        # Calculate variance of selected item weights
        if len(selected) == 1:
            variance = 0.0
        else:
            weights = [items[i][0] for i in selected]
            mean_weight = sum(weights) / len(weights)
            variance = sum((w - mean_weight) ** 2 for w in weights) / len(weights)

        # Update best if this is better (primary: max value, secondary: min variance)
        if total_value > best_value or (total_value == best_value and variance < best_variance):
            best_value = total_value
            best_variance = variance
            best_selected = selected

    return (best_value, best_variance, sorted(best_selected))
