# Task: Expression Parser with Variables

Parse and evaluate arithmetic expressions with variables and precedence.

**Function signature:**
```python
def parse_and_eval(
    expression: str,
    variables: dict[str, float] = None
) -> float:
    """
    Parse and evaluate arithmetic expression with variables.

    Args:
        expression: String like "2 * x + y / (z - 1)"
        variables: Dict of variable values, defaults to empty

    Returns:
        Evaluated result as float

    Raises:
        ValueError: if expression invalid or variable undefined
    """
    pass
```

**Requirements:**
- Support: +, -, *, /, parentheses
- Correct operator precedence (* / before + -)
- Support variables (single letters or words)
- Support negative numbers
- Handle whitespace flexibly
- Raise ValueError for undefined variables or invalid syntax
- Use recursive descent parser or similar

**Example:**
```python
parse_and_eval("2 + 3 * 4") == 14.0
parse_and_eval("(2 + 3) * 4") == 20.0
parse_and_eval("x * 2 + y", {"x": 5, "y": 3}) == 13.0
parse_and_eval("-5 + 10") == 5.0
parse_and_eval("undefined", {}) # Raises ValueError
```

**Difficulty:** Parsing with precedence and error handling
