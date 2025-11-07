"""
Walrus Operator Mastery - ACE Practice Task
============================================

Task: ace_practice_walrus_operator_20251107_063421
Objective: Improve walrus_operator proficiency from 0.0% → 80%

The walrus operator (:=) enables assignment expressions - assigning values
to variables as part of larger expressions. This improves code readability
and performance by avoiding repeated calculations.

This module demonstrates 5 walrus operator patterns targeting common use cases.
"""

from typing import List, Dict, Any, Optional, Iterator
import re
import json


# Exercise 1: Write 5 functions using walrus_operator
# =====================================================

def process_data_stream(data: List[str]) -> List[str]:
    """
    Process data stream, filtering and transforming valid entries.

    Walrus operator avoids duplicate regex matching and validation.
    Without walrus: match once for check, again for extraction
    With walrus: match once, assign, use immediately
    """
    results = []
    pattern = re.compile(r'data_(\d+)_(\w+)')

    for item in data:
        # Walrus: assign match result and check in one expression
        if (match := pattern.match(item)):
            results.append(f"Processed: {match.group(1)} - {match.group(2)}")

    return results


def find_first_valid_config(config_paths: List[str]) -> Optional[Dict[str, Any]]:
    """
    Find first valid configuration file.

    Walrus operator enables early exit with assigned value.
    Avoids loading file twice (once to check, once to return).
    """
    for path in config_paths:
        try:
            with open(path, 'r') as f:
                # Walrus: assign parsed config and check validity
                if (config := json.load(f)) and config.get('valid', False):
                    return config
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return None


def batch_process_with_limit(items: List[int], max_value: int = 100) -> List[int]:
    """
    Process items until cumulative value exceeds limit.

    Walrus operator updates running total while checking limit.
    Cleaner than separate assignment and condition.
    """
    results = []
    total = 0

    for item in items:
        # Walrus: add item to total and check limit in one line
        if (total := total + item) <= max_value:
            results.append(item)
        else:
            break

    return results


def extract_validated_input(prompt: str, validator: callable) -> Optional[str]:
    """
    Get and validate user input in single expression.

    Walrus operator combines input and validation check.
    Useful for interactive loops.
    """
    # Walrus: get input and validate immediately
    # (In real code, this would use input() - here we demonstrate the pattern)
    if (user_input := prompt.lower().strip()) and validator(user_input):
        return user_input
    return None


def generate_while_condition(max_items: int = 10) -> Iterator[int]:
    """
    Generate items with mid-loop condition check.

    Walrus operator in while loop header enables clean iteration.
    """
    items = []
    counter = 0

    # Walrus: increment and check in while condition
    while (counter := counter + 1) <= max_items:
        items.append(counter * 2)
        if counter % 3 == 0:
            yield sum(items)


# Exercise 2: Refactor existing code to use walrus_operator
# ==========================================================

def calculate_statistics_refactored(numbers: List[float]) -> Dict[str, float]:
    """
    Calculate statistics with walrus operator refactoring.

    BEFORE (without walrus):
        filtered = [n for n in numbers if n > 0]
        if len(filtered) > 0:
            avg = sum(filtered) / len(filtered)

    AFTER (with walrus):
        if (n := len(filtered := [n for n in numbers if n > 0])) > 0:
            avg = sum(filtered) / n

    Reduces variable scope and makes data flow explicit.
    """
    stats = {}

    # Walrus in comprehension + outer expression
    if (count := len(filtered := [n for n in numbers if n > 0])) > 0:
        stats['count'] = count
        stats['sum'] = sum(filtered)
        stats['average'] = sum(filtered) / count
        stats['max'] = max(filtered)
        stats['min'] = min(filtered)

    return stats


# Exercise 3: Handle edge cases with walrus_operator
# ==================================================

def safe_divide_with_walrus(numerator: float, denominator: float) -> Optional[float]:
    """
    Safe division with edge case handling using walrus.

    Handles: zero division, infinity, NaN
    Walrus enables check and assign in single expression.
    """
    import math

    # Walrus: perform division and check validity
    if denominator != 0 and not math.isinf(result := numerator / denominator) and not math.isnan(result):
        return result

    return None


def parse_nested_data_safe(data: Dict[str, Any], path: str) -> Optional[Any]:
    """
    Safely navigate nested dictionary with walrus operator.

    Edge cases: missing keys, wrong types, None values
    Walrus enables safe navigation with immediate validation.
    """
    keys = path.split('.')
    current = data

    for key in keys:
        # Walrus: get value and check if valid dict for next iteration
        if not isinstance(current, dict) or (current := current.get(key)) is None:
            return None

    return current


