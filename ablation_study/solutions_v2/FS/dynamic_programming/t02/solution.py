def dependent_knapsack(
    capacity: int,
    items: list[dict]  # {"weight": int, "value": int, "requires": list[int]}
) -> tuple[int, list[int]]:
    """
    Solve knapsack where items may require other items to be included.

    Args:
        capacity: Maximum weight capacity
        items: List of items with weight, value, and list of required item indices

    Returns:
        Tuple of (max_value, list_of_selected_indices)
    """
    if not items or capacity == 0:
        return (0, [])

    n = len(items)
    best_value = 0
    best_subset = []

    # Enumerate all subsets using bitmask
    for mask in range(1 << n):
        # Check if this subset is valid (all dependencies satisfied)
        valid = True
        selected = []
        total_weight = 0
        total_value = 0

        for i in range(n):
            if mask & (1 << i):
                selected.append(i)
                total_weight += items[i]["weight"]
                total_value += items[i]["value"]
                # Check that all dependencies are also in the subset
                for req in items[i]["requires"]:
                    if not (mask & (1 << req)):
                        valid = False
                        break
            if not valid:
                break

        if valid and total_weight <= capacity and total_value > best_value:
            best_value = total_value
            best_subset = selected

    return (best_value, sorted(best_subset))
