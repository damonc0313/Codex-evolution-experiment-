# Session 1: Tokenizer

## Task
Implement a tokenizer for arithmetic expressions that breaks input into typed token dictionaries.

## Function Signature
```python
def tokenize(code: str) -> list[dict]:
    """
    Tokenize arithmetic expressions into token dictionaries.

    Args:
        code: Arithmetic expression string (e.g., "3 + 4 * 2")

    Returns:
        List of token dicts with 'type' and 'value' keys
    """
```

## Token Types
- `NUMBER`: Integer or decimal numbers (e.g., "42", "3.14")
- `OPERATOR`: Arithmetic operators (+, -, *, /, ^)
- `LPAREN`: Left parenthesis (
- `RPAREN`: Right parenthesis )
- `IDENTIFIER`: Variable names (alphabetic, e.g., "x", "foo")

## Requirements
- Skip whitespace between tokens
- Support integers and floating-point numbers
- Support basic arithmetic operators: +, -, *, /, ^
- Support parentheses for grouping
- Support variable identifiers (letters only)
- Raise `ValueError` for invalid characters

## Examples
```python
tokenize("3 + 4") == [
    {"type": "NUMBER", "value": "3"},
    {"type": "OPERATOR", "value": "+"},
    {"type": "NUMBER", "value": "4"}
]

tokenize("(x + 2) * 3") == [
    {"type": "LPAREN", "value": "("},
    {"type": "IDENTIFIER", "value": "x"},
    {"type": "OPERATOR", "value": "+"},
    {"type": "NUMBER", "value": "2"},
    {"type": "RPAREN", "value": ")"},
    {"type": "OPERATOR", "value": "*"},
    {"type": "NUMBER", "value": "3"}
]
```

## Learning Goal
Understand lexical analysis as the first phase of parsing, converting raw text into structured tokens.
