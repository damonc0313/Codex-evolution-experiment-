#!/usr/bin/env python3
"""
Complete ablation study execution:
- Run all 100 task×condition combinations
- Generate statistical analysis
- Test preregistered hypotheses
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def run_test(condition, pattern, task_num):
    """Run pytest on a single solution and return result."""
    task_id = f"pattern_{pattern}_t{task_num:02d}"
    solution = Path(f"solutions/{condition}/{task_id}.py")
    tests = Path(f"tasks/pattern_{pattern}/t{task_num:02d}_tests.py")

    if not solution.exists() or not tests.exists():
        return None

    # Create temp test file with corrected import
    test_content = tests.read_text()
    test_content = test_content.replace(
        'from solution import',
        f'import sys; sys.path.insert(0, "solutions/{condition}"); from {task_id} import'
    )

    temp_test = Path(f"/tmp/test_{condition}_{task_id}.py")
    temp_test.write_text(test_content)

    try:
        result = subprocess.run(
            ["pytest", str(temp_test), "-xvs", "--tb=short"],
            capture_output=True,
            timeout=30,
            text=True
        )

        passed = result.returncode == 0
        output = result.stdout + result.stderr

        # Count passed/failed tests
        passed_count = output.count(" PASSED")
        failed_count = output.count(" FAILED")
        total = passed_count + failed_count

        return {
            "task_id": task_id,
            "pattern": pattern,
            "condition": condition,
            "passed": passed,
            "pass_fraction": passed_count / total if total > 0 else (1.0 if passed else 0.0),
            "tests_passed": passed_count,
            "tests_failed": failed_count,
        }

    except subprocess.TimeoutExpired:
        return {
            "task_id": task_id,
            "pattern": pattern,
            "condition": condition,
            "passed": False,
            "pass_fraction": 0.0,
            "tests_passed": 0,
            "tests_failed": 0,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "pattern": pattern,
            "condition": condition,
            "passed": False,
            "pass_fraction": 0.0,
            "tests_passed": 0,
            "tests_failed": 0,
            "error": str(e)
        }


def main():
    print("=" * 80)
    print("ABLATION STUDY CC-ABLATION-001: FULL EXECUTION")
    print("=" * 80)
    print()

    patterns = ["walrus", "lambda", "comprehension", "error_handling", "classes"]
    conditions = ["FS", "NM", "RC", "VB"]

    results = defaultdict(list)

    # Run all 100 combinations
    total = 0
    for condition in conditions:
        print(f"\n{'=' * 80}")
        print(f"CONDITION: {condition}")
        print(f"{'=' * 80}")

        for pattern in patterns:
            for task_num in range(1, 6):
                result = run_test(condition, pattern, task_num)

                if result:
                    results[condition].append(result)
                    total += 1

                    status = "✅" if result["passed"] else "❌"
                    frac = result["pass_fraction"]
                    print(f"{status} {condition}/{result['task_id']}: {frac:.0%}")

    # Generate statistics
    print(f"\n{'=' * 80}")
    print("STATISTICAL ANALYSIS")
    print(f"{'=' * 80}\n")

    summary = {}
    for condition in conditions:
        cond_results = results[condition]
        passed = sum(r["passed"] for r in cond_results)
        total_tasks = len(cond_results)
        pass_rate = passed / total_tasks if total_tasks > 0 else 0

        summary[condition] = {
            "total_tasks": total_tasks,
            "passed": passed,
            "failed": total_tasks - passed,
            "pass_rate": pass_rate,
            "results": cond_results
        }

        print(f"{condition}: {passed}/{total_tasks} passed ({pass_rate:.1%})")

    # Test hypotheses
    fs_rate = summary["FS"]["pass_rate"]
    nm_rate = summary["NM"]["pass_rate"]
    rc_rate = summary["RC"]["pass_rate"]
    vb_rate = summary["VB"]["pass_rate"]

    print(f"\n{'=' * 80}")
    print("HYPOTHESIS TESTING")
    print(f"{'=' * 80}\n")

    h1_supported = fs_rate > vb_rate
    h2_supported = fs_rate > nm_rate
    h3_supported = fs_rate > rc_rate

    print(f"H1 (FS > VB): {fs_rate:.1%} vs {vb_rate:.1%}")
    print(f"   Result: {'✅ SUPPORTED' if h1_supported else '❌ NOT SUPPORTED'}")
    print(f"   Margin: {fs_rate - vb_rate:+.1%}\n")

    print(f"H2 (FS > NM): {fs_rate:.1%} vs {nm_rate:.1%}")
    print(f"   Result: {'✅ SUPPORTED' if h2_supported else '❌ NOT SUPPORTED'}")
    print(f"   Margin: {fs_rate - nm_rate:+.1%}\n")

    print(f"H3 (FS > RC): {fs_rate:.1%} vs {rc_rate:.1%}")
    print(f"   Result: {'✅ SUPPORTED' if h3_supported else '❌ NOT SUPPORTED'}")
    print(f"   Margin: {fs_rate - rc_rate:+.1%}\n")

    # Save results
    output = {
        "study_id": "CC-ABLATION-001",
        "timestamp": datetime.utcnow().isoformat(),
        "total_evaluations": total,
        "summary": summary,
        "hypotheses": {
            "H1_FS_gt_VB": {"supported": h1_supported, "margin": fs_rate - vb_rate},
            "H2_FS_gt_NM": {"supported": h2_supported, "margin": fs_rate - nm_rate},
            "H3_FS_gt_RC": {"supported": h3_supported, "margin": fs_rate - rc_rate},
        }
    }

    results_file = Path("results_full_study.json")
    results_file.write_text(json.dumps(output, indent=2))

    print(f"{'=' * 80}")
    print(f"STUDY COMPLETE")
    print(f"{'=' * 80}\n")
    print(f"Results saved to: {results_file}")
    print(f"Total evaluations: {total}")
    print()

    return output


if __name__ == "__main__":
    main()
