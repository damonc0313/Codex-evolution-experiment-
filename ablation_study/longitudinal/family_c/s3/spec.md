# Session 3: Precedence Parser

## Task
Implement a parser that respects operator precedence. Multiplication and division bind tighter than addition and subtraction. Exponentiation binds tightest.

## Function Signature
```python
def parse_with_precedence(tokens: list[dict]) -> dict:
    """
    Parse tokens into an AST respecting operator precedence.

    Args:
        tokens: List of token dicts from tokenizer

    Returns:
        AST dict with correct precedence structure
    """
```

## Operator Precedence (lowest to highest)
1. `+`, `-` (additive)
2. `*`, `/` (multiplicative)
3. `^` (exponentiation, right-associative)

## AST Node Types
Same as Session 2:
- `NUMBER`: `{"type": "NUMBER", "value": <float>}`
- `IDENTIFIER`: `{"type": "IDENTIFIER", "name": <str>}`
- `BINOP`: `{"type": "BINOP", "op": <str>, "left": <node>, "right": <node>}`

## Requirements
- Multiplication and division before addition and subtraction
- Exponentiation has highest precedence
- `+`, `-`, `*`, `/` are left-associative
- `^` is right-associative (2^3^4 = 2^(3^4))
- Parentheses override precedence

## Examples
```python
# 2 + 3 * 4 = 2 + (3 * 4), not (2 + 3) * 4
parse_with_precedence([...])
== {"type": "BINOP", "op": "+",
    "left": {"type": "NUMBER", "value": 2.0},
    "right": {"type": "BINOP", "op": "*",
              "left": {"type": "NUMBER", "value": 3.0},
              "right": {"type": "NUMBER", "value": 4.0}}}

# 2 ^ 3 ^ 2 = 2 ^ (3 ^ 2) (right associative)
parse_with_precedence([...])
== {"type": "BINOP", "op": "^",
    "left": {"type": "NUMBER", "value": 2.0},
    "right": {"type": "BINOP", "op": "^",
              "left": {"type": "NUMBER", "value": 3.0},
              "right": {"type": "NUMBER", "value": 2.0}}}
```

## Learning Goal
Understand precedence climbing and how mathematical conventions are encoded in parsers.
