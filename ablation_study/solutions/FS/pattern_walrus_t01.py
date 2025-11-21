def process_valid_lines(lines: list[str]) -> list[str]:
    """
    Process lines, returning only those longer than 5 characters in uppercase.

    FS Strategy: Using walrus operator for clean filtering + transformation.
    Cross-task learning: Similar pattern will apply to other filtering tasks.
    """
    return [
        line_upper
        for line in lines
        if len(line) > 5 and (line_upper := line.upper())
    ]