# Exercise 4: Optimize code using walrus_operator
# ===============================================

def expensive_computation_optimized(items: List[int], threshold: int) -> List[int]:
    """
    Optimize by avoiding repeated expensive calls.

    BEFORE:
        if expensive_transform(item) > threshold:
            results.append(expensive_transform(item))  # Called twice!

    AFTER:
        if (transformed := expensive_transform(item)) > threshold:
            results.append(transformed)  # Called once!

    Performance improvement: 50% reduction in expensive_transform calls
    """
    def expensive_transform(x: int) -> int:
        """Simulates expensive computation"""
        return sum(range(x * 100))

    results = []
    for item in items:
        # Walrus: transform once, use twice
        if (transformed := expensive_transform(item)) > threshold:
            results.append(transformed)

    return results


def cached_regex_matching(texts: List[str], pattern: str) -> Dict[str, List[str]]:
    """
    Optimize regex matching with walrus operator.

    Avoids recompiling pattern and re-matching strings.
    Performance: O(n) instead of O(2n) for match + extract.
    """
    compiled = re.compile(pattern)
    matches = {}

    for text in texts:
        # Walrus: match once, extract groups immediately
        if (match := compiled.search(text)):
            matches[text] = match.groups()

    return matches


# Exercise 5: Document walrus_operator usage
# ==========================================

"""
WALRUS OPERATOR (:=) - COMPREHENSIVE GUIDE
=========================================

SYNTAX: (variable := expression)

WHEN TO USE:
1. Avoid repeated function calls
2. Combine assignment + conditional check
3. Reduce variable scope in comprehensions
4. Early exit with computed value
5. Clean up complex conditions

COMMON PATTERNS:

Pattern 1: Conditional Assignment
    if (value := compute_expensive()) > threshold:
        use(value)

Pattern 2: Loop with Mid-Condition
    while (line := file.readline()) != "":
        process(line)

Pattern 3: Comprehension Filtering
    [y for x in items if (y := transform(x)) > 0]

Pattern 4: Nested Assignment
    if (match := pattern.search(text)) and (group := match.group(1)):
        return group

Pattern 5: Multiple Conditions
    if (data := fetch()) and (processed := validate(data)):
        return processed

PERFORMANCE BENEFITS:
- Eliminates duplicate function calls (50% reduction in example above)
- Reduces temporary variables in scope
- Makes data dependencies explicit
- Enables early exit optimizations

READABILITY CONSIDERATIONS:
- Use for simple cases (1-2 levels deep)
- Avoid in complex nested expressions
- Add comments for non-obvious usage
- Consider extraction to separate variable if too complex

PYTHON VERSION: Requires Python 3.8+
PEP: 572 (Assignment Expressions)
"""


# Comprehensive test suite
def test_walrus_operator_mastery():
    """Test all walrus operator patterns."""

    # Test Exercise 1
    assert len(process_data_stream(['data_1_test', 'invalid', 'data_2_prod'])) == 2
    assert batch_process_with_limit([10, 20, 30, 40, 50], max_value=60) == [10, 20, 30]

    # Test Exercise 2
    stats = calculate_statistics_refactored([1.5, 2.5, -1.0, 3.5, 0.0])
    assert stats['count'] == 3
    assert stats['average'] == 2.5

    # Test Exercise 3
    assert safe_divide_with_walrus(10, 2) == 5.0
    assert safe_divide_with_walrus(10, 0) is None
    assert parse_nested_data_safe({'a': {'b': {'c': 42}}}, 'a.b.c') == 42
    assert parse_nested_data_safe({'a': {'b': {}}}, 'a.b.c') is None

    # Test Exercise 4
    optimized = expensive_computation_optimized([1, 2, 3], threshold=1000)
    assert len(optimized) > 0  # Should have some results above threshold

    matches = cached_regex_matching(['test123', 'abc456', 'xyz'], r'(\d+)')
    assert 'test123' in matches
    assert matches['test123'] == ('123',)

    print("✅ All walrus operator tests passed!")
    return True


if __name__ == "__main__":
    print("Walrus Operator Mastery - ACE Practice Task")
    print("=" * 50)
    print("\nExecuting test suite...\n")
    test_walrus_operator_mastery()
    print("\n✅ Practice task complete!")
    print("Walrus operator proficiency: 0.0% → [measuring...]")
