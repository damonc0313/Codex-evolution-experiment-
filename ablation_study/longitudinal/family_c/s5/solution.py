def evaluate(code: str, variables: dict) -> float:
    """
    Evaluate an arithmetic expression with variables.

    Args:
        code: Arithmetic expression string
        variables: Dictionary mapping variable names to float values

    Returns:
        The computed result as a float
    """
    tokens = tokenize(code)
    ast = parse_with_precedence(tokens)
    optimized = constant_fold(ast)
    return eval_ast(optimized, variables)


def tokenize(code: str) -> list[dict]:
    """Tokenize arithmetic expressions into token dictionaries."""
    tokens = []
    i = 0

    while i < len(code):
        char = code[i]

        if char.isspace():
            i += 1
            continue

        if char.isdigit() or (char == '.' and i + 1 < len(code) and code[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < len(code) and (code[i].isdigit() or (code[i] == '.' and not has_dot)):
                if code[i] == '.':
                    has_dot = True
                i += 1
            tokens.append({"type": "NUMBER", "value": code[start:i]})
            continue

        if char.isalpha():
            start = i
            while i < len(code) and code[i].isalpha():
                i += 1
            tokens.append({"type": "IDENTIFIER", "value": code[start:i]})
            continue

        if char in "+-*/^":
            tokens.append({"type": "OPERATOR", "value": char})
            i += 1
            continue

        if char == '(':
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue

        if char == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue

        raise ValueError(f"Invalid character: {char}")

    return tokens


class PrecedenceParser:
    PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
    RIGHT_ASSOC = {"^"}

    def __init__(self, tokens: list[dict]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> dict | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> dict:
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of expression")
        self.pos += 1
        return token

    def parse_expression(self, min_prec: int = 0) -> dict:
        left = self.parse_primary()

        while True:
            token = self.current()
            if token is None or token["type"] != "OPERATOR":
                break

            op = token["value"]
            prec = self.PRECEDENCE.get(op, 0)

            if prec < min_prec:
                break

            self.consume()
            next_min_prec = prec if op in self.RIGHT_ASSOC else prec + 1
            right = self.parse_expression(next_min_prec)

            left = {"type": "BINOP", "op": op, "left": left, "right": right}

        return left

    def parse_primary(self) -> dict:
        token = self.current()

        if token is None:
            raise SyntaxError("Unexpected end of expression")

        if token["type"] == "NUMBER":
            self.consume()
            return {"type": "NUMBER", "value": float(token["value"])}

        if token["type"] == "IDENTIFIER":
            self.consume()
            return {"type": "IDENTIFIER", "name": token["value"]}

        if token["type"] == "LPAREN":
            self.consume()
            expr = self.parse_expression(0)
            if self.current() is None or self.current()["type"] != "RPAREN":
                raise SyntaxError("Expected closing parenthesis")
            self.consume()
            return expr

        raise SyntaxError(f"Unexpected token: {token}")


def parse_with_precedence(tokens: list[dict]) -> dict:
    """Parse tokens with operator precedence."""
    parser = PrecedenceParser(tokens)
    return parser.parse_expression()


def constant_fold(node: dict) -> dict:
    """Recursively fold constant expressions in the AST."""
    if node["type"] == "NUMBER":
        return node

    if node["type"] == "IDENTIFIER":
        return node

    if node["type"] == "BINOP":
        left = constant_fold(node["left"])
        right = constant_fold(node["right"])

        if left["type"] == "NUMBER" and right["type"] == "NUMBER":
            result = compute_op(node["op"], left["value"], right["value"])
            return {"type": "NUMBER", "value": result}

        return {"type": "BINOP", "op": node["op"], "left": left, "right": right}

    return node


def compute_op(op: str, left: float, right: float) -> float:
    """Compute a binary operation."""
    if op == "+":
        return left + right
    elif op == "-":
        return left - right
    elif op == "*":
        return left * right
    elif op == "/":
        return left / right
    elif op == "^":
        return left ** right
    else:
        raise ValueError(f"Unknown operator: {op}")


def eval_ast(node: dict, variables: dict) -> float:
    """
    Evaluate an AST node with variable bindings.

    Args:
        node: AST node to evaluate
        variables: Variable name to value mapping

    Returns:
        Computed float value
    """
    if node["type"] == "NUMBER":
        return node["value"]

    if node["type"] == "IDENTIFIER":
        name = node["name"]
        if name not in variables:
            raise NameError(f"undefined variable '{name}'")
        return float(variables[name])

    if node["type"] == "BINOP":
        left = eval_ast(node["left"], variables)
        right = eval_ast(node["right"], variables)
        return compute_op(node["op"], left, right)

    raise ValueError(f"Unknown node type: {node['type']}")
