def typed_bin_packing(
    items: list[tuple[int, str]],  # (size, type)
    bin_capacity: int,
    incompatible: set[tuple[str, str]]  # types that can't share a bin
) -> list[list[int]]:
    """
    Pack items into minimum number of bins respecting type constraints.

    Args:
        items: List of (size, type) for each item
        bin_capacity: Maximum total size per bin
        incompatible: Set of (type1, type2) pairs that can't coexist in same bin

    Returns:
        List of bins, each bin is list of item indices
    """
    if not items:
        return []

    # Build symmetric incompatibility lookup for O(1) checks
    incompatible_set = set()
    for t1, t2 in incompatible:
        incompatible_set.add((t1, t2))
        incompatible_set.add((t2, t1))

    def is_compatible(item_type: str, bin_types: set[str]) -> bool:
        """Check if item_type can coexist with all types in bin."""
        for bt in bin_types:
            if (item_type, bt) in incompatible_set:
                return False
        return True

    # First Fit Decreasing: sort items by size descending
    # Keep track of original indices
    indexed_items = [(i, items[i][0], items[i][1]) for i in range(len(items))]
    indexed_items.sort(key=lambda x: x[1], reverse=True)

    # Each bin tracks: list of item indices, current size, set of types
    bins: list[tuple[list[int], int, set[str]]] = []

    for idx, size, item_type in indexed_items:
        placed = False

        # Try to fit in existing bins
        for i, (bin_items, bin_size, bin_types) in enumerate(bins):
            # Check capacity constraint
            if bin_size + size > bin_capacity:
                continue
            # Check type compatibility
            if not is_compatible(item_type, bin_types):
                continue
            # Place item in this bin
            bin_items.append(idx)
            new_types = bin_types | {item_type}
            bins[i] = (bin_items, bin_size + size, new_types)
            placed = True
            break

        if not placed:
            # Create new bin
            bins.append(([idx], size, {item_type}))

    # Return only the lists of item indices
    return [bin_items for bin_items, _, _ in bins]
