from typing import Iterator

def read_file_chunks(filename: str, chunk_size: int = 1024) -> Iterator[str]:
    """
    Read file in chunks, yielding non-empty lines.

    Edge case awareness: Must handle line-splitting at chunk boundaries.
    """
    with open(filename, 'r') as f:
        remainder = ""

        # Read chunks using walrus in while condition
        while (chunk := f.read(chunk_size)):
            # Combine remainder from previous chunk with new chunk
            combined = remainder + chunk

            # Split into lines
            lines = combined.splitlines(keepends=True)

            # If last line doesn't end with newline, it's incomplete
            if combined and not combined.endswith('\n'):
                # Save incomplete line for next iteration
                remainder = lines[-1] if lines else ""
                lines = lines[:-1] if lines else []
            else:
                remainder = ""

            # Yield non-empty lines (stripped)
            for line in lines:
                if (stripped := line.strip()):
                    yield stripped

        # Yield final remainder if exists
        if (stripped := remainder.strip()):
            yield stripped
