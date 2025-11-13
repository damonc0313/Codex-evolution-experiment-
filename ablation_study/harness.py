#!/usr/bin/env python3
"""
Experimental harness for ablation study.
Runs coding tasks under 4 conditions: FS, NM, RC, VB
"""

import json
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
import random


@dataclass
class TaskResult:
    """Result of running a single task."""
    condition: str
    pattern: str
    task_id: str
    passed: bool
    pass_fraction: float
    attempts: int
    self_corrections: int
    tokens_generated: int
    timestamp_utc: str
    error_log: Optional[str] = None
    solution_code: Optional[str] = None


class TaskLoader:
    """Loads task specifications and tests."""

    def __init__(self, tasks_dir: Path):
        self.tasks_dir = tasks_dir

    def load_task(self, pattern: str, task_num: int) -> dict:
        """Load task specification and tests."""
        task_dir = self.tasks_dir / pattern / f"t{task_num:02d}"
        spec_file = self.tasks_dir / pattern / f"t{task_num:02d}_spec.md"
        tests_file = self.tasks_dir / pattern / f"t{task_num:02d}_tests.py"

        if not spec_file.exists() or not tests_file.exists():
            raise FileNotFoundError(f"Task {pattern}/t{task_num:02d} not found")

        return {
            "pattern": pattern,
            "task_id": f"{pattern}_t{task_num:02d}",
            "spec": spec_file.read_text(),
            "tests": tests_file.read_text()
        }

    def list_all_tasks(self) -> list[tuple[str, int]]:
        """List all available tasks as (pattern, task_num) tuples."""
        tasks = []
        patterns = ["pattern_walrus", "pattern_lambda", "pattern_comprehension",
                    "pattern_error_handling", "pattern_classes"]

        for pattern in patterns:
            pattern_dir = self.tasks_dir / pattern
            if pattern_dir.exists():
                for i in range(1, 6):  # 5 tasks per pattern
                    spec_file = self.tasks_dir / pattern / f"t{i:02d}_spec.md"
                    if spec_file.exists():
                        tasks.append((pattern, i))

        return tasks


class TestRunner:
    """Runs pytest on generated solutions."""

    def run_tests(self, solution_code: str, test_code: str, timeout: int = 60) -> dict:
        """
        Run tests on solution code.

        Returns:
            dict with 'passed', 'pass_fraction', 'error_log'
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write solution and tests
            solution_file = Path(tmpdir) / "solution.py"
            test_file = Path(tmpdir) / "test_solution.py"

            solution_file.write_text(solution_code)
            test_file.write_text(test_code)

            # Run pytest
            try:
                result = subprocess.run(
                    ["pytest", str(test_file), "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir
                )

                # Parse results
                passed = result.returncode == 0
                output = result.stdout + result.stderr

                # Count passed/failed tests
                passed_count = output.count(" PASSED")
                failed_count = output.count(" FAILED")
                total = passed_count + failed_count

                pass_fraction = passed_count / total if total > 0 else 0.0

                return {
                    "passed": passed,
                    "pass_fraction": pass_fraction,
                    "error_log": None if passed else output[-1000:]  # Last 1000 chars
                }

            except subprocess.TimeoutExpired:
                return {
                    "passed": False,
                    "pass_fraction": 0.0,
                    "error_log": "Test execution timeout"
                }
            except Exception as e:
                return {
                    "passed": False,
                    "pass_fraction": 0.0,
                    "error_log": f"Test execution error: {str(e)}"
                }


class ConditionExecutor:
    """Executes tasks under different experimental conditions."""

    def __init__(self, condition: str):
        self.condition = condition
        self.test_runner = TestRunner()

    def generate_solution(self, task: dict, attempt: int = 0) -> str:
        """
        Generate solution code for the task.

        This is a placeholder - in real implementation, this would:
        - For FS: Use full scaffolding (CIL, ACE, learning kernel, self-directed)
        - For NM: Stateless generation
        - For RC: Memory but random task selection
        - For VB: Vanilla Claude Code

        For now, returns a template that needs to be filled in.
        """
        spec = task["spec"]

        # Extract function signatures and requirements from spec
        # This is a simplified version - real implementation would parse spec
        # and generate actual working code

        # Return template (caller needs to fill this in with real implementation)
        return f'''"""
Generated solution for {task['task_id']} under condition {self.condition}
Attempt: {attempt + 1}

