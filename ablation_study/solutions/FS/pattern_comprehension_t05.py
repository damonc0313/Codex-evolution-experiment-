def group_stats(items: list[dict], group_key: str, value_key: str) -> dict[str, dict]:
    """
    Group items by a key and compute statistics on values.

    FS Strategy: Nested comprehensions for grouping + aggregation.
    Advanced pattern: Combines filtering, grouping, and reduction in comprehensions.
    """
    # First, extract valid items (those with both keys)
    valid_items = [
        item for item in items
        if group_key in item and value_key in item
    ]

    if not valid_items:
        return {}

    # Get unique group values
    groups = {item[group_key] for item in valid_items}

    # Compute stats for each group
    return {
        group: {
            "count": (group_items := [
                item[value_key]
                for item in valid_items
                if item[group_key] == group
            ]) and len(group_items),
            "sum": sum(group_items),
            "avg": sum(group_items) / len(group_items)
        }
        for group in groups
        # Use walrus to avoid recomputing group_items
        if (group_items := [
            item[value_key]
            for item in valid_items
            if item[group_key] == group
        ])
    }
