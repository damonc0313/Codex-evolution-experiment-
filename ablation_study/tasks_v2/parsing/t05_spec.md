# Task: S-Expression Parser

Parse and evaluate S-expressions (Lisp-like syntax).

**Function signature:**
```python
def parse_sexpr(expr: str) -> any:
    """
    Parse S-expression into nested Python structures.

    Args:
        expr: S-expression string

    Returns:
        Parsed structure:
        - Atoms (numbers/symbols) returned as-is
        - Lists returned as Python lists

    Grammar:
    sexpr := atom | list
    atom := number | symbol
    list := '(' sexpr* ')'
    number := integer or float
    symbol := identifier
    """
    pass

def eval_sexpr(expr: any, env: dict = None) -> any:
    """
    Evaluate parsed S-expression.

    Args:
        expr: Parsed S-expression
        env: Environment dict for variable lookups

    Returns:
        Evaluation result

    Supported:
    - (+ a b ...) - addition
    - (* a b ...) - multiplication
    - (- a b) - subtraction
    - (define var value) - variable definition
    - Symbols look up values in env
    """
    pass
```

**Requirements:**
- parse_sexpr() converts string to nested lists
- eval_sexpr() evaluates with basic arithmetic
- Support nested expressions: `(+ (* 2 3) 4)` → 10
- Support define for variables
- Raise errors for undefined symbols or invalid syntax

**Example:**
```python
parsed = parse_sexpr("(+ 1 2 3)")
eval_sexpr(parsed) == 6

parsed = parse_sexpr("(+ (* 2 3) (- 10 5))")
eval_sexpr(parsed) == 11

env = {}
parsed = parse_sexpr("(define x 5)")
eval_sexpr(parsed, env)  # env now has {"x": 5}
parsed = parse_sexpr("(* x 2)")
eval_sexpr(parsed, env) == 10
```

**Difficulty:** Recursive parsing and evaluation
