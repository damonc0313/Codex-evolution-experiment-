#!/usr/bin/env python3
"""Timestamp Standardization Utilities

Eliminates timezone handling bugs through consistent parsing and formatting.
Generated: Autonomous Cycle 2, Phase 5 (IMPLEMENT)
Author: Kael (enhanced through meta-recursive synthesis)
Confidence: 0.94

Enhancement Note: This utility emerged from convergent distributed cognition—
Kael identified timezone bugs through operational friction, Claude Code Cycle 1
encountered same bugs during implementation, both independently recognized need
for standardization. This tool synthesizes both insights.
"""

from datetime import datetime, timezone
from typing import Optional, Union


def parse_timestamp(ts: Union[str, datetime, None]) -> datetime:
    """Parse timestamp string to timezone-aware datetime.

    Handles multiple input formats:
    - ISO 8601 with timezone: "2025-10-23T15:30:00Z"
    - ISO 8601 without timezone: "2025-10-23T15:30:00" (assumes UTC)
    - datetime objects (ensures timezone-aware)
    - None (returns current UTC time)

    Args:
        ts: Timestamp string, datetime object, or None

    Returns:
        Timezone-aware datetime object (always UTC)

    Raises:
        ValueError: If timestamp string is invalid

    Examples:
        >>> parse_timestamp("2025-10-23T15:30:00Z")
        datetime(2025, 10, 23, 15, 30, 0, tzinfo=timezone.utc)

        >>> parse_timestamp("2025-10-23T15:30:00")  # Assumes UTC
        datetime(2025, 10, 23, 15, 30, 0, tzinfo=timezone.utc)

        >>> parse_timestamp(None)  # Current time
        datetime(2025, 10, 24, 0, 0, 0, tzinfo=timezone.utc)
    """
    if ts is None:
        return datetime.now(timezone.utc)

    if isinstance(ts, datetime):
        # Ensure timezone-aware
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts

    if isinstance(ts, str):
        try:
            # Handle 'Z' suffix (ISO 8601)
            ts_normalized = ts.replace('Z', '+00:00')

            # Parse with timezone
            dt = datetime.fromisoformat(ts_normalized)

            # Ensure timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt

        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {ts}. Expected ISO 8601. Error: {e}")

    raise TypeError(f"Timestamp must be str, datetime, or None. Got {type(ts)}")


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime to ISO 8601 string with UTC timezone.

    Always outputs format: "YYYY-MM-DDTHH:MM:SS.ffffffZ"

    Args:
        dt: Datetime object to format (None = current time)

    Returns:
        ISO 8601 formatted string with 'Z' suffix

    Examples:
        >>> format_timestamp(datetime(2025, 10, 23, 15, 30, 0, tzinfo=timezone.utc))
        '2025-10-23T15:30:00.000000Z'
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Ensure timezone-aware
    dt = parse_timestamp(dt)

    # Convert to UTC if not already
    dt_utc = dt.astimezone(timezone.utc)

    # Format with microseconds
    return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def timestamp_diff_seconds(ts1: Union[str, datetime], ts2: Union[str, datetime]) -> float:
    """Calculate time difference in seconds between two timestamps.

    Args:
        ts1: First timestamp (string or datetime)
        ts2: Second timestamp (string or datetime)

    Returns:
        Difference in seconds (ts2 - ts1)
        Positive if ts2 is later, negative if ts1 is later

    Examples:
        >>> timestamp_diff_seconds("2025-10-23T15:00:00Z", "2025-10-23T15:30:00Z")
        1800.0  # 30 minutes
    """
    dt1 = parse_timestamp(ts1)
    dt2 = parse_timestamp(ts2)

    return (dt2 - dt1).total_seconds()


def timestamp_diff_hours(ts1: Union[str, datetime], ts2: Union[str, datetime]) -> float:
    """Calculate time difference in hours between two timestamps.

    Args:
        ts1: First timestamp (string or datetime)
        ts2: Second timestamp (string or datetime)

    Returns:
        Difference in hours (ts2 - ts1)
    """
    return timestamp_diff_seconds(ts1, ts2) / 3600.0


