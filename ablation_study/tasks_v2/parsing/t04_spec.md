# Task: Regex-Like Pattern Matcher

Implement simplified regex matching with *, ?, and character classes.

**Function signature:**
```python
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
    pass
```

**Requirements:**
- Must match ENTIRE text (not substring)
- '*' and '?' apply to previous element (char or class)
- Character classes can have ranges [a-z] or lists [abc]
- '.' matches any character including space
- Handle edge cases: empty text, empty pattern
- Use backtracking or DP

**Example:**
```python
pattern_match("abc", "abc") == True
pattern_match("abc", "a.c") == True
pattern_match("abc", "a*bc") == True  # zero 'a's + "bc" doesn't match
pattern_match("aabc", "a*bc") == True # two 'a's + "bc"
pattern_match("hello", "h[aeiou]llo") == True
pattern_match("world", "w[a-z]*d") == True
pattern_match("abc", "ab") == False  # Must match entire text
```

**Difficulty:** Recursive/DP pattern matching
