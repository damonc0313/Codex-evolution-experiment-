#!/usr/bin/env python3
"""
Production-Grade Batch Runner - Autonomous Learning Loop

Processes entire codebase through learning modules to:
1. Establish baseline coding signature
2. Identify pattern weaknesses
3. Generate ACE practice curriculum
4. Create prioritized improvement plan

This is production execution - measuring real code at scale.

Author: Claude Code (Production System)
Date: 2025-11-07
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import traceback

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from code_quality_tracker import CodeQualityTracker
from iterative_improvement_engine import IterativeImprovementEngine
from ace_practice_generator import ACEPracticeGenerator


class ProductionBatchRunner:
    """Production-grade batch processor for autonomous learning"""

    def __init__(self, root_dir: Path = None):
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.tracker = CodeQualityTracker()
        self.improvement_engine = IterativeImprovementEngine()
        self.practice_generator = ACEPracticeGenerator()

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'codebase_root': str(self.root_dir),
            'files_processed': [],
            'files_failed': [],
            'aggregate_stats': {},
            'practice_curriculum': [],
            'improvement_plan': {}
        }

    def find_python_files(self) -> List[Path]:
        """Find all Python files in repository (excluding venv, .git, etc.)"""

        exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'venv', 'env',
            '.venv', 'node_modules', '.mypy_cache', '.tox', 'build', 'dist'
        }

        python_files = []

        for path in self.root_dir.rglob('*.py'):
            # Skip excluded directories
            if any(exclude_dir in path.parts for exclude_dir in exclude_dirs):
                continue

            # Skip empty files
            if path.stat().st_size == 0:
                continue

            python_files.append(path)

        return sorted(python_files)

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process single file through quality tracker"""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Track without test execution (would require test discovery)
            result = self.tracker.track_code_session(
                code=code,
                file_path=str(file_path.relative_to(self.root_dir)),
                session_id=f"batch_{file_path.stem}"
            )

            return {
                'status': 'success',
                'file': str(file_path.relative_to(self.root_dir)),
                **result
            }

        except Exception as e:
            return {
                'status': 'failed',
                'file': str(file_path.relative_to(self.root_dir)),
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def run_batch_analysis(self, max_files: int = None, verbose: bool = True):
        """
        Run batch analysis on entire codebase.

        Args:
            max_files: Limit number of files (None = all)
            verbose: Print progress
        """

        if verbose:
            print("=" * 70)
            print("PRODUCTION BATCH RUNNER - AUTONOMOUS LEARNING LOOP")
            print("=" * 70)
            print(f"\nCodebase: {self.root_dir}")
            print(f"Timestamp: {self.results['timestamp']}")

        # Find Python files
        python_files = self.find_python_files()

        if max_files:
            python_files = python_files[:max_files]

        total_files = len(python_files)

        if verbose:
            print(f"\nPython files found: {total_files}")
            print("\nProcessing files...")

        # Process each file
        for i, file_path in enumerate(python_files, 1):
            if verbose:
                print(f"  [{i}/{total_files}] {file_path.relative_to(self.root_dir)}")

            result = self.process_file(file_path)

            if result['status'] == 'success':
                self.results['files_processed'].append(result)
            else:
                self.results['files_failed'].append(result)
                if verbose:
                    print(f"    ✗ Failed: {result['error']}")

        # Compute aggregate statistics
        if verbose:
            print(f"\n{'='*70}")
            print("COMPUTING AGGREGATE STATISTICS")
            print(f"{'='*70}")

        self._compute_aggregate_stats(verbose)

        # Generate practice curriculum
        if verbose:
            print(f"\n{'='*70}")
            print("GENERATING ACE PRACTICE CURRICULUM")
            print(f"{'='*70}")

        self._generate_practice_curriculum(verbose)

        # Create improvement plan
        if verbose:
            print(f"\n{'='*70}")
            print("CREATING IMPROVEMENT PLAN")
            print(f"{'='*70}")

        self._create_improvement_plan(verbose)

        # Save results
        output_path = Path("runs/production_batch_analysis.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        if verbose:
            print(f"\n{'='*70}")
            print("BATCH ANALYSIS COMPLETE")
            print(f"{'='*70}")
            print(f"\nResults saved: {output_path}")
            print(f"Files processed: {len(self.results['files_processed'])}")
            print(f"Files failed: {len(self.results['files_failed'])}")

    def _compute_aggregate_stats(self, verbose: bool = True):
        """Compute statistics across all processed files"""

        # Aggregate patterns
        pattern_totals = {}
        pattern_qualities = {}
        total_loc = 0
        total_functions = 0
        total_classes = 0
        quality_scores = []

        for result in self.results['files_processed']:
            # Patterns
            for pattern, count in result.get('patterns', {}).items():
                if count > 0:
                    pattern_totals[pattern] = pattern_totals.get(pattern, 0) + count
                    if pattern not in pattern_qualities:
                        pattern_qualities[pattern] = []
                    pattern_qualities[pattern].append(result['quality'])

            # Complexity
            complexity = result.get('complexity', {})
            total_loc += complexity.get('lines_of_code', 0)
            total_functions += complexity.get('num_functions', 0)
            total_classes += complexity.get('num_classes', 0)

            # Quality
            quality_scores.append(result['quality'])

        # Analyze patterns from tracker
        pattern_success = self.tracker.analyze_pattern_success_rates()

        self.results['aggregate_stats'] = {
            'files_analyzed': len(self.results['files_processed']),
            'total_loc': total_loc,
            'total_functions': total_functions,
            'total_classes': total_classes,
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'pattern_totals': pattern_totals,
            'pattern_success_rates': pattern_success
        }

        if verbose:
            print(f"\nCodebase Statistics:")
            print(f"  Files analyzed: {self.results['aggregate_stats']['files_analyzed']}")
            print(f"  Total LOC: {total_loc:,}")
            print(f"  Total functions: {total_functions}")
            print(f"  Total classes: {total_classes}")
            print(f"  Avg quality: {self.results['aggregate_stats']['avg_quality']:.3f}")

            print(f"\nTop 10 Patterns by Usage:")
            sorted_patterns = sorted(pattern_totals.items(), key=lambda x: x[1], reverse=True)[:10]
            for pattern, count in sorted_patterns:
                success_rate = pattern_success.get(pattern, {}).get('success_rate', 0)
                print(f"  {pattern}: {count} occurrences (success rate: {success_rate:.1%})")

    def _generate_practice_curriculum(self, verbose: bool = True):
        """Generate ACE practice curriculum from analysis"""

        # Get practice tasks from generator
        tasks = self.practice_generator.analyze_and_propose(max_tasks=5)

        self.results['practice_curriculum'] = tasks

        if verbose and tasks:
            print(f"\nACE has proposed {len(tasks)} practice tasks:")
            for i, task in enumerate(tasks, 1):
                print(f"\n{i}. {task['objective']}")
                print(f"   Pattern: {task['pattern']}")
                print(f"   Current success: {task['current_rate']:.1%}")
                print(f"   Target: {task['target_rate']:.1%}")
                print(f"   Gap: {task['gap']:.1%}")
                print(f"   Exercises: {len(task['exercises'])}")
        elif verbose:
            print("\nNo practice tasks needed - all patterns >70% success rate")

    def _create_improvement_plan(self, verbose: bool = True):
        """Create prioritized improvement plan"""

        pattern_success = self.results['aggregate_stats'].get('pattern_success_rates', {})

        # Categorize patterns
        strong_patterns = {}  # >80% success
        moderate_patterns = {}  # 60-80% success
        weak_patterns = {}  # <60% success

        for pattern, stats in pattern_success.items():
            rate = stats['success_rate']
            if rate >= 0.80:
                strong_patterns[pattern] = stats
            elif rate >= 0.60:
                moderate_patterns[pattern] = stats
            else:
                weak_patterns[pattern] = stats

        # Create plan
        self.results['improvement_plan'] = {
            'baseline_signature': {
                'strong_patterns': list(strong_patterns.keys()),
                'moderate_patterns': list(moderate_patterns.keys()),
                'weak_patterns': list(weak_patterns.keys()),
                'dominant_pattern': max(self.results['aggregate_stats']['pattern_totals'].items(), key=lambda x: x[1])[0] if self.results['aggregate_stats']['pattern_totals'] else None
            },
            'immediate_focus': [
                {
                    'pattern': pattern,
                    'current_rate': stats['success_rate'],
                    'recommended_action': 'Complete ACE practice tasks'
                }
                for pattern, stats in sorted(weak_patterns.items(), key=lambda x: x[1]['success_rate'])[:3]
            ],
            'leverage_strengths': [
                {
                    'pattern': pattern,
                    'current_rate': stats['success_rate'],
                    'recommended_action': 'Use more frequently as reliable tool'
                }
                for pattern, stats in sorted(strong_patterns.items(), key=lambda x: x[1]['success_rate'], reverse=True)[:3]
            ]
        }

        if verbose:
            print(f"\nBaseline Coding Signature:")
            print(f"  Strong patterns (>80%): {len(strong_patterns)}")
            for pattern in list(strong_patterns.keys())[:5]:
                print(f"    - {pattern}: {strong_patterns[pattern]['success_rate']:.1%}")

            print(f"\n  Weak patterns (<60%): {len(weak_patterns)}")
            for pattern in list(weak_patterns.keys())[:5]:
                print(f"    - {pattern}: {weak_patterns[pattern]['success_rate']:.1%}")

            if self.results['improvement_plan']['immediate_focus']:
                print(f"\nImmediate Focus (Top 3 Weaknesses):")
                for item in self.results['improvement_plan']['immediate_focus']:
                    print(f"  • {item['pattern']}: {item['current_rate']:.1%} → complete ACE tasks")


def main():
    """Run production batch analysis"""

    import argparse

    parser = argparse.ArgumentParser(description='Production batch runner for autonomous learning')
    parser.add_argument('--max-files', type=int, help='Limit number of files to process')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress output')

    args = parser.parse_args()

    runner = ProductionBatchRunner()
    runner.run_batch_analysis(
        max_files=args.max_files,
        verbose=not args.quiet
    )

    print("\n" + "=" * 70)
    print("PRODUCTION BATCH COMPLETE")
    print("=" * 70)
    print("\nThe autonomous learning loop has established baseline state.")
    print("ACE practice curriculum generated and ready for execution.")
    print("\nNext steps:")
    print("  1. Review: runs/production_batch_analysis.json")
    print("  2. Execute: ACE practice tasks for weak patterns")
    print("  3. Measure: Improvement after practice completion")
    print("  4. Iterate: System learns from outcomes")


if __name__ == "__main__":
    main()