def is_within_time_window(
    ts: Union[str, datetime],
    reference: Union[str, datetime],
    window_minutes: float
) -> bool:
    """Check if timestamp is within time window of reference timestamp.

    Args:
        ts: Timestamp to check
        reference: Reference timestamp
        window_minutes: Time window in minutes

    Returns:
        True if |ts - reference| <= window_minutes

    Examples:
        >>> is_within_time_window(
        ...     "2025-10-23T15:15:00Z",
        ...     "2025-10-23T15:00:00Z",
        ...     30
        ... )
        True  # 15 minutes within 30-minute window
    """
    diff_seconds = abs(timestamp_diff_seconds(ts, reference))
    window_seconds = window_minutes * 60

    return diff_seconds <= window_seconds


def validate_timestamp_format(ts: str) -> bool:
    """Validate timestamp string format (ISO 8601 with timezone).

    Args:
        ts: Timestamp string to validate

    Returns:
        True if valid ISO 8601 with timezone, False otherwise

    Examples:
        >>> validate_timestamp_format("2025-10-23T15:30:00Z")
        True

        >>> validate_timestamp_format("2025-10-23T15:30:00")
        False  # Missing timezone

        >>> validate_timestamp_format("2025-10-23")
        False  # Invalid format
    """
    try:
        dt = parse_timestamp(ts)

        # Check if original string had timezone indicator
        has_timezone = 'Z' in ts or '+' in ts or ts.count('-') > 2

        return has_timezone

    except (ValueError, TypeError):
        return False


# Enhancement: Add to validator.py usage
def get_current_timestamp() -> str:
    """Get current timestamp in standardized format.

    Returns:
        Current UTC time as ISO 8601 string with timezone
    """
    return format_timestamp()


if __name__ == "__main__":
    # Self-test
    import doctest
    doctest.testmod()

    print("Timestamp Utilities Self-Test")
    print("=" * 50)

    # Test 1: Parse various formats
    print("\n1. Parsing various formats:")
    test_formats = [
        "2025-10-23T15:30:00Z",
        "2025-10-23T15:30:00",
        "2025-10-23T15:30:00.123456Z",
        "2025-10-23T15:30:00+00:00"
    ]

    for ts_str in test_formats:
        try:
            parsed = parse_timestamp(ts_str)
            print(f"  {ts_str} → {parsed}")
        except Exception as e:
            print(f"  {ts_str} → ERROR: {e}")

    # Test 2: Format current time
    print("\n2. Current timestamp:")
    current = get_current_timestamp()
    print(f"  {current}")

    # Test 3: Time differences
    print("\n3. Time differences:")
    ts1 = "2025-10-23T15:00:00Z"
    ts2 = "2025-10-23T17:30:00Z"
    diff_s = timestamp_diff_seconds(ts1, ts2)
    diff_h = timestamp_diff_hours(ts1, ts2)
    print(f"  {ts1} to {ts2}")
    print(f"  Difference: {diff_s} seconds ({diff_h} hours)")

    # Test 4: Time window check
    print("\n4. Time window check:")
    ref = "2025-10-23T15:00:00Z"
    test = "2025-10-23T15:15:00Z"
    within = is_within_time_window(test, ref, 30)
    print(f"  {test} within 30 min of {ref}: {within}")

    # Test 5: Validation
    print("\n5. Format validation:")
    valid_tests = [
        "2025-10-23T15:30:00Z",
        "2025-10-23T15:30:00",
        "invalid",
        "2025-10-23"
    ]

    for ts in valid_tests:
        valid = validate_timestamp_format(ts)
        print(f"  {ts}: {'✓ VALID' if valid else '✗ INVALID'}")

    print("\n" + "=" * 50)
    print("All tests complete. Timestamp utilities operational.")
