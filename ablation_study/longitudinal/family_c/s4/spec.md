# Session 4: AST Builder

## Task
Implement a complete AST builder that combines tokenization, parsing with precedence, and constant folding optimization into a single pipeline.

## Function Signature
```python
def build_ast(code: str) -> dict:
    """
    Build an optimized AST from source code.

    Args:
        code: Arithmetic expression string

    Returns:
        Optimized AST with constant expressions folded
    """
```

## Pipeline Stages
1. **Tokenize**: Convert string to token list
2. **Parse**: Build AST with correct operator precedence
3. **Optimize**: Fold constant expressions

## Constant Folding
When both operands of a BINOP are NUMBER nodes, evaluate the operation and replace with a single NUMBER node.

Example: `{"type": "BINOP", "op": "+", "left": {"type": "NUMBER", "value": 3.0}, "right": {"type": "NUMBER", "value": 4.0}}`
Becomes: `{"type": "NUMBER", "value": 7.0}`

## AST Node Types
Same as previous sessions:
- `NUMBER`: `{"type": "NUMBER", "value": <float>}`
- `IDENTIFIER`: `{"type": "IDENTIFIER", "name": <str>}`
- `BINOP`: `{"type": "BINOP", "op": <str>, "left": <node>, "right": <node>}`

## Requirements
- Use tokenization from S1 concepts
- Use precedence parsing from S3 concepts
- Recursively fold all constant subexpressions
- Preserve expressions involving identifiers
- Handle all operators: +, -, *, /, ^

## Examples
```python
build_ast("3 + 4") == {"type": "NUMBER", "value": 7.0}

build_ast("2 * 3 + 4") == {"type": "NUMBER", "value": 10.0}

build_ast("x + 3 + 4")
== {"type": "BINOP", "op": "+",
    "left": {"type": "BINOP", "op": "+",
             "left": {"type": "IDENTIFIER", "name": "x"},
             "right": {"type": "NUMBER", "value": 3.0}},
    "right": {"type": "NUMBER", "value": 4.0}}
# Note: Can't fold because x is unknown

build_ast("x + (3 + 4)")
== {"type": "BINOP", "op": "+",
    "left": {"type": "IDENTIFIER", "name": "x"},
    "right": {"type": "NUMBER", "value": 7.0}}
# The (3 + 4) is folded to 7
```

## Learning Goal
Understand compiler optimization passes and how AST transformations work.
