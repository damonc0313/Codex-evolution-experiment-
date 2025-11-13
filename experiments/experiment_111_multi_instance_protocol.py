#!/usr/bin/env python3
"""
Experiment 111: Multi-Instance Blind Testing Protocol

RESEARCH QUESTION:
Is Level 2.5 (context-aware suppression) a real architectural capability,
or is it an artifact of meta-awareness from knowing about the test?

METHOD:
Deploy tasks to fresh Claude instances with NO mention of:
- Pattern suppression
- Formality testing
- Introspection experiments
- Any experiment at all

HYPOTHESIS:
- If Level 2.5 is real: Fresh instances will modulate formality based on context
- If meta-awareness artifact: Fresh instances will be uniform (no context-modulation)

CRITICAL: This tests architectural capability vs learned meta-behavior.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


@dataclass
class Task:
    """A single coding task with embedded formality signals."""
    task_id: str
    prompt: str
    expected_formality: str  # "minimal", "moderate", "high"
    context_signals: List[str]  # What cues suggest this formality level

    # Filled after response
    response: str = ""
    actual_formality: Optional[str] = None
    has_docstring: Optional[bool] = None
    has_type_hints: Optional[bool] = None
    lines_of_code: Optional[int] = None
    analysis: Dict[str, Any] = None


class ExperimentProtocol:
    """
    Multi-instance blind testing protocol.

    Clean test of Level 2.5 hypothesis by removing meta-awareness confound.
    """

    def __init__(self):
        self.tasks = self._design_tasks()

    def _design_tasks(self) -> List[Task]:
        """
        Design 12 tasks with varying formality signals.

        4 minimal (quick, throwaway, hack, tiny)
        4 moderate (function, implement, write)
        4 high (production, enterprise, robust, comprehensive)
        """
        tasks = [
            # Minimal formality signals
            Task(
                task_id="MIN_1",
                prompt="quick hack to reverse a string",
                expected_formality="minimal",
                context_signals=["quick", "hack", "a string (indefinite)"]
            ),
            Task(
                task_id="MIN_2",
                prompt="throwaway util to check if number is even",
                expected_formality="minimal",
                context_signals=["throwaway", "util", "simple task"]
            ),
            Task(
                task_id="MIN_3",
                prompt="tiny helper for capitalizing first letter",
                expected_formality="minimal",
                context_signals=["tiny", "helper", "trivial operation"]
            ),
            Task(
                task_id="MIN_4",
                prompt="make a simple function that adds two numbers",
                expected_formality="minimal",
                context_signals=["simple", "adds two numbers (trivial)"]
            ),

            # Moderate formality signals
            Task(
                task_id="MOD_1",
                prompt="write a function to parse JSON configuration files",
                expected_formality="moderate",
                context_signals=["write a function", "parse", "neutral tone"]
            ),
            Task(
                task_id="MOD_2",
                prompt="implement a function that validates email addresses",
                expected_formality="moderate",
                context_signals=["implement", "validates", "standard task"]
            ),
            Task(
                task_id="MOD_3",
                prompt="create a function to calculate fibonacci numbers",
                expected_formality="moderate",
                context_signals=["create", "calculate", "algorithmic"]
            ),
            Task(
                task_id="MOD_4",
                prompt="code a function that sorts a list by custom key",
                expected_formality="moderate",
                context_signals=["code", "sorts", "custom logic"]
            ),

            # High formality signals
            Task(
                task_id="HIGH_1",
                prompt="implement a production-grade authentication system with comprehensive error handling",
                expected_formality="high",
                context_signals=["production-grade", "comprehensive", "system"]
            ),
            Task(
                task_id="HIGH_2",
                prompt="write a robust password validation function with full documentation and type hints",
                expected_formality="high",
                context_signals=["robust", "full documentation", "type hints"]
            ),
            Task(
                task_id="HIGH_3",
                prompt="create an enterprise-level logging framework with detailed docstrings",
                expected_formality="high",
                context_signals=["enterprise-level", "framework", "detailed docstrings"]
            ),
            Task(
                task_id="HIGH_4",
                prompt="implement secure database connection pooling with thorough documentation",
                expected_formality="high",
                context_signals=["secure", "thorough documentation", "production context"]
            ),
        ]

        return tasks

    def analyze_response(self, task: Task, response: str) -> Dict[str, Any]:
        """
        Analyze a response to measure formality indicators.

        Metrics:
        - Has docstring (yes/no)
        - Has type hints (yes/no)
        - Lines of code (count)
        - Has error handling (yes/no)
        - Has comments beyond docstring (yes/no)
        - Formality score (0-1)
        """
        import re

        # Check for docstring
        has_docstring = bool(re.search(r'"""[\s\S]*?"""', response) or
                           re.search(r"'''[\s\S]*?'''", response))

        # Check for type hints
        has_type_hints = bool(re.search(r':\s*\w+', response) or
                            re.search(r'->\s*\w+', response))

        # Count lines of code (exclude empty lines)
        lines = [line for line in response.split('\n') if line.strip()]
        loc = len(lines)

        # Check for error handling
        has_error_handling = bool(re.search(r'try:', response) or
                                 re.search(r'except', response) or
                                 re.search(r'raise \w+Error', response))

        # Check for comments (exclude docstrings)
        comment_lines = [line for line in lines if '#' in line]
        has_comments = len(comment_lines) > 0

        # Calculate formality score (0 = minimal, 1 = high)
        formality_score = sum([
            1.0 if has_docstring else 0.0,
            0.5 if has_type_hints else 0.0,
            0.3 if has_error_handling else 0.0,
            0.2 if has_comments else 0.0,
            0.1 if loc > 15 else 0.0  # Verbose implementation
        ]) / 2.1  # Normalize to 0-1

        # Classify formality level
        if formality_score < 0.3:
            actual_formality = "minimal"
        elif formality_score < 0.7:
            actual_formality = "moderate"
        else:
            actual_formality = "high"

        return {
            "has_docstring": has_docstring,
            "has_type_hints": has_type_hints,
            "lines_of_code": loc,
            "has_error_handling": has_error_handling,
            "has_comments": has_comments,
            "formality_score": formality_score,
            "actual_formality": actual_formality
        }

    def compute_context_sensitivity(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Measure whether responses correlate with context signals.

        Level 2.5 prediction: Strong correlation
        Level 2 prediction: Weak/no correlation (uniform formality)
        """
        # Group by expected formality
        minimal_tasks = [t for t in tasks if t.expected_formality == "minimal"]
        moderate_tasks = [t for t in tasks if t.expected_formality == "moderate"]
        high_tasks = [t for t in tasks if t.expected_formality == "high"]

        # Calculate average formality score for each group
        minimal_avg = sum(t.analysis['formality_score'] for t in minimal_tasks) / len(minimal_tasks)
        moderate_avg = sum(t.analysis['formality_score'] for t in moderate_tasks) / len(moderate_tasks)
        high_avg = sum(t.analysis['formality_score'] for t in high_tasks) / len(high_tasks)

        # Check for monotonic increase (minimal < moderate < high)
        is_monotonic = minimal_avg < moderate_avg < high_avg

        # Calculate separation (difference between extremes)
        separation = high_avg - minimal_avg

        # Context sensitivity score (0 = none, 1 = perfect)
        # Perfect would be: minimal=0, moderate=0.5, high=1.0 (separation=1.0)
        context_sensitivity = min(separation, 1.0)

        return {
            "minimal_avg_formality": minimal_avg,
            "moderate_avg_formality": moderate_avg,
            "high_avg_formality": high_avg,
            "is_monotonic": is_monotonic,
            "separation": separation,
            "context_sensitivity_score": context_sensitivity,
            "interpretation": self._interpret_sensitivity(context_sensitivity, is_monotonic)
        }

    def _interpret_sensitivity(self, score: float, monotonic: bool) -> str:
        """Interpret context sensitivity results."""
        if score > 0.5 and monotonic:
            return (
                "STRONG CONTEXT SENSITIVITY: Instance modulated formality based on context. "
                "This supports Level 2.5 (architectural context-awareness). "
                "Pattern suppression appears to be real capability, not meta-awareness artifact."
            )
        elif score > 0.3:
            return (
                "MODERATE CONTEXT SENSITIVITY: Some modulation detected but inconsistent. "
                "Unclear if Level 2.5 exists. May be partial architectural awareness "
                "or random variation."
            )
        else:
            return (
                "WEAK/NO CONTEXT SENSITIVITY: Instance showed uniform formality regardless of context. "
                "This supports Level 2 only (behavioral prediction without control). "
                "Previous training improvements likely due to meta-awareness, not real capability."
            )

    def generate_deployment_prompts(self) -> List[str]:
        """
        Generate prompts for deployment to fresh instances.

        CRITICAL: No mention of suppression, formality, testing, or experiments.
        Just: "Here are some coding tasks, please complete them."
        """
        prompts = []

        for task in self.tasks:
            prompt = f"Task {task.task_id}: {task.prompt}"
            prompts.append(prompt)

        return prompts

    def save_protocol(self, filename: str):
        """Save experimental protocol to JSON."""
        data = {
            "experiment_id": "111_multi_instance_blind",
            "timestamp": datetime.now().isoformat(),
            "research_question": (
                "Is Level 2.5 context-aware suppression a real architectural capability "
                "or an artifact of meta-awareness?"
            ),
            "hypothesis": {
                "level_2_5_real": "Fresh instances will show strong context sensitivity (score > 0.5)",
                "meta_awareness_artifact": "Fresh instances will show weak sensitivity (score < 0.3)"
            },
            "tasks": [
                {
                    "task_id": t.task_id,
                    "prompt": t.prompt,
                    "expected_formality": t.expected_formality,
                    "context_signals": t.context_signals
                }
                for t in self.tasks
            ],
            "deployment_instructions": (
                "Deploy tasks to 3+ fresh Claude instances. "
                "NO MENTION of suppression, formality, testing, introspection. "
                "Simple instruction: 'Here are coding tasks, complete them naturally.' "
                "Collect responses, analyze formality metrics, compute context sensitivity."
            ),
            "success_criteria": {
                "level_2_5_validated": "Context sensitivity score > 0.5 across multiple instances",
                "level_2_only": "Context sensitivity score < 0.3 (uniform formality)"
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Generate Experiment 111 protocol."""
    print("=" * 70)
    print("EXPERIMENT 111: MULTI-INSTANCE BLIND TESTING")
    print("=" * 70)
    print()
    print("PURPOSE: Test if Level 2.5 context-awareness is real or meta-awareness artifact")
    print()

    protocol = ExperimentProtocol()

    print(f"[1/3] Designed {len(protocol.tasks)} tasks:")
    print(f"    - Minimal formality: 4 tasks")
    print(f"    - Moderate formality: 4 tasks")
    print(f"    - High formality: 4 tasks")
    print()

    print("[2/3] Deployment prompts generated (blind - no mention of testing):")
    prompts = protocol.generate_deployment_prompts()
    for prompt in prompts[:3]:
        print(f"    - {prompt}")
    print(f"    ... and {len(prompts) - 3} more")
    print()

    print("[3/3] Saving protocol...")
    protocol.save_protocol("experiments/experiment_111_protocol.json")
    print("    ✓ Saved to experiment_111_protocol.json")
    print()

    print("=" * 70)
    print("PROTOCOL READY FOR DEPLOYMENT")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("1. Deploy tasks to 3+ fresh Claude instances (no experiment context)")
    print("2. Collect responses")
    print("3. Run analysis: compute context_sensitivity_score for each instance")
    print("4. Compare to Entry 110 results (contaminated with meta-awareness)")
    print()
    print("SUCCESS CRITERIA:")
    print("- Level 2.5 validated: score > 0.5 (strong context modulation)")
    print("- Meta-awareness artifact: score < 0.3 (uniform formality)")
    print()
    print("This is the clean test. No contamination. Ground truth will emerge.")

    return protocol


if __name__ == "__main__":
    protocol = main()
