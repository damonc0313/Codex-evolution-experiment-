def parse_config(config: dict, key: str, default: int = 0, min_val: int = 0) -> int:
    """
    Parse a config value, applying default and minimum validation.

    FS Strategy: Walrus operator for single-expression retrieve+validate.
    Pattern recognition: Common in config parsing - will inform similar tasks.
    """
    if (val := config.get(key)) is not None and isinstance(val, int) and val >= min_val:
        return val
    return default
