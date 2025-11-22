# Session 2: Recursive Descent Parser

## Task
Implement a recursive descent parser that converts tokens into an Abstract Syntax Tree (AST). This version does NOT respect operator precedence - it evaluates left-to-right.

## Function Signature
```python
def parse(tokens: list[dict]) -> dict:
    """
    Parse tokens into an AST dictionary.

    Args:
        tokens: List of token dicts from tokenizer

    Returns:
        AST dict with 'type' and appropriate child keys
    """
```

## AST Node Types
- `NUMBER`: `{"type": "NUMBER", "value": <float>}`
- `IDENTIFIER`: `{"type": "IDENTIFIER", "name": <str>}`
- `BINOP`: `{"type": "BINOP", "op": <str>, "left": <node>, "right": <node>}`

## Requirements
- Parse tokens from left to right without precedence
- Support parentheses for explicit grouping
- All operators are left-associative
- Handle single values (just a number or identifier)
- Raise `SyntaxError` for malformed expressions

## Examples
```python
# 3 + 4
parse([{"type": "NUMBER", "value": "3"},
       {"type": "OPERATOR", "value": "+"},
       {"type": "NUMBER", "value": "4"}])
== {"type": "BINOP", "op": "+", "left": {"type": "NUMBER", "value": 3.0},
    "right": {"type": "NUMBER", "value": 4.0}}

# 1 + 2 + 3 (left associative: (1 + 2) + 3)
parse([...]) == {"type": "BINOP", "op": "+",
                 "left": {"type": "BINOP", "op": "+",
                          "left": {"type": "NUMBER", "value": 1.0},
                          "right": {"type": "NUMBER", "value": 2.0}},
                 "right": {"type": "NUMBER", "value": 3.0}}
```

## Learning Goal
Understand recursive descent parsing for building tree structures from linear token sequences.
