def invert_dict(d: dict) -> dict:
    """
    Invert dictionary, swapping keys and values.

    """
    return {value: key for key, value in d.items()}
