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
    if not text:
        return []

    # State machine states
    START = 0       # Beginning of a field
    UNQUOTED = 1    # Inside an unquoted field
    QUOTED = 2      # Inside a quoted field
    QUOTE_END = 3   # Just saw a quote that might end the quoted field

    rows = []
    current_row = []
    current_field = []
    state = START
    expecting_field = False  # Track if we're expecting a new field after delimiter

    i = 0
    while i < len(text):
        char = text[i]

        if state == START:
            # Beginning of a new field
            if char == '"':
                state = QUOTED
                expecting_field = False
            elif char == delimiter:
                # Empty field
                current_row.append("")
                expecting_field = True  # We're now expecting another field
            elif char == '\n':
                # Empty field at end of row (only if we were expecting a field)
                if expecting_field:
                    current_row.append("")
                if current_row:
                    rows.append(current_row)
                current_row = []
                expecting_field = False
            elif char == '\r':
                # Handle \r\n
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1
                if expecting_field:
                    current_row.append("")
                if current_row:
                    rows.append(current_row)
                current_row = []
                expecting_field = False
            else:
                # Start of unquoted field
                current_field.append(char)
                state = UNQUOTED
                expecting_field = False

        elif state == UNQUOTED:
            if char == delimiter:
                # End of field
                field_value = ''.join(current_field).strip()
                current_row.append(field_value)
                current_field = []
                state = START
                expecting_field = True  # Expecting another field after delimiter
            elif char == '\n':
                # End of field and row
                field_value = ''.join(current_field).strip()
                current_row.append(field_value)
                rows.append(current_row)
                current_row = []
                current_field = []
                state = START
                expecting_field = False
            elif char == '\r':
                # Handle \r\n
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1
                field_value = ''.join(current_field).strip()
                current_row.append(field_value)
                rows.append(current_row)
                current_row = []
                current_field = []
                state = START
                expecting_field = False
            else:
                current_field.append(char)

        elif state == QUOTED:
            if char == '"':
                # Might be end of quoted field or escaped quote
                state = QUOTE_END
            else:
                # Any character inside quoted field (including newlines, delimiters)
                current_field.append(char)

        elif state == QUOTE_END:
            if char == '"':
                # Escaped quote - add single quote and continue in quoted state
                current_field.append('"')
                state = QUOTED
            elif char == delimiter:
                # End of quoted field, move to next field
                current_row.append(''.join(current_field))
                current_field = []
                state = START
                expecting_field = True  # Expecting another field after delimiter
            elif char == '\n':
                # End of quoted field and row
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                state = START
                expecting_field = False
            elif char == '\r':
                # Handle \r\n
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 1
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                state = START
                expecting_field = False
            else:
                # Character after closing quote - technically malformed, but handle gracefully
                # Just continue as if we're unquoted now
                current_field.append(char)
                state = UNQUOTED

        i += 1

    # Handle remaining content at end of text
    if state == UNQUOTED:
        field_value = ''.join(current_field).strip()
        current_row.append(field_value)
    elif state == QUOTED:
        # Unclosed quote - just take what we have
        current_row.append(''.join(current_field))
    elif state == QUOTE_END:
        # End of text right after closing quote
        current_row.append(''.join(current_field))
    elif state == START:
        # Text ended with delimiter (expecting another field)
        if expecting_field:
            current_row.append("")

    # Add final row if it has content
    if current_row:
        rows.append(current_row)

    return rows
