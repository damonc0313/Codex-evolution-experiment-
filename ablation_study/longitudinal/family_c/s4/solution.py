def build_ast(code: str) -> dict:
    """
    Build an optimized AST from source code.

    Args:
        code: Arithmetic expression string

    Returns:
        Optimized AST with constant expressions folded
    """
    tokens = tokenize(code)
    ast = parse_with_precedence(tokens)
    optimized = constant_fold(ast)
    return optimized


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
    """
    Recursively fold constant expressions in the AST.

    Args:
        node: AST node to optimize

    Returns:
        Optimized AST node
    """
    if node["type"] == "NUMBER":
        return node

    if node["type"] == "IDENTIFIER":
        return node

    if node["type"] == "BINOP":
        # Recursively fold children first
        left = constant_fold(node["left"])
        right = constant_fold(node["right"])

        # If both are numbers, we can fold
        if left["type"] == "NUMBER" and right["type"] == "NUMBER":
            result = evaluate_op(node["op"], left["value"], right["value"])
            return {"type": "NUMBER", "value": result}

        # Otherwise return with folded children
        return {"type": "BINOP", "op": node["op"], "left": left, "right": right}

    return node


def evaluate_op(op: str, left: float, right: float) -> float:
    """Evaluate a binary operation."""
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
