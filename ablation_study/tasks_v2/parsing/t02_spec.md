# Task: JSON Path Query

Implement a simple JSONPath-like query language for extracting data.

**Function signature:**
```python
def json_query(data: any, path: str) -> list[any]:
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
    pass
```

**Requirements:**
- Support nested object access: "a.b.c"
- Support array indexing: "arr[0]"
- Support wildcard: "arr[*]"
- Support combination: "users[*].emails[0]"
- Return list of all matching values
- Handle missing keys gracefully (return [])
- No need for advanced features (filters, functions, etc.)

**Example:**
```python
data = {
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
}
json_query(data, "users[0].name") == ["Alice"]
json_query(data, "users[*].name") == ["Alice", "Bob"]
json_query(data, "users[*].email") == []  # Missing key
json_query(data, "store.books") == []  # Missing path
```

**Difficulty:** Parsing and nested data traversal
