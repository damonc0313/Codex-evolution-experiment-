#!/usr/bin/env python3
"""
Code Quality Tracker - The Measurement Layer

Tracks every coding session with real outcomes. No simulation.
Measures which patterns actually work through test execution.

This is the sensory layer for code-pattern learning.

Author: Claude Code (Autonomous Learning Module)
Date: 2025-11-07
"""

import json
import re
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import sys

# Add core for CIL
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from causal_influence_ledger import get_cil


class CodePatternDetector:
    """Detects coding patterns in Python source code"""

    PATTERNS = {
        'async_await': r'async\s+def|await\s+',
        'list_comprehension': r'\[.+\s+for\s+.+\s+in\s+.+\]',
        'generator_expression': r'\(.+\s+for\s+.+\s+in\s+.+\)',
        'lambda_function': r'lambda\s+',
        'decorator': r'@\w+',
        'context_manager': r'with\s+.+\s+as\s+',
        'try_except': r'try:|except\s+',
        'class_definition': r'class\s+\w+',
        'function_definition': r'def\s+\w+',
        'type_hints': r'->\s*\w+|:\s*\w+\[',
        'docstring': r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
        'f_string': r'f["\']',
        'match_statement': r'match\s+.+:|case\s+',
        'walrus_operator': r':=',
    }

    def detect_patterns(self, code: str) -> Dict[str, int]:
        """Count occurrences of each pattern"""
        counts = {}
        for pattern_name, pattern_regex in self.PATTERNS.items():
            matches = re.findall(pattern_regex, code, re.MULTILINE)
            counts[pattern_name] = len(matches)
        return counts

    def detect_complexity(self, code: str) -> Dict[str, float]:
        """Estimate code complexity metrics"""
        try:
            tree = ast.parse(code)

            # Count nodes
            num_functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            num_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            num_imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
            num_branches = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While)))

            lines = code.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

            return {
                'lines_of_code': loc,
                'num_functions': num_functions,
                'num_classes': num_classes,
                'num_imports': num_imports,
                'cyclomatic_complexity': num_branches + 1,  # Simplified
                'avg_function_length': loc / max(num_functions, 1)
            }
        except:
            return {'error': 'parse_failed'}


class CodeQualityTracker:
    """
    Tracks coding sessions with real outcomes.

    For each piece of code written:
    1. Detect patterns used
    2. Run tests (if available)
    3. Measure quality
    4. Compute reward
    5. Log to CIL with pattern attribution
    6. Store in coding session ledger
    """

    def __init__(self):
        self.detector = CodePatternDetector()
        self.cil = get_cil()
        self.session_ledger = Path("diagnostics/coding_sessions.jsonl")
        self.session_ledger.parent.mkdir(parents=True, exist_ok=True)

    def track_code_session(
        self,
        code: str,
        file_path: str,
        test_command: str = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Track a coding session with real outcomes.

        Args:
            code: The code written
            file_path: Path to the code file
            test_command: Optional test command to run
            session_id: Optional session identifier

        Returns:
            Session data with outcomes and patterns
        """
        session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*70}")
        print(f"CODE QUALITY TRACKING: {session_id}")
        print(f"{'='*70}")

        # 1. Detect patterns
        patterns = self.detector.detect_patterns(code)
        complexity = self.detector.detect_complexity(code)

        print(f"\nPatterns detected:")
        for pattern, count in patterns.items():
            if count > 0:
                print(f"  {pattern}: {count}")

        print(f"\nComplexity:")
        for metric, value in complexity.items():
            if metric != 'error':
                print(f"  {metric}: {value}")

        # 2. Run tests if provided
        test_outcome = None
        if test_command:
            test_outcome = self._run_tests(test_command)
            print(f"\nTest outcome:")
            print(f"  Command: {test_command}")
            print(f"  Success: {test_outcome['success']}")
            if not test_outcome['success']:
                print(f"  Error: {test_outcome.get('error', 'unknown')[:200]}")

        # 3. Compute quality score
        quality = self._compute_quality(patterns, complexity, test_outcome)

        print(f"\nQuality score: {quality:.3f}")

        # 4. Compute reward (quality + complexity penalty)
        reward = quality
        if complexity.get('cyclomatic_complexity', 0) > 10:
            reward *= 0.8  # Penalty for high complexity

        print(f"Reward: {reward:.3f}")

        # 5. Log to CIL with pattern attribution
        inputs = []
        for pattern, count in patterns.items():
            if count > 0:
                inputs.append({
                    'artifact_id': f'pattern_{pattern}',
                    'weight': float(count),
                    'reason': 'pattern_usage'
                })

        if inputs:
            self.cil.log_decision(
                decision_type='code_pattern_selection',
                inputs=inputs,
                output=reward,
                metadata={
                    'session_id': session_id,
                    'file_path': file_path,
                    'quality': quality,
                    'test_success': test_outcome['success'] if test_outcome else None
                }
            )

        # 6. Store in session ledger
        session_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'patterns': patterns,
            'complexity': complexity,
            'test_outcome': test_outcome,
            'quality': quality,
            'reward': reward
        }

        with open(self.session_ledger, 'a') as f:
            f.write(json.dumps(session_data) + '\n')

        print(f"\nSession logged to: {self.session_ledger}")

        return session_data

    def _run_tests(self, test_command: str) -> Dict[str, Any]:
        """Run test command and capture outcome"""
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _compute_quality(
        self,
        patterns: Dict[str, int],
        complexity: Dict[str, float],
        test_outcome: Dict[str, Any] = None
    ) -> float:
        """
        Compute quality score from patterns, complexity, and test outcome.

        Quality formula:
        - Base: 0.5
        - Tests pass: +0.3
        - Has type hints: +0.1
        - Has docstrings: +0.1
        - Low complexity: +0.1
        - Minus: complexity penalty
        """
        quality = 0.5

        # Test outcome (most important)
        if test_outcome and test_outcome.get('success'):
            quality += 0.3

        # Type hints
        if patterns.get('type_hints', 0) > 0:
            quality += 0.1

        # Docstrings
        if patterns.get('docstring', 0) > 0:
            quality += 0.1

        # Complexity penalty
        complexity_score = complexity.get('cyclomatic_complexity', 0)
        if complexity_score <= 5:
            quality += 0.1
        elif complexity_score > 15:
            quality -= 0.1

        return max(0.0, min(1.0, quality))

    def analyze_pattern_success_rates(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze success rates by pattern from session history.

        Returns dict of {pattern: {success_rate, avg_quality, count}}
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

        # Compute rates
        results = {}
        for pattern, stats in pattern_stats.items():
            results[pattern] = {
                'avg_quality': stats['total_quality'] / stats['sessions'],
                'success_rate': stats['high_quality_count'] / stats['sessions'],
                'sessions': stats['sessions']
            }

        return results


if __name__ == "__main__":
    # Example usage
    tracker = CodeQualityTracker()

    # Example code to track
    example_code = '''
async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data from URL asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

def process_items(items: List[str]) -> List[str]:
    """Process items using list comprehension"""
    return [item.upper() for item in items if len(item) > 3]
'''

    tracker.track_code_session(
        code=example_code,
        file_path="examples/example.py",
        session_id="demo_session"
    )

    print("\n" + "="*70)
    print("PATTERN SUCCESS RATES")
    print("="*70)

    rates = tracker.analyze_pattern_success_rates()
    for pattern, stats in sorted(rates.items(), key=lambda x: x[1]['success_rate'], reverse=True):
        print(f"\n{pattern}:")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg quality: {stats['avg_quality']:.3f}")
        print(f"  Sessions: {stats['sessions']}")
