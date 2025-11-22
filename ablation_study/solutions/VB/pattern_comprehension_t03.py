def transpose(matrix: list[list]) -> list[list]:
    """
    Transpose a 2D matrix.

    """
    if not matrix:
        return []

    # zip(*matrix) unpacks rows and zips columns together
    return [list(col) for col in zip(*matrix)]
