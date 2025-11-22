def tokenize(code: str) -> list[dict]:
    """
    Tokenize arithmetic expressions into token dictionaries.

    Args:
        code: Arithmetic expression string (e.g., "3 + 4 * 2")

    Returns:
        List of token dicts with 'type' and 'value' keys
    """
    tokens = []
    i = 0

    while i < len(code):
        char = code[i]

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Numbers (integers and floats)
        if char.isdigit() or (char == '.' and i + 1 < len(code) and code[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < len(code) and (code[i].isdigit() or (code[i] == '.' and not has_dot)):
                if code[i] == '.':
                    has_dot = True
                i += 1
            tokens.append({"type": "NUMBER", "value": code[start:i]})
            continue

        # Identifiers (variable names)
        if char.isalpha():
            start = i
            while i < len(code) and code[i].isalpha():
                i += 1
            tokens.append({"type": "IDENTIFIER", "value": code[start:i]})
            continue

        # Operators
        if char in "+-*/^":
            tokens.append({"type": "OPERATOR", "value": char})
            i += 1
            continue

        # Parentheses
        if char == '(':
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue

        if char == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue

        # Invalid character
        raise ValueError(f"Invalid character: {char}")

    return tokens
