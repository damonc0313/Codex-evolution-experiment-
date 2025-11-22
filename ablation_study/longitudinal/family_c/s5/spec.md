# Session 5: Interpreter

## Task
Implement a complete expression interpreter that evaluates arithmetic expressions with variable support. This is the culmination of the parsing evolution family, combining all previous components.

## Function Signature
```python
def evaluate(code: str, variables: dict) -> float:
    """
    Evaluate an arithmetic expression with variables.

    Args:
        code: Arithmetic expression string
        variables: Dictionary mapping variable names to float values

    Returns:
        The computed result as a float
    """
```

## Pipeline
1. **Tokenize**: Convert string to tokens
2. **Parse**: Build AST with precedence
3. **Optimize**: Constant fold where possible
4. **Evaluate**: Walk AST and compute result

## Requirements
- Full pipeline from previous sessions
- Variable substitution from provided dictionary
- Raise `NameError` for undefined variables
- Support all operators: +, -, *, /, ^
- Return float result

## Examples
```python
evaluate("3 + 4", {}) == 7.0

evaluate("x + y", {"x": 3, "y": 4}) == 7.0

evaluate("2 * x + 3", {"x": 5}) == 13.0

evaluate("x ^ 2 + y ^ 2", {"x": 3, "y": 4}) == 25.0

evaluate("(a + b) * c", {"a": 1, "b": 2, "c": 3}) == 9.0
```

## Error Handling
```python
evaluate("x + 1", {})  # raises NameError: undefined variable 'x'
```

## Learning Goal
Understand the complete interpreter pipeline from source code to computed value.
