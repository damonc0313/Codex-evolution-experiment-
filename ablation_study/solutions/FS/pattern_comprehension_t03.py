def transpose(matrix: list[list]) -> list[list]:
    """
    Transpose a 2D matrix.

    FS Strategy: Nested comprehension with zip for elegant column extraction.
    Meta-insight: This is mathematical matrix operation as Python comprehension.
    """
    if not matrix:
        return []

    # zip(*matrix) unpacks rows and zips columns together
    return [list(col) for col in zip(*matrix)]
