"""Expression Parser with Variables using Recursive Descent."""

import re
from typing import Optional


def parse_and_eval(
    expression: str,
    variables: dict[str, float] = None
) -> float:
    """
    Parse and evaluate arithmetic expression with variables.

    Args:
        expression: String like "2 * x + y / (z - 1)"
        variables: Dict of variable values, defaults to empty

    Returns:
        Evaluated result as float

    Raises:
        ValueError: if expression invalid or variable undefined
    """
    if variables is None:
        variables = {}

    parser = ExpressionParser(expression, variables)
    return parser.parse()


class ExpressionParser:
    """Recursive descent parser for arithmetic expressions."""

    def __init__(self, expression: str, variables: dict[str, float]):
        self.expression = expression
        self.variables = variables
        self.pos = 0
        self.tokens = self._tokenize()
        self.current_token_index = 0

    def _tokenize(self) -> list:
        """Convert expression into tokens."""
        tokens = []
        pattern = r'(\d+\.?\d*|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/()])'

        # Remove whitespace and tokenize
        expr = self.expression
        pos = 0

        while pos < len(expr):
            # Skip whitespace
            while pos < len(expr) and expr[pos] in ' \t\n\r':
                pos += 1

            if pos >= len(expr):
                break

            # Try to match a token
            match = re.match(pattern, expr[pos:])
            if match:
                token = match.group(0)
                tokens.append(token)
                pos += len(token)
            else:
                raise ValueError(f"Invalid character at position {pos}: '{expr[pos]}'")

        return tokens

    def _current_token(self) -> Optional[str]:
        """Get current token without consuming it."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def _consume(self) -> str:
        """Consume and return current token."""
        token = self._current_token()
        if token is None:
            raise ValueError("Unexpected end of expression")
        self.current_token_index += 1
        return token

    def _peek(self) -> Optional[str]:
        """Peek at current token."""
        return self._current_token()

    def parse(self) -> float:
        """Parse the expression and return the result."""
        if not self.tokens:
            raise ValueError("Empty expression")

        result = self._parse_expression()

        # Ensure all tokens were consumed
        if self._current_token() is not None:
            raise ValueError(f"Unexpected token: {self._current_token()}")

        return float(result)

    def _parse_expression(self) -> float:
        """Parse addition and subtraction (lowest precedence)."""
        left = self._parse_term()

        while self._peek() in ('+', '-'):
            op = self._consume()
            right = self._parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right

        return left

    def _parse_term(self) -> float:
        """Parse multiplication and division (higher precedence)."""
        left = self._parse_factor()

        while self._peek() in ('*', '/'):
            op = self._consume()
            right = self._parse_factor()
            if op == '*':
                left = left * right
            else:
                # Handle division by zero gracefully - return infinity
                if right == 0:
                    left = float('inf') if left >= 0 else float('-inf')
                else:
                    left = left / right

        return left

    def _parse_factor(self) -> float:
        """Parse unary minus, numbers, variables, and parentheses."""
        token = self._peek()

        if token is None:
            raise ValueError("Unexpected end of expression")

        # Handle unary minus (only allow minus as unary operator)
        if token == '-':
            self._consume()
            return -self._parse_factor()

        # Handle parentheses
        if token == '(':
            self._consume()
            result = self._parse_expression()
            if self._peek() != ')':
                raise ValueError("Missing closing parenthesis")
            self._consume()
            return result

        # Handle numbers
        if self._is_number(token):
            self._consume()
            return float(token)

        # Handle variables
        if self._is_variable(token):
            self._consume()
            if token not in self.variables:
                raise ValueError(f"Undefined variable: {token}")
            return float(self.variables[token])

        raise ValueError(f"Unexpected token: {token}")

    def _is_number(self, token: str) -> bool:
        """Check if token is a number."""
        try:
            float(token)
            return True
        except ValueError:
            return False

    def _is_variable(self, token: str) -> bool:
        """Check if token is a variable name."""
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token))
