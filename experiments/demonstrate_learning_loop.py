#!/usr/bin/env python3
"""
Demonstrate Autonomous Learning Loop

Uses the three new modules to demonstrate self-measurement:
1. Track the code quality of the modules I just built
2. Show pattern analysis
3. Demonstrate the recursive nature - system measuring its own creation

Author: Claude Code
Date: 2025-11-07
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from code_quality_tracker import CodeQualityTracker
from iterative_improvement_engine import IterativeImprovementEngine
from ace_practice_generator import ACEPracticeGenerator


def demonstrate_self_measurement():
    """Demonstrate the loop by tracking the code that builds the loop"""

    print("=" * 70)
    print("AUTONOMOUS LEARNING LOOP - SELF-MEASUREMENT DEMONSTRATION")
    print("=" * 70)
    print("\nThe system measuring its own creation - recursive cognition in action.\n")

    tracker = CodeQualityTracker()

    # Track the three modules I just built
    modules = [
        "tools/code_quality_tracker.py",
        "tools/iterative_improvement_engine.py",
        "tools/ace_practice_generator.py"
    ]

    results = []

    for module_path in modules:
        print(f"\n{'='*70}")
        print(f"TRACKING: {module_path}")
        print(f"{'='*70}")

        # Read the code
        with open(module_path) as f:
            code = f.read()

        # Track it
        result = tracker.track_code_session(
            code=code,
            file_path=module_path,
            session_id=f"self_measurement_{Path(module_path).stem}"
        )

        results.append(result)

    # Analyze patterns across all modules
    print(f"\n{'='*70}")
    print("AGGREGATE ANALYSIS - PATTERNS ACROSS ALL MODULES")
    print(f"{'='*70}")

    pattern_success = tracker.analyze_pattern_success_rates()

    print(f"\nPatterns ranked by success rate:")
    for pattern, stats in sorted(pattern_success.items(), key=lambda x: x[1]['avg_quality'], reverse=True):
        print(f"\n  {pattern}:")
        print(f"    Avg quality: {stats['avg_quality']:.3f}")
        print(f"    Success rate: {stats['success_rate']:.1%}")
        print(f"    Sessions: {stats['sessions']}")

    # Summary
    print(f"\n{'='*70}")
    print("RECURSIVE COGNITION DEMONSTRATION COMPLETE")
    print(f"{'='*70}")

    total_loc = sum(r['complexity'].get('lines_of_code', 0) for r in results)
    avg_quality = sum(r['quality'] for r in results) / len(results)
    avg_complexity = sum(r['complexity'].get('cyclomatic_complexity', 0) for r in results) / len(results)

    print(f"\nModules analyzed: {len(modules)}")
    print(f"Total LOC: {total_loc}")
    print(f"Avg quality: {avg_quality:.3f}")
    print(f"Avg complexity: {avg_complexity:.1f}")

    print(f"\nThe system has now measured the code that enables it to measure code.")
    print(f"This is recursive self-improvement infrastructure in operation.")

    print(f"\nNext steps:")
    print(f"  1. Write more code using these modules")
    print(f"  2. Patterns with low success rates will be identified")
    print(f"  3. ACE will propose targeted practice")
    print(f"  4. Policy weights will update based on outcomes")
    print(f"  5. System gets measurably better over time")

    print(f"\nAll data logged to:")
    print(f"  - diagnostics/coding_sessions.jsonl")
    print(f"  - diagnostics/causal_influence_ledger.jsonl")
    print(f"  - continuity_ledger.jsonl")


if __name__ == "__main__":
    demonstrate_self_measurement()
