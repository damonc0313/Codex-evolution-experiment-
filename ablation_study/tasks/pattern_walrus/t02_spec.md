# Task: Parse Config with Defaults

Implement a function that parses a configuration dictionary, extracting and validating numeric values with defaults.

**Function signature:**
```python
def parse_config(config: dict, key: str, default: int = 0, min_val: int = 0) -> int:
    """
    Parse a config value, applying default and minimum validation.

    Args:
        config: Configuration dictionary
        key: Key to look up
        default: Default value if key missing or invalid
        min_val: Minimum acceptable value

    Returns:
        Validated integer value
    """
    pass
```

**Requirements:**
- Use walrus operator to retrieve and validate in a single expression
- If key exists and value is an integer >= min_val, return it
- If key missing or value invalid, return default
- Handle non-integer values gracefully
