#!/usr/bin/env python3
"""
ACE Practice Generator - The Autonomous Curriculum Layer

Analyzes coding weaknesses from session history and autonomously
proposes targeted practice tasks to improve specific weak areas.

This is where ACE becomes a self-directed learning curriculum.

Author: Claude Code (Autonomous Learning Module)
Date: 2025-11-07
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import sys

# Add core for CIL
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from causal_influence_ledger import get_cil


class WeaknessAnalyzer:
    """Analyzes coding session history to identify weak patterns"""

    def __init__(self):
        self.session_ledger = Path("diagnostics/coding_sessions.jsonl")

    def analyze_pattern_weaknesses(self, threshold: float = 0.70) -> Dict[str, Dict[str, float]]:
        """
        Find patterns with success rate < threshold.

        Returns: {pattern: {current_rate, avg_quality, sessions}}
        """
        if not self.session_ledger.exists():
            return {}

        pattern_stats = {}

        with open(self.session_ledger) as f:
            for line in f:
                if not line.strip():
                    continue
                session = json.loads(line)

                quality = session.get('quality', 0)
                patterns = session.get('patterns', {})

                for pattern, count in patterns.items():
                    if count > 0:
                        if pattern not in pattern_stats:
                            pattern_stats[pattern] = {
                                'total_quality': 0,
                                'sessions': 0,
                                'high_quality_count': 0
                            }

                        pattern_stats[pattern]['total_quality'] += quality
                        pattern_stats[pattern]['sessions'] += 1
                        if quality >= 0.7:
                            pattern_stats[pattern]['high_quality_count'] += 1

        # Find weak patterns
        weak_patterns = {}
        for pattern, stats in pattern_stats.items():
            if stats['sessions'] >= 3:  # Need at least 3 sessions to be meaningful
                success_rate = stats['high_quality_count'] / stats['sessions']
                if success_rate < threshold:
                    weak_patterns[pattern] = {
                        'current_rate': success_rate,
                        'avg_quality': stats['total_quality'] / stats['sessions'],
                        'sessions': stats['sessions']
                    }

        return weak_patterns

    def analyze_failure_patterns(self) -> Dict[str, int]:
        """
        Analyze common failure types from improvement sessions.

        Returns: {failure_type: count}
        """
        improvement_ledger = Path("diagnostics/improvement_sessions.jsonl")

        if not improvement_ledger.exists():
            return {}

        failure_counts = {}

        with open(improvement_ledger) as f:
            for line in f:
                if not line.strip():
                    continue
                session = json.loads(line)

                refactoring = session.get('refactoring', '')
                # Infer failure type from refactoring
                # (In real usage, we'd track this explicitly)
                if 'type' in refactoring:
                    failure_type = 'type_errors'
                elif 'null' in refactoring or 'attribute' in refactoring:
                    failure_type = 'null_reference_errors'
                elif 'bounds' in refactoring or 'index' in refactoring:
                    failure_type = 'index_errors'
                else:
                    failure_type = 'other_errors'

                failure_counts[failure_type] = failure_counts.get(failure_type, 0) + 1

        return failure_counts


class PracticeTaskGenerator:
    """Generates targeted practice tasks for weak areas"""

    PRACTICE_TEMPLATES = {
        'async_await': {
            'objective': 'Master async/await patterns',
            'exercises': [
                'Implement async function that fetches data from 3 URLs concurrently',
                'Create async context manager for resource management',
                'Write async generator function',
                'Handle async exceptions properly',
                'Implement async retry logic with exponential backoff'
            ],
            'success_metric': 'All exercises pass tests with >80% quality'
        },
        'list_comprehension': {
            'objective': 'Improve list comprehension proficiency',
            'exercises': [
                'Filter and transform list with single comprehension',
                'Nested comprehension for 2D data structure',
                'Comprehension with multiple conditions',
                'Dictionary comprehension from two lists',
                'Set comprehension with filtering'
            ],
            'success_metric': 'Readable comprehensions with <5 complexity'
        },
        'type_hints': {
            'objective': 'Add comprehensive type annotations',
            'exercises': [
                'Annotate function with generic types (List[T], Dict[K,V])',
                'Use Optional and Union types correctly',
                'Create TypedDict for structured data',
                'Annotate async functions properly',
                'Use Protocol for duck typing'
            ],
            'success_metric': 'mypy validation passes with no errors'
        },
        'try_except': {
            'objective': 'Master exception handling patterns',
            'exercises': [
                'Handle multiple exception types appropriately',
                'Use finally for cleanup',
                'Create custom exception classes',
                'Implement retry logic with exception handling',
                'Use context managers to avoid try-finally'
            ],
            'success_metric': 'No unhandled exceptions in edge cases'
        },
        'context_manager': {
            'objective': 'Build robust resource management',
            'exercises': [
                'Create context manager with __enter__ and __exit__',
                'Use contextlib.contextmanager decorator',
                'Handle exceptions in context managers',
                'Nest multiple context managers',
                'Create reusable context managers for common patterns'
            ],
            'success_metric': 'Resources always cleaned up properly'
        }
    }

    def generate_practice_task(
        self,
        pattern: str,
        current_rate: float,
        target_rate: float = 0.80
    ) -> Dict[str, Any]:
        """Generate practice task for weak pattern"""

        template = self.PRACTICE_TEMPLATES.get(pattern)

        if not template:
            # Generic practice task
            template = {
                'objective': f'Improve {pattern} proficiency',
                'exercises': [
                    f'Write 5 functions using {pattern}',
                    f'Refactor existing code to use {pattern}',
                    f'Handle edge cases with {pattern}',
                    f'Optimize code using {pattern}',
                    f'Document {pattern} usage'
                ],
                'success_metric': f'{pattern} success rate >80%'
            }

        task = {
            'task_id': f'ace_practice_{pattern}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'pattern': pattern,
            'objective': template['objective'],
            'current_rate': current_rate,
            'target_rate': target_rate,
            'gap': target_rate - current_rate,
            'exercises': template['exercises'],
            'success_metric': template['success_metric'],
            'estimated_time_minutes': len(template['exercises']) * 15
        }

        return task


class ACEPracticeGenerator:
    """
    ACE-driven autonomous practice curriculum.

    Analyzes coding session history, identifies weaknesses,
    proposes targeted practice tasks, and scores them by priority.
    """

    def __init__(self):
        self.weakness_analyzer = WeaknessAnalyzer()
        self.task_generator = PracticeTaskGenerator()
        self.cil = get_cil()
        self.practice_ledger = Path("diagnostics/practice_tasks.jsonl")
        self.practice_ledger.parent.mkdir(parents=True, exist_ok=True)

    def analyze_and_propose(self, max_tasks: int = 3) -> List[Dict[str, Any]]:
        """
        Analyze weaknesses and propose top N practice tasks.

        Returns: List of practice tasks sorted by priority
        """
        print(f"\n{'='*70}")
        print("ACE PRACTICE GENERATOR - ANALYZING WEAKNESSES")
        print(f"{'='*70}")

        # Analyze pattern weaknesses
        weak_patterns = self.weakness_analyzer.analyze_pattern_weaknesses()

        if not weak_patterns:
            print("\nNo weaknesses detected yet (need ≥3 sessions per pattern)")
            return []

        print(f"\nWeak patterns found: {len(weak_patterns)}")
        for pattern, stats in sorted(weak_patterns.items(), key=lambda x: x[1]['current_rate']):
            print(f"  {pattern}: {stats['current_rate']:.1%} success rate (avg quality: {stats['avg_quality']:.2f})")

        # Generate practice tasks
        tasks = []
        for pattern, stats in weak_patterns.items():
            task = self.task_generator.generate_practice_task(
                pattern=pattern,
                current_rate=stats['current_rate']
            )
            tasks.append(task)

        # Score and rank tasks
        scored_tasks = self._score_tasks(tasks)

        # Take top N
        top_tasks = scored_tasks[:max_tasks]

        print(f"\n{'='*70}")
        print(f"TOP {len(top_tasks)} PRACTICE TASKS")
        print(f"{'='*70}")

        for i, task in enumerate(top_tasks, 1):
            print(f"\n{i}. {task['objective']}")
            print(f"   Pattern: {task['pattern']}")
            print(f"   Current rate: {task['current_rate']:.1%}")
            print(f"   Target rate: {task['target_rate']:.1%}")
            print(f"   Gap: {task['gap']:.1%}")
            print(f"   Priority score: {task['priority_score']:.3f}")
            print(f"   Exercises: {len(task['exercises'])}")

        # Log to CIL
        self.cil.log_decision(
            decision_type='practice_task_proposal',
            inputs=[
                {
                    'artifact_id': f'weakness_{task["pattern"]}',
                    'weight': task['gap'],
                    'reason': 'skill_gap'
                }
                for task in top_tasks
            ],
            output=len(top_tasks),
            metadata={'proposed_tasks': [t['task_id'] for t in top_tasks]}
        )

        # Log to practice ledger
        for task in top_tasks:
            with open(self.practice_ledger, 'a') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'event_type': 'task_proposed',
                    **task
                }) + '\n')

        return top_tasks

    def record_practice_outcome(
        self,
        task_id: str,
        exercises_completed: int,
        final_success_rate: float,
        time_spent_minutes: int
    ):
        """Record outcome of practice session"""

        print(f"\n{'='*70}")
        print(f"PRACTICE OUTCOME: {task_id}")
        print(f"{'='*70}")
        print(f"Exercises completed: {exercises_completed}")
        print(f"Final success rate: {final_success_rate:.1%}")
        print(f"Time spent: {time_spent_minutes} minutes")

        # Log to CIL
        self.cil.log_decision(
            decision_type='practice_outcome',
            inputs=[
                {'artifact_id': task_id, 'weight': 1.0, 'reason': 'practice_session'}
            ],
            output=final_success_rate,
            metadata={
                'exercises_completed': exercises_completed,
                'time_spent_minutes': time_spent_minutes
            }
        )

        # Log to practice ledger
        with open(self.practice_ledger, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'event_type': 'task_completed',
                'task_id': task_id,
                'exercises_completed': exercises_completed,
                'final_success_rate': final_success_rate,
                'time_spent_minutes': time_spent_minutes
            }) + '\n')

    def _score_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score and rank tasks by priority.

        Scoring factors:
        - Gap size (bigger gap = higher priority)
        - Pattern frequency (more common = higher priority)
        - Estimated time (shorter = higher priority)
        """
        for task in tasks:
            # Base score from gap
            gap_score = task['gap']

            # Time penalty (prefer shorter tasks)
            time_score = 1.0 - (min(task['estimated_time_minutes'], 120) / 120)

            # Combined priority
            priority = gap_score * 0.7 + time_score * 0.3

            task['priority_score'] = priority

        # Sort by priority (descending)
        tasks.sort(key=lambda x: x['priority_score'], reverse=True)

        return tasks


if __name__ == "__main__":
    # Example usage
    generator = ACEPracticeGenerator()

    # Analyze and propose tasks
    tasks = generator.analyze_and_propose(max_tasks=3)

    if tasks:
        print(f"\n{'='*70}")
        print("EXAMPLE PRACTICE TASK DETAIL")
        print(f"{'='*70}")

        task = tasks[0]
        print(f"\nTask ID: {task['task_id']}")
        print(f"Objective: {task['objective']}")
        print(f"\nExercises:")
        for i, exercise in enumerate(task['exercises'], 1):
            print(f"  {i}. {exercise}")
        print(f"\nSuccess Metric: {task['success_metric']}")
        print(f"Estimated Time: {task['estimated_time_minutes']} minutes")

        # Simulate completion
        generator.record_practice_outcome(
            task_id=task['task_id'],
            exercises_completed=len(task['exercises']),
            final_success_rate=0.85,
            time_spent_minutes=task['estimated_time_minutes']
        )