Specification:
{spec}
"""

# TODO: Implement solution based on specification
# This is a placeholder - real implementation would generate working code
pass
'''

    def execute_task(
        self,
        task: dict,
        max_attempts: int = 5,
        timeout: int = 600
    ) -> TaskResult:
        """
        Execute a single task under this condition.

        Args:
            task: Task dictionary with spec and tests
            max_attempts: Maximum solution attempts
            timeout: Maximum time in seconds

        Returns:
            TaskResult with metrics
        """
        start_time = time.time()
        attempts = 0
        self_corrections = 0
        tokens_generated = 0

        solution_code = None
        test_result = None

        for attempt in range(max_attempts):
            if time.time() - start_time > timeout:
                break

            attempts += 1

            # Generate solution
            solution_code = self.generate_solution(task, attempt)
            tokens_generated += len(solution_code.split())  # Rough token estimate

            # Run tests
            test_result = self.test_runner.run_tests(solution_code, task["tests"])

            if test_result["passed"]:
                break

            # If failed, we'll try again (this counts as self-correction)
            if attempt < max_attempts - 1:
                self_corrections += 1

        # Build result
        return TaskResult(
            condition=self.condition,
            pattern=task["pattern"],
            task_id=task["task_id"],
            passed=test_result["passed"] if test_result else False,
            pass_fraction=test_result["pass_fraction"] if test_result else 0.0,
            attempts=attempts,
            self_corrections=self_corrections,
            tokens_generated=tokens_generated,
            timestamp_utc=datetime.utcnow().isoformat(),
            error_log=test_result["error_log"] if test_result else "No attempts completed",
            solution_code=solution_code
        )


class AblationHarness:
    """Main harness orchestrating the ablation study."""

    def __init__(self, tasks_dir: Path, results_dir: Path):
        self.task_loader = TaskLoader(tasks_dir)
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_condition(
        self,
        condition: str,
        tasks: list[tuple[str, int]],
        shuffle: bool = False
    ) -> list[TaskResult]:
        """
        Run all tasks under a specific condition.

        Args:
            condition: Condition name (FS, NM, RC, VB)
            tasks: List of (pattern, task_num) to run
            shuffle: Whether to shuffle task order

        Returns:
            List of TaskResults
        """
        executor = ConditionExecutor(condition)
        results = []

        if shuffle:
            tasks = tasks.copy()
            random.shuffle(tasks)

        for pattern, task_num in tasks:
            print(f"[{condition}] Running {pattern}/t{task_num:02d}...")

            task = self.task_loader.load_task(pattern, task_num)
            result = executor.execute_task(task)
            results.append(result)

            # Save result immediately
            self._save_result(condition, result)

            print(f"  → {'PASS' if result.passed else 'FAIL'} "
                  f"({result.pass_fraction:.1%} tests passed)")

        return results

    def _save_result(self, condition: str, result: TaskResult):
        """Save individual result to JSON."""
        condition_dir = self.results_dir / condition
        condition_dir.mkdir(exist_ok=True)

        result_file = condition_dir / f"{result.task_id}.json"
        result_file.write_text(json.dumps(asdict(result), indent=2))

    def run_full_study(self):
        """Run complete ablation study across all conditions."""
        print("=" * 80)
        print("ABLATION STUDY: CC-ABLATION-001")
        print("=" * 80)

        tasks = self.task_loader.list_all_tasks()
        print(f"Loaded {len(tasks)} tasks")

        conditions = ["VB", "NM", "RC", "FS"]  # Run in order of increasing complexity

        all_results = {}

        for condition in conditions:
            print(f"\n{'=' * 80}")
            print(f"CONDITION: {condition}")
            print(f"{'=' * 80}\n")

            results = self.run_condition(condition, tasks, shuffle=True)
            all_results[condition] = results

        # Generate summary
        self._generate_summary(all_results)

        print(f"\n{'=' * 80}")
        print("STUDY COMPLETE")
        print(f"{'=' * 80}\n")
        print(f"Results saved to: {self.results_dir}")

    def _generate_summary(self, all_results: dict[str, list[TaskResult]]):
        """Generate summary statistics and save to JSON."""
        summary = {
            "study_id": "CC-ABLATION-001",
            "timestamp": datetime.utcnow().isoformat(),
            "conditions": {}
        }

        for condition, results in all_results.items():
            pass_rate = sum(r.passed for r in results) / len(results)
            avg_attempts = sum(r.attempts for r in results) / len(results)
            avg_corrections = sum(r.self_corrections for r in results) / len(results)
            total_tokens = sum(r.tokens_generated for r in results)

            summary["conditions"][condition] = {
                "total_tasks": len(results),
                "passed": sum(r.passed for r in results),
                "pass_rate": pass_rate,
                "avg_attempts": avg_attempts,
                "avg_self_corrections": avg_corrections,
                "total_tokens": total_tokens
            }

        summary_file = self.results_dir / "summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        print("\nSUMMARY:")
        print("-" * 80)
        for condition, stats in summary["conditions"].items():
            print(f"{condition}: {stats['pass_rate']:.1%} pass rate "
                  f"({stats['passed']}/{stats['total_tasks']} tasks)")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent
    tasks_dir = base_dir / "tasks"
    results_dir = base_dir / "results"

    harness = AblationHarness(tasks_dir, results_dir)
    harness.run_full_study()


if __name__ == "__main__":
    main()
