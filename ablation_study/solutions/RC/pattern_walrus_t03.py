def batch_process(items: list, batch_size: int = 3) -> list[list]:
    """
    Process items in batches, returning list of batches.

    Learning from t01/t02: Walrus excels at "get value, immediately use it" patterns.
    """
    batches = []
    while items:
        # Extract batch using slice, test emptiness via walrus
        if (batch := items[:batch_size]):
            batches.append(batch)
            # Mutate original list by removing processed items
            del items[:batch_size]
    return batches
