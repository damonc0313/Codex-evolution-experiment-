# Task: Chunked File Reader

Implement a generator function that reads a file in chunks and yields non-empty lines.

**Function signature:**
```python
from typing import Iterator

def read_file_chunks(filename: str, chunk_size: int = 1024) -> Iterator[str]:
    """
    Read file in chunks, yielding non-empty lines.

    Args:
        filename: Path to file to read
        chunk_size: Size of chunks to read at once

    Yields:
        Non-empty lines from the file
    """
    pass
```

**Requirements:**
- Use walrus operator to read chunks in while loop condition
- Yield only non-empty lines (after stripping whitespace)
- Handle chunk boundaries that split lines correctly
- Handle files that don't end with newline
- Close file properly (use context manager)
