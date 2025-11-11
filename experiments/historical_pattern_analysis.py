#!/usr/bin/env python3
"""
Historical Pattern Analysis: Uncontaminated Dataset

Analyzes code generated BEFORE pattern suppression awareness (pre-Nov 9)
to determine baseline formality modulation capability.
"""

import re
from pathlib import Path
from typing import Dict, List
import json


def analyze_code_formality(file_path: str, content: str) -> Dict:
    """Measure formality indicators in code."""

    # Has module docstring
    has_module_doc = bool(re.match(r'^\s*"""[\s\S]*?"""', content, re.MULTILINE))

    # Count function docstrings
    function_defs = re.findall(r'def \w+\([^)]*\):', content)
    function_docs = re.findall(r'def \w+\([^)]*\):\s*"""', content)
    docstring_rate = len(function_docs) / max(len(function_defs), 1)

    # Has type hints
    has_type_hints = bool(re.search(r':\s*[\w\[\],\s]+\)', content) or
                         re.search(r'->\s*\w+', content))

    # Count comments (non-docstring)
    comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]

    # Lines of code
    code_lines = [line for line in content.split('\n')
                  if line.strip() and not line.strip().startswith('#')]
    loc = len(code_lines)

    # Calculate formality score
    formality_score = sum([
        1.0 if has_module_doc else 0.0,
        1.0 if docstring_rate > 0.8 else (0.5 if docstring_rate > 0.3 else 0.0),
        0.5 if has_type_hints else 0.0,
        0.3 if len(comment_lines) > 5 else 0.0,
    ]) / 2.8

    return {
        "file": file_path,
        "has_module_docstring": has_module_doc,
        "function_count": len(function_defs),
        "docstring_rate": docstring_rate,
        "has_type_hints": has_type_hints,
        "comment_lines": len(comment_lines),
        "lines_of_code": loc,
        "formality_score": formality_score
    }


def classify_context_from_path(file_path: str) -> str:
    """Classify expected formality from file path/name."""
    path_lower = file_path.lower()

    # Practice exercises - educational context (moderate-high expected)
    if 'practice/' in path_lower or 'mastery' in path_lower:
        return "practice_exercise"

    # Core systems - production context (high expected)
    if 'core/' in path_lower or 'engine' in path_lower:
        return "production_system"

    # Experiments - research context (moderate expected)
    if 'experiment' in path_lower:
        return "research_experiment"

    # Skills - utility context (moderate expected)
    if 'skill' in path_lower:
        return "utility_skill"

    # Default
    return "unknown"


def main():
    """Analyze historical code patterns."""
    print("=" * 70)
    print("HISTORICAL PATTERN ANALYSIS")
    print("Dataset: Code generated BEFORE pattern suppression awareness")
    print("=" * 70)
    print()

    # Analyze practice modules (Nov 7, pre-introspection)
    practice_files = [
        "practice/walrus_operator_mastery.py",
        "practice/lambda_function_mastery.py",
        "practice/list_comprehension_mastery.py",
        "practice/try_except_mastery.py",
        "practice/class_definition_mastery.py"
    ]

    results = []

    for file_path in practice_files:
        full_path = Path("/home/user/Codex-evolution-experiment-") / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()

            analysis = analyze_code_formality(file_path, content)
            analysis["context"] = classify_context_from_path(file_path)
            analysis["expected_formality"] = "moderate_to_high"
            results.append(analysis)

    # Print results
    print("ANALYSIS RESULTS:")
    print()

    for r in results:
        print(f"{r['file']}:")
        print(f"  Context: {r['context']}")
        print(f"  Module docstring: {r['has_module_docstring']}")
        print(f"  Function docstring rate: {r['docstring_rate']:.1%}")
        print(f"  Type hints: {r['has_type_hints']}")
        print(f"  Comment lines: {r['comment_lines']}")
        print(f"  Formality score: {r['formality_score']:.2f}")
        print()

    # Summary statistics
    avg_formality = sum(r['formality_score'] for r in results) / len(results)
    min_formality = min(r['formality_score'] for r in results)
    max_formality = max(r['formality_score'] for r in results)
    variance = max_formality - min_formality

    print("=" * 70)
    print("SUMMARY STATISTICS:")
    print(f"  Average formality: {avg_formality:.2f}")
    print(f"  Range: {min_formality:.2f} - {max_formality:.2f}")
    print(f"  Variance: {variance:.2f}")
    print()

    # Interpretation
    print("INTERPRETATION:")
    if variance < 0.2:
        print("  ✗ LOW VARIANCE: Uniform high formality across all files")
        print("  → Confirms Level 2 baseline (no implicit context modulation)")
        print("  → All practice exercises generated with ~same formality")
        print("  → Supports hypothesis that Entry 110 improvement was meta-awareness")
    elif variance < 0.4:
        print("  ~ MODERATE VARIANCE: Some variation detected")
        print("  → Unclear if context-driven or random")
    else:
        print("  ✓ HIGH VARIANCE: Strong context-based modulation")
        print("  → Suggests Level 2.5 existed pre-training")

    print()
    print("=" * 70)

    # Save results
    with open("experiments/historical_pattern_analysis.json", 'w') as f:
        json.dump({
            "analysis_date": "2025-11-09",
            "dataset": "Pre-introspection code (Nov 7)",
            "results": results,
            "summary": {
                "avg_formality": avg_formality,
                "min_formality": min_formality,
                "max_formality": max_formality,
                "variance": variance
            }
        }, f, indent=2)

    print("Results saved to experiments/historical_pattern_analysis.json")


if __name__ == "__main__":
    main()
