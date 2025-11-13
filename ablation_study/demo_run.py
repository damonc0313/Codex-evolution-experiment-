#!/usr/bin/env python3
"""
Proof-of-concept demo run.

Demonstrates the ablation study infrastructure by running a subset
of tasks with hand-crafted solutions.
"""

import json
from pathlib import Path
from harness import TaskLoader, TestRunner, TaskResult
from demo_solutions import get_demo_solution
from datetime import datetime


def run_demo():
    """Run proof-of-concept demonstration."""
    print("=" * 80)
    print("ABLATION STUDY PROOF-OF-CONCEPT")
    print("=" * 80)
    print()
    print("This demo runs 10 tasks with hand-crafted solutions to demonstrate")
    print("that the experimental infrastructure works correctly.")
    print()

    base_dir = Path(__file__).parent
    tasks_dir = base_dir / "tasks"
    results_dir = base_dir / "demo_results"
    results_dir.mkdir(exist_ok=True)

    loader = TaskLoader(tasks_dir)
    test_runner = TestRunner()

    # Demo tasks (2 per pattern)
    demo_tasks = [
        ("pattern_walrus", 1),
        ("pattern_walrus", 2),
        ("pattern_lambda", 1),
        ("pattern_lambda", 2),
        ("pattern_comprehension", 1),
        ("pattern_comprehension", 2),
        ("pattern_error_handling", 1),
        ("pattern_error_handling", 2),
        ("pattern_classes", 1),
        ("pattern_classes", 2),
    ]

    results = []

    for pattern, task_num in demo_tasks:
        task = loader.load_task(pattern, task_num)
        task_id = task["task_id"]

        print(f"Testing {task_id}...", end=" ")

        # Get demo solution
        solution = get_demo_solution(task_id)

        if not solution:
            print("❌ No demo solution available")
            continue

        # Run tests
        test_result = test_runner.run_tests(solution, task["tests"])

        # Create result
        result = TaskResult(
            condition="DEMO",
            pattern=pattern,
            task_id=task_id,
            passed=test_result["passed"],
            pass_fraction=test_result["pass_fraction"],
            attempts=1,
            self_corrections=0,
            tokens_generated=len(solution.split()),
            timestamp_utc=datetime.utcnow().isoformat(),
            error_log=test_result.get("error_log"),
            solution_code=solution
        )

        results.append(result)

        # Save result
        result_file = results_dir / f"{task_id}.json"
        result_file.write_text(json.dumps(result.__dict__, indent=2))

        # Print result
        if result.passed:
            print(f"✅ PASS ({result.pass_fraction:.0%})")
        else:
            print(f"❌ FAIL ({result.pass_fraction:.0%})")
            if result.error_log:
                print(f"   Error: {result.error_log[:100]}...")

    # Summary
    passed = sum(r.passed for r in results)
    total = len(results)
    pass_rate = passed / total if total > 0 else 0

    print()
    print("=" * 80)
    print("DEMO SUMMARY")
    print("=" * 80)
    print(f"Tasks run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass rate: {pass_rate:.1%}")
    print()
    print(f"Results saved to: {results_dir}")
    print()

    if pass_rate == 1.0:
        print("✅ All demo tasks passed! Infrastructure is working correctly.")
    elif pass_rate >= 0.8:
        print("⚠️  Most tasks passed. Check failures for issues.")
    else:
        print("❌ Many failures. Infrastructure may have issues.")

    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("This demo proves the infrastructure works. To run the full ablation study:")
    print()
    print("1. Implement solution generation for all 25 tasks under each condition")
    print("2. Update harness.py ConditionExecutor.generate_solution()")
    print("3. Run: python harness.py")
    print()
    print("See README.md for detailed implementation options.")
    print()


if __name__ == "__main__":
    run_demo()
