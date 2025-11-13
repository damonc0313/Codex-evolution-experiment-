#!/usr/bin/env python3
"""
Iterative Improvement Engine - The Learning Layer

Takes failing code and iteratively improves it through measured feedback.
Learns which refactoring patterns work for which failure modes.

This is where code learns from its mistakes.

Author: Claude Code (Autonomous Learning Module)
Date: 2025-11-07
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import sys

# Add core for CIL
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from causal_influence_ledger import get_cil


class FailureAnalyzer:
    """Analyzes test failures and code issues"""

    FAILURE_PATTERNS = {
        'type_error': r'TypeError|type.*mismatch',
        'attribute_error': r'AttributeError|has no attribute',
        'index_error': r'IndexError|list index',
        'key_error': r'KeyError|key.*not found',
        'value_error': r'ValueError|invalid value',
        'import_error': r'ImportError|ModuleNotFoundError',
        'syntax_error': r'SyntaxError|invalid syntax',
        'indentation_error': r'IndentationError',
        'assertion_error': r'AssertionError|assertion failed',
        'timeout': r'timeout|TimeoutExpired'
    }

    def classify_failure(self, error_message: str) -> List[str]:
        """Classify failure types from error message"""
        failures = []
        for failure_type, pattern in self.FAILURE_PATTERNS.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                failures.append(failure_type)
        return failures if failures else ['unknown_error']


class RefactoringPatternSelector:
    """
    Selects refactoring patterns based on failure types and learned policy.

    This is where the learning happens - we track which refactorings
    work for which failure types and update weights accordingly.
    """

    # Maps failure types to potential refactoring patterns
    REFACTORING_MAP = {
        'type_error': ['add_type_hints', 'add_type_checking', 'use_isinstance'],
        'attribute_error': ['add_null_checks', 'use_getattr', 'add_hasattr'],
        'index_error': ['add_bounds_checking', 'use_enumerate', 'use_get_method'],
        'key_error': ['use_get_method', 'add_default_dict', 'add_key_validation'],
        'value_error': ['add_input_validation', 'use_try_except', 'add_constraints'],
        'import_error': ['check_dependencies', 'add_try_import', 'fix_import_path'],
        'syntax_error': ['fix_syntax', 'check_parentheses', 'check_indentation'],
        'assertion_error': ['fix_logic', 'update_test', 'add_edge_case_handling'],
        'timeout': ['optimize_algorithm', 'add_caching', 'parallelize'],
        'unknown_error': ['add_logging', 'add_try_except', 'simplify_logic']
    }

    def __init__(self):
        self.policy_path = Path("runtime/refactoring_policy.json")
        self.policy = self._load_policy()

    def _load_policy(self) -> Dict[str, float]:
        """Load learned refactoring weights"""
        if self.policy_path.exists():
            with open(self.policy_path) as f:
                return json.load(f)
        else:
            # Initialize with uniform weights
            all_refactorings = set()
            for patterns in self.REFACTORING_MAP.values():
                all_refactorings.update(patterns)
            return {pattern: 0.5 for pattern in all_refactorings}

    def _save_policy(self):
        """Save updated policy"""
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.policy_path, 'w') as f:
            json.dump(self.policy, f, indent=2)

    def select_refactoring(self, failure_types: List[str]) -> str:
        """
        Select best refactoring pattern based on failure types and policy.

        Uses weighted selection based on learned success rates.
        """
        # Collect candidate refactorings
        candidates = []
        for failure_type in failure_types:
            patterns = self.REFACTORING_MAP.get(failure_type, [])
            candidates.extend(patterns)

        if not candidates:
            return 'add_logging'

        # Score by policy weights
        scores = [(pattern, self.policy.get(pattern, 0.5)) for pattern in candidates]
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[0][0]

    def update_policy(self, refactoring: str, success: bool, learning_rate: float = 0.1):
        """Update policy weights based on refactoring outcome"""
        current_weight = self.policy.get(refactoring, 0.5)

        if success:
            # Increase weight if successful
            new_weight = current_weight + learning_rate * (1.0 - current_weight)
        else:
            # Decrease weight if failed
            new_weight = current_weight - learning_rate * current_weight

        self.policy[refactoring] = max(0.1, min(0.9, new_weight))
        self._save_policy()


class IterativeImprovementEngine:
    """
    Iteratively improves code through measured feedback.

    Process:
    1. Run tests on current code
    2. If failures, analyze failure types
    3. Select refactoring based on policy
    4. Apply refactoring (conceptual - guidance for human/AI)
    5. Measure improvement
    6. Update policy based on outcome
    7. Log to CIL for causal attribution
    """

    def __init__(self):
        self.failure_analyzer = FailureAnalyzer()
        self.refactoring_selector = RefactoringPatternSelector()
        self.cil = get_cil()
        self.improvement_ledger = Path("diagnostics/improvement_sessions.jsonl")
        self.improvement_ledger.parent.mkdir(parents=True, exist_ok=True)

    def analyze_and_suggest(
        self,
        code: str,
        test_output: str,
        iteration: int = 0,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze failing code and suggest refactoring.

        Returns:
            Suggestion dict with refactoring pattern and reasoning
        """
        print(f"\n{'='*70}")
        print(f"ITERATIVE IMPROVEMENT - Iteration {iteration + 1}/{max_iterations}")
        print(f"{'='*70}")

        # Classify failures
        failure_types = self.failure_analyzer.classify_failure(test_output)

        print(f"\nFailure types detected: {', '.join(failure_types)}")

        # Select refactoring
        refactoring = self.refactoring_selector.select_refactoring(failure_types)

        print(f"Suggested refactoring: {refactoring}")
        print(f"Policy weight: {self.refactoring_selector.policy.get(refactoring, 0.5):.3f}")

        # Log to CIL
        self.cil.log_decision(
            decision_type='refactoring_selection',
            inputs=[
                {'artifact_id': f'failure_{ft}', 'weight': 1.0, 'reason': 'failure_type'}
                for ft in failure_types
            ],
            output=1.0,  # Will update after measuring outcome
            metadata={
                'iteration': iteration,
                'refactoring': refactoring,
                'failure_types': failure_types
            }
        )

        suggestion = {
            'iteration': iteration,
            'failure_types': failure_types,
            'refactoring': refactoring,
            'policy_weight': self.refactoring_selector.policy.get(refactoring, 0.5),
            'reasoning': self._get_refactoring_description(refactoring)
        }

        return suggestion

    def record_outcome(
        self,
        refactoring: str,
        success: bool,
        improvement_pct: float,
        session_id: str = None
    ):
        """
        Record outcome of refactoring attempt.

        Updates policy based on success/failure.
        Logs to improvement ledger.
        """
        session_id = session_id or f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*70}")
        print(f"RECORDING OUTCOME: {session_id}")
        print(f"{'='*70}")
        print(f"Refactoring: {refactoring}")
        print(f"Success: {success}")
        print(f"Improvement: {improvement_pct:.1f}%")

        # Update policy
        old_weight = self.refactoring_selector.policy.get(refactoring, 0.5)
        self.refactoring_selector.update_policy(refactoring, success)
        new_weight = self.refactoring_selector.policy.get(refactoring, 0.5)

        print(f"Policy update: {old_weight:.3f} → {new_weight:.3f}")

        # Log to CIL
        self.cil.log_decision(
            decision_type='refactoring_outcome',
            inputs=[
                {'artifact_id': f'refactoring_{refactoring}', 'weight': 1.0, 'reason': 'applied_pattern'}
            ],
            output=improvement_pct / 100.0,
            metadata={
                'session_id': session_id,
                'success': success,
                'policy_update': {'old': old_weight, 'new': new_weight}
            }
        )

        # Log to improvement ledger
        outcome_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'refactoring': refactoring,
            'success': success,
            'improvement_pct': improvement_pct,
            'policy_before': old_weight,
            'policy_after': new_weight
        }

        with open(self.improvement_ledger, 'a') as f:
            f.write(json.dumps(outcome_data) + '\n')

        print(f"\nOutcome logged to: {self.improvement_ledger}")

    def analyze_refactoring_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze which refactoring patterns are most effective.

        Returns dict of {refactoring: {success_rate, avg_improvement, count}}
        """
        if not self.improvement_ledger.exists():
            return {}

        refactoring_stats = {}

        with open(self.improvement_ledger) as f:
            for line in f:
                if not line.strip():
                    continue
                outcome = json.loads(line)

                refactoring = outcome.get('refactoring')
                success = outcome.get('success', False)
                improvement = outcome.get('improvement_pct', 0)

                if refactoring not in refactoring_stats:
                    refactoring_stats[refactoring] = {
                        'total_improvement': 0,
                        'attempts': 0,
                        'successes': 0
                    }

                refactoring_stats[refactoring]['total_improvement'] += improvement
                refactoring_stats[refactoring]['attempts'] += 1
                if success:
                    refactoring_stats[refactoring]['successes'] += 1

        # Compute rates
        results = {}
        for refactoring, stats in refactoring_stats.items():
            results[refactoring] = {
                'success_rate': stats['successes'] / stats['attempts'],
                'avg_improvement': stats['total_improvement'] / stats['attempts'],
                'attempts': stats['attempts']
            }

        return results

    def _get_refactoring_description(self, refactoring: str) -> str:
        """Get human-readable description of refactoring pattern"""
        descriptions = {
            'add_type_hints': 'Add type annotations to function parameters and return types',
            'add_type_checking': 'Add runtime type validation using isinstance()',
            'use_isinstance': 'Replace type() == checks with isinstance()',
            'add_null_checks': 'Add None checks before attribute access',
            'use_getattr': 'Use getattr() with defaults instead of direct attribute access',
            'add_hasattr': 'Check attribute existence with hasattr() before access',
            'add_bounds_checking': 'Validate list indices before access',
            'use_enumerate': 'Use enumerate() instead of manual index tracking',
            'use_get_method': 'Use dict.get() with defaults instead of direct key access',
            'add_default_dict': 'Use collections.defaultdict for automatic defaults',
            'add_key_validation': 'Validate dictionary keys before access',
            'add_input_validation': 'Add validation for function input parameters',
            'use_try_except': 'Wrap risky code in try-except blocks',
            'add_constraints': 'Add value range constraints and validation',
            'check_dependencies': 'Verify required packages are installed',
            'add_try_import': 'Use try-except for optional imports',
            'fix_import_path': 'Correct module import paths',
            'fix_syntax': 'Correct syntax errors',
            'check_parentheses': 'Balance parentheses and brackets',
            'check_indentation': 'Fix indentation issues',
            'fix_logic': 'Correct logical errors in code',
            'update_test': 'Update test assertions to match implementation',
            'add_edge_case_handling': 'Add handling for edge cases and boundary conditions',
            'optimize_algorithm': 'Improve algorithm efficiency (reduce time complexity)',
            'add_caching': 'Cache expensive computations',
            'parallelize': 'Use concurrent execution for independent operations',
            'add_logging': 'Add logging statements for debugging',
            'simplify_logic': 'Reduce logical complexity and nested conditions'
        }
        return descriptions.get(refactoring, f'Apply {refactoring} refactoring')


if __name__ == "__main__":
    # Example usage
    engine = IterativeImprovementEngine()

    # Simulate failure analysis
    test_output = """
    TypeError: unsupported operand type(s) for +: 'int' and 'str'
    File "example.py", line 42, in process_data
        result = count + value
    """

    suggestion = engine.analyze_and_suggest(
        code="def process_data(count, value): return count + value",
        test_output=test_output,
        iteration=0
    )

    print(f"\n{'='*70}")
    print("REFACTORING SUGGESTION")
    print(f"{'='*70}")
    print(f"Pattern: {suggestion['refactoring']}")
    print(f"Reasoning: {suggestion['reasoning']}")

    # Simulate successful refactoring
    engine.record_outcome(
        refactoring=suggestion['refactoring'],
        success=True,
        improvement_pct=100.0
    )

    # Show effectiveness analysis
    print(f"\n{'='*70}")
    print("REFACTORING EFFECTIVENESS")
    print(f"{'='*70}")

    effectiveness = engine.analyze_refactoring_effectiveness()
    for refactoring, stats in sorted(effectiveness.items(), key=lambda x: x[1]['success_rate'], reverse=True):
        print(f"\n{refactoring}:")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg improvement: {stats['avg_improvement']:.1f}%")
        print(f"  Attempts: {stats['attempts']}")
