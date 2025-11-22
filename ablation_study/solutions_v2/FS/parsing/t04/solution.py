def pattern_match(text: str, pattern: str) -> bool:
    """
    Match text against simplified regex pattern.

    Args:
        text: String to match
        pattern: Pattern supporting:
            - Literals: 'a', 'b', etc.
            - '.' matches any single character
            - '*' matches zero or more of previous character
            - '?' matches zero or one of previous character
            - '[abc]' matches any of a, b, or c
            - '[a-z]' matches any lowercase letter

    Returns:
        True if entire text matches pattern
    """
    # Parse pattern into elements
    # Each element is (type, value, quantifier)
    # type: 'literal', 'dot', 'class'
    # value: the char or class content
    # quantifier: None, '*', '?'

    elements = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '.':
            elem = ('dot', None)
            i += 1
        elif pattern[i] == '[':
            # Find matching ]
            j = i + 1
            while j < len(pattern) and pattern[j] != ']':
                j += 1
            class_content = pattern[i+1:j]
            elem = ('class', class_content)
            i = j + 1
        else:
            elem = ('literal', pattern[i])
            i += 1

        # Check for quantifier
        if i < len(pattern) and pattern[i] in '*?':
            quantifier = pattern[i]
            i += 1
        else:
            quantifier = None

        elements.append((elem[0], elem[1], quantifier))

    def char_in_class(c, class_content):
        """Check if character c is in the character class."""
        i = 0
        while i < len(class_content):
            if i + 2 < len(class_content) and class_content[i+1] == '-':
                # Range like a-z
                if class_content[i] <= c <= class_content[i+2]:
                    return True
                i += 3
            else:
                if c == class_content[i]:
                    return True
                i += 1
        return False

    def char_matches(c, elem_type, elem_value):
        """Check if character c matches the element."""
        if elem_type == 'dot':
            return True
        elif elem_type == 'literal':
            return c == elem_value
        elif elem_type == 'class':
            return char_in_class(c, elem_value)
        return False

    # Recursive matching with memoization
    cache = {}

    def match(ti, ei):
        """
        Match text starting at index ti with elements starting at index ei.
        Returns True if the rest of text matches the rest of elements.
        """
        if (ti, ei) in cache:
            return cache[(ti, ei)]

        # Base case: end of elements
        if ei == len(elements):
            result = ti == len(text)
            cache[(ti, ei)] = result
            return result

        elem_type, elem_value, quantifier = elements[ei]

        if quantifier is None:
            # Must match exactly one character
            if ti < len(text) and char_matches(text[ti], elem_type, elem_value):
                result = match(ti + 1, ei + 1)
            else:
                result = False
        elif quantifier == '?':
            # Zero or one
            # Try zero first
            result = match(ti, ei + 1)
            if not result and ti < len(text) and char_matches(text[ti], elem_type, elem_value):
                # Try one
                result = match(ti + 1, ei + 1)
        elif quantifier == '*':
            # Zero or more
            # Try zero first
            result = match(ti, ei + 1)
            if not result:
                # Try consuming characters one at a time
                j = ti
                while j < len(text) and char_matches(text[j], elem_type, elem_value):
                    j += 1
                    if match(j, ei + 1):
                        result = True
                        break
        else:
            result = False

        cache[(ti, ei)] = result
        return result

    return match(0, 0)
