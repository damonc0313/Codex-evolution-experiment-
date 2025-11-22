"""S-Expression Parser and Evaluator."""


def tokenize(expr: str) -> list:
    """
    Tokenize an S-expression string into a list of tokens.

    Tokens are: '(', ')', and atoms (numbers/symbols).
    """
    tokens = []
    i = 0
    while i < len(expr):
        char = expr[i]

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Parentheses are their own tokens
        if char == '(':
            tokens.append('(')
            i += 1
        elif char == ')':
            tokens.append(')')
            i += 1
        else:
            # Collect atom (number or symbol)
            j = i
            while j < len(expr) and not expr[j].isspace() and expr[j] not in '()':
                j += 1
            tokens.append(expr[i:j])
            i = j

    return tokens


def parse_tokens(tokens: list, index: int = 0) -> tuple:
    """
    Parse tokens starting at index, return (parsed_value, next_index).
    """
    if index >= len(tokens):
        raise ValueError("Unexpected end of input")

    token = tokens[index]

    if token == '(':
        # Start of a list
        result = []
        index += 1  # Skip the '('

        while index < len(tokens) and tokens[index] != ')':
            value, index = parse_tokens(tokens, index)
            result.append(value)

        if index >= len(tokens):
            raise ValueError("Unmatched opening parenthesis")

        index += 1  # Skip the ')'
        return result, index

    elif token == ')':
        raise SyntaxError("Unexpected closing parenthesis")

    else:
        # Atom: try to parse as number, otherwise treat as symbol
        atom = parse_atom(token)
        return atom, index + 1


def parse_atom(token: str):
    """Parse an atom token into a number or symbol."""
    # Try integer first
    try:
        return int(token)
    except ValueError:
        pass

    # Try float
    try:
        return float(token)
    except ValueError:
        pass

    # It's a symbol (string)
    return token


def parse_sexpr(expr: str):
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
    tokens = tokenize(expr)

    if not tokens:
        raise ValueError("Empty expression")

    result, next_index = parse_tokens(tokens, 0)

    # Check for extra tokens after the main expression
    if next_index < len(tokens):
        raise SyntaxError("Unexpected tokens after expression")

    return result


def eval_sexpr(expr, env: dict = None):
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
    if env is None:
        env = {}

    # Numbers evaluate to themselves
    if isinstance(expr, (int, float)):
        return expr

    # Symbols look up in environment
    if isinstance(expr, str):
        if expr in env:
            return env[expr]
        else:
            raise NameError(f"Undefined symbol: {expr}")

    # Empty list
    if isinstance(expr, list) and len(expr) == 0:
        return []

    # List: evaluate as function call
    if isinstance(expr, list):
        op = expr[0]
        args = expr[1:]

        if op == '+':
            # Addition: evaluate all args and sum
            return sum(eval_sexpr(arg, env) for arg in args)

        elif op == '*':
            # Multiplication: evaluate all args and multiply
            result = 1
            for arg in args:
                result *= eval_sexpr(arg, env)
            return result

        elif op == '-':
            # Subtraction: binary only
            if len(args) != 2:
                raise ValueError("Subtraction requires exactly 2 arguments")
            return eval_sexpr(args[0], env) - eval_sexpr(args[1], env)

        elif op == 'define':
            # Define: (define var value)
            if len(args) != 2:
                raise ValueError("Define requires exactly 2 arguments")
            var_name = args[0]
            if not isinstance(var_name, str):
                raise ValueError("Variable name must be a symbol")
            value = eval_sexpr(args[1], env)
            env[var_name] = value
            return value

        else:
            raise ValueError(f"Unknown operator: {op}")

    raise ValueError(f"Cannot evaluate: {expr}")
