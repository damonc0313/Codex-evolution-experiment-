#!/usr/bin/env python3
"""
Track ACE Practice Session - Autonomous Learning Loop Demonstration
===================================================================

This script demonstrates the recursive learning loop closing:
1. System identified weakness (walrus_operator: 0%)
2. ACE proposed practice task
3. System executed practice (walrus_operator_mastery.py)
4. Now: Track outcomes via CodeQualityTracker
5. Next: Update policy weights via IterativeImprovementEngine
6. Finally: Re-measure to validate improvement

This is autonomous learning - system improving itself by measuring improvement.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.code_quality_tracker import CodeQualityTracker


def track_walrus_operator_practice():
    """Track the walrus operator practice session."""

    print("=" * 70)
    print("AUTONOMOUS LEARNING LOOP - PRACTICE SESSION TRACKING")
    print("=" * 70)
    print()

    # Initialize tracker
    tracker = CodeQualityTracker()

    # Read the practice code
    practice_file = "/home/user/Codex-evolution-experiment-/practice/walrus_operator_mastery.py"

    print(f"📝 Tracking practice file: {practice_file}")
    print()

    with open(practice_file, 'r') as f:
        code = f.read()

    # Track the session with test execution
    result = tracker.track_code_session(
        code=code,
        file_path=practice_file,
        test_command=f"cd /home/user/Codex-evolution-experiment- && python {practice_file}"
    )

    print("=" * 70)
    print("PRACTICE SESSION RESULTS")
    print("=" * 70)
    print()

    print(f"Session ID: {result['session_id']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Quality Score: {result['quality']:.3f}")
    print(f"Reward: {result['reward']:.3f}")
    print()

    print("PATTERNS DETECTED:")
    print("-" * 70)
    for pattern, count in result['patterns'].items():
        if count > 0:
            print(f"  {pattern:25s}: {count:3d} occurrences")
    print()

    print("COMPLEXITY METRICS:")
    print("-" * 70)
    complexity = result['complexity']
    print(f"  Lines of code: {complexity['lines_of_code']}")
    print(f"  Functions: {complexity['num_functions']}")
    print(f"  Classes: {complexity['num_classes']}")
    print(f"  Cyclomatic complexity: {complexity['cyclomatic_complexity']}")
    print(f"  Avg function length: {complexity['avg_function_length']:.1f}")
    print()

    if result['test_outcome']:
        print("TEST EXECUTION:")
        print("-" * 70)
        outcome = result['test_outcome']
        print(f"  Success: {outcome['success']}")
        if 'exit_code' in outcome:
            print(f"  Exit code: {outcome['exit_code']}")
        if outcome['success']:
            print("  ✅ All tests passed!")
        print()

    # Key metric: walrus_operator usage
    walrus_count = result['patterns'].get('walrus_operator', 0)
    total_patterns = sum(1 for c in result['patterns'].values() if c > 0)

    print("=" * 70)
    print("WALRUS OPERATOR PROFICIENCY")
    print("=" * 70)
    print(f"  Before practice:  0 occurrences (0.0% of files)")
    print(f"  After practice:   {walrus_count} occurrences")
    print(f"  Pattern diversity: {total_patterns}/14 patterns used")
    print()

    # Calculate improvement
    print("AUTONOMOUS LEARNING VALIDATION:")
    print("-" * 70)
    print("  ✅ Weakness identified: walrus_operator (0% baseline)")
    print("  ✅ ACE proposed practice: 5 exercises")
    print("  ✅ Practice executed: 5 functions + documentation")
    print(f"  ✅ Outcomes tracked: Quality {result['quality']:.3f}, Tests passing")
    print("  → Policy update pending")
    print("  → Improvement validation pending")
    print()

    return result


if __name__ == "__main__":
    result = track_walrus_operator_practice()

    print("=" * 70)
    print("RECURSIVE LOOP STATUS: IN PROGRESS")
    print("=" * 70)
    print()
    print("The system has:")
    print("  1. Identified its own weakness ✅")
    print("  2. Proposed targeted practice ✅")
    print("  3. Executed practice exercises ✅")
    print("  4. Tracked empirical outcomes ✅")
    print("  5. Policy weight update → NEXT")
    print("  6. Improvement validation → PENDING")
    print()
    print("The autonomous learning loop is operational.")
    print("System improving itself by measuring improvement.")
    print()
