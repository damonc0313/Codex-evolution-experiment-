def parse_with_precedence(tokens: list[dict]) -> dict:
    """
    Parse tokens into an AST respecting operator precedence.

    Args:
        tokens: List of token dicts from tokenizer

    Returns:
        AST dict with correct precedence structure
    """
    parser = PrecedenceParser(tokens)
    return parser.parse_expression()


class PrecedenceParser:
    # Precedence levels (lower number = lower precedence)
    PRECEDENCE = {
        "+": 1, "-": 1,   # Additive
        "*": 2, "/": 2,   # Multiplicative
        "^": 3            # Exponentiation
    }

    # Right-associative operators
    RIGHT_ASSOC = {"^"}

    def __init__(self, tokens: list[dict]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> dict | None:
        """Get current token or None if exhausted."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> dict:
        """Consume and return current token."""
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of expression")
        self.pos += 1
        return token

    def parse_expression(self, min_prec: int = 0) -> dict:
        """
        Parse expression using precedence climbing.

        Args:
            min_prec: Minimum precedence level to parse
        """
        left = self.parse_primary()

        while True:
            token = self.current()
            if token is None or token["type"] != "OPERATOR":
                break

            op = token["value"]
            prec = self.PRECEDENCE.get(op, 0)

            if prec < min_prec:
                break

            self.consume()  # consume operator

            # For right-associative, use same precedence; for left, use prec + 1
            next_min_prec = prec if op in self.RIGHT_ASSOC else prec + 1
            right = self.parse_expression(next_min_prec)

            left = {
                "type": "BINOP",
                "op": op,
                "left": left,
                "right": right
            }

        return left

    def parse_primary(self) -> dict:
        """Parse a primary expression (number, identifier, or parenthesized)."""
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
            self.consume()  # consume '('
            expr = self.parse_expression(0)
            if self.current() is None or self.current()["type"] != "RPAREN":
                raise SyntaxError("Expected closing parenthesis")
            self.consume()  # consume ')'
            return expr

        raise SyntaxError(f"Unexpected token: {token}")
