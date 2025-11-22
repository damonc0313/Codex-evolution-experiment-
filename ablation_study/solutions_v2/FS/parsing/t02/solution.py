"""JSON Path Query Implementation."""

import re
from typing import Any, List


def json_query(data: Any, path: str) -> List[Any]:
    """
    Query JSON-like data structure using path expression.

    Args:
        data: Nested dict/list structure
        path: Query path like "users[*].name" or "store.books[0].title"

    Returns:
        List of values matching the path

    Path syntax:
    - "." for nested objects
    - "[index]" for array access
    - "[*]" for all array elements
    - Returns empty list if path doesn't match
    """
    if not path:
        return [data]

    # Parse the path into tokens
    tokens = _parse_path(path)

    if not tokens:
        return [data]

    # Start with the root data as the initial set of values
    current_values = [data]

    for token in tokens:
        next_values = []
        for value in current_values:
            next_values.extend(_apply_token(value, token))
        current_values = next_values

        # Early exit if no matches
        if not current_values:
            return []

    return current_values


def _parse_path(path: str) -> List[dict]:
    """
    Parse path string into list of tokens.

    Each token is a dict with:
    - type: 'key', 'index', or 'wildcard'
    - value: the key name or index number
    """
    tokens = []

    # Pattern to match path segments:
    # - Key names (letters, numbers, underscores)
    # - Array indices [n] or [*]
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*|\[-?\d+\]|\[\*\])'

    # Remove leading dots and split properly
    # Handle paths like "a.b.c" or "a[0].b" or "a[*].b[0]"

    i = 0
    while i < len(path):
        # Skip dots
        if path[i] == '.':
            i += 1
            continue

        # Check for array access
        if path[i] == '[':
            end = path.find(']', i)
            if end == -1:
                break
            bracket_content = path[i+1:end]
            if bracket_content == '*':
                tokens.append({'type': 'wildcard'})
            else:
                try:
                    index = int(bracket_content)
                    tokens.append({'type': 'index', 'value': index})
                except ValueError:
                    break
            i = end + 1
        else:
            # Find the end of the key name
            match = re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', path[i:])
            if match:
                key = match.group()
                tokens.append({'type': 'key', 'value': key})
                i += len(key)
            else:
                # Handle numeric keys or other characters
                end = i
                while end < len(path) and path[end] not in '.[]':
                    end += 1
                if end > i:
                    key = path[i:end]
                    tokens.append({'type': 'key', 'value': key})
                    i = end
                else:
                    i += 1

    return tokens


def _apply_token(value: Any, token: dict) -> List[Any]:
    """
    Apply a single token to a value and return matching results.
    """
    token_type = token['type']

    if token_type == 'key':
        key = token['value']
        if isinstance(value, dict) and key in value:
            return [value[key]]
        return []

    elif token_type == 'index':
        index = token['value']
        if isinstance(value, list):
            # Handle negative indices
            if -len(value) <= index < len(value):
                return [value[index]]
        return []

    elif token_type == 'wildcard':
        if isinstance(value, list):
            return list(value)
        return []

    return []
