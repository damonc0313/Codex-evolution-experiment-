def invert_dict(d: dict) -> dict:
    """
    Invert dictionary, swapping keys and values.

    FS Strategy: Dict comprehension with simple swap.
    Learning: Comprehensions are the dual of loops - declarative vs imperative.
    """
    return {value: key for key, value in d.items()}
