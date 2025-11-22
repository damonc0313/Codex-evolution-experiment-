def parse(tokens: list[dict]) -> dict:
    """
    Parse tokens into an AST dictionary (no operator precedence).

    Args:
        tokens: List of token dicts from tokenizer

    Returns:
        AST dict with 'type' and appropriate child keys
    """
    parser = Parser(tokens)
    return parser.parse_expression()


class Parser:
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

    def parse_expression(self) -> dict:
        """Parse an expression (left-associative, no precedence)."""
        left = self.parse_primary()

        while self.current() and self.current()["type"] == "OPERATOR":
            op_token = self.consume()
            right = self.parse_primary()
            left = {
                "type": "BINOP",
                "op": op_token["value"],
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
            expr = self.parse_expression()
            if self.current() is None or self.current()["type"] != "RPAREN":
                raise SyntaxError("Expected closing parenthesis")
            self.consume()  # consume ')'
            return expr

        raise SyntaxError(f"Unexpected token: {token}")
