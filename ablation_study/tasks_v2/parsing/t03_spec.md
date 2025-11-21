# Task: CSV Parser with Quoted Fields

Parse CSV handling quotes, escapes, and multi-line fields.

**Function signature:**
```python
def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    Parse CSV text into rows and fields, handling quotes and escapes.

    Args:
        text: CSV text content
        delimiter: Field delimiter (default comma)

    Returns:
        List of rows, each row is list of field strings

    CSV rules:
    - Fields may be quoted with double quotes
    - Quoted fields can contain delimiter, newlines, quotes
    - Quotes inside quoted fields are escaped as ""
    - Unquoted fields cannot contain delimiter or newline
    """
    pass
```

**Requirements:**
- Handle quoted fields: `"field with, comma"`
- Handle escaped quotes: `"field with ""quotes"""`
- Handle multi-line quoted fields
- Trim whitespace around unquoted fields
- Preserve whitespace in quoted fields
- Empty fields should be empty strings

**Example:**
```python
text = '''name,age,city
Alice,30,New York
"Bob ""Bobby""",25,"San Francisco, CA"'''

parse_csv(text) == [
    ["name", "age", "city"],
    ["Alice", "30", "New York"],
    ["Bob \"Bobby\"", "25", "San Francisco, CA"]
]
```

**Difficulty:** State machine parsing with edge cases
