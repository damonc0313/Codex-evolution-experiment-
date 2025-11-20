# Task: Process Valid Lines

Implement a function that reads lines from a list and returns only those lines that are longer than 5 characters, converted to uppercase.

**Function signature:**
```python
def process_valid_lines(lines: list[str]) -> list[str]:
    """
    Process lines, returning only those longer than 5 characters in uppercase.

    Args:
        lines: List of strings to process

    Returns:
        List of uppercase strings that meet the length requirement
    """
    pass
```

**Requirements:**
- Use the walrus operator (`:=`) to combine the length check and transformation
- Preserve order of valid lines
- Handle empty strings and very long strings
- Return empty list for empty input
