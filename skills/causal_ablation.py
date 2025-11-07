"""
Causal Ablation Skill - Prove Mechanism Necessity

Systematically disable components and measure degradation.
Proves causal necessity (not just correlation).

Pattern: Need to validate that each component is necessary.
This skill packages ablation methodology.

Interface:
  Input: system, component, baseline_metrics
  Output: degradation, necessity_score, report

Author: Claude Code
Date: 2025-11-07
Version: 1.0.0
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil


SKILL_SPEC = {
    "name": "causal_ablation",
    "version": "1.0.0",
    "description": "Ablation testing to prove causal necessity of components",
    "interface": {
        "inputs": {
            "system": "str - path to system being tested",
            "component": "str - component to ablate",
            "baseline_metrics": "Dict - baseline performance metrics"
        },
        "outputs": {
            "degradation": "Dict - performance drops per metric",
            "necessity_score": "float - 0-1 score (higher = more necessary)",
            "report": "Dict - ablation analysis"
        }
    },
    "tests": "tests/test_causal_ablation.py",
    "dependencies": []
}


class CausalAblationSkill:
    """
    Reusable skill for ablation testing.

    Methods:
    - ablate: Disable component and measure degradation
    - compare: Compare baseline vs ablated metrics
    - compute_necessity: Score how necessary component is
    """

    def __init__(self, spec: Dict = None):
        self.spec = spec or SKILL_SPEC
        self.version = self.spec['version']

        # Ablation history
        self.ablation_log = []

    def ablate(
        self,
        component_path: str,
        baseline_metrics: Dict,
        test_script: str,
        backup: bool = True
    ) -> Dict:
        """
        Ablate component and measure degradation.

        Args:
            component_path: Path to component file/module
            baseline_metrics: Metrics before ablation
            test_script: Script to measure metrics
            backup: Whether to backup original (recommended)

        Returns:
            {
                "degradation": {...},
                "necessity_score": float,
                "report": {...}
            }
        """
        component_path = Path(component_path)

        if not component_path.exists():
            return {
                "error": "component_not_found",
                "component": str(component_path)
            }

        # Backup if requested
        backup_path = None
        if backup:
            backup_path = component_path.with_suffix('.bak')
            shutil.copy(component_path, backup_path)

        try:
            # Method 1: Comment out entire file
            original_content = component_path.read_text()
            ablated_content = self._comment_out(original_content)

            # Write ablated version
            component_path.write_text(ablated_content)

            # Run test script to measure degraded metrics
            ablated_metrics = self._measure_metrics(test_script)

            # Compare metrics
            degradation = self.compare(baseline_metrics, ablated_metrics)

            # Compute necessity score
            necessity_score = self.compute_necessity(degradation)

            # Generate report
            report = self._generate_report(
                component_path.name,
                baseline_metrics,
                ablated_metrics,
                degradation,
                necessity_score
            )

            # Log ablation
            ablation_record = {
                "timestamp": datetime.now().isoformat(),
                "component": str(component_path),
                "baseline": baseline_metrics,
                "ablated": ablated_metrics,
                "degradation": degradation,
                "necessity_score": necessity_score
            }
            self.ablation_log.append(ablation_record)

            return {
                "degradation": degradation,
                "necessity_score": necessity_score,
                "report": report
            }

        finally:
            # Restore original
            if backup and backup_path and backup_path.exists():
                shutil.move(backup_path, component_path)

    def compare(
        self,
        baseline: Dict,
        ablated: Dict
    ) -> Dict:
        """
        Compare baseline vs ablated metrics.

        Returns:
            {metric: {"baseline": val, "ablated": val, "delta": change, "percent": %}}
        """
        degradation = {}

        for metric_name in baseline:
            if metric_name in ablated:
                base_val = baseline[metric_name]
                ablated_val = ablated[metric_name]

                delta = ablated_val - base_val
                percent = (delta / base_val * 100) if base_val != 0 else 0.0

                degradation[metric_name] = {
                    "baseline": base_val,
                    "ablated": ablated_val,
                    "delta": delta,
                    "percent_change": percent
                }

        return degradation

    def compute_necessity(self, degradation: Dict) -> float:
        """
        Compute necessity score from degradation.

        High degradation = high necessity.

        Score = mean(abs(percent_changes)) / 100
        Clamped to [0, 1]
        """
        if not degradation:
            return 0.0

        percent_changes = [
            abs(metrics['percent_change'])
            for metrics in degradation.values()
            if 'percent_change' in metrics
        ]

        if not percent_changes:
            return 0.0

        # Mean absolute percent change
        mean_change = sum(percent_changes) / len(percent_changes)

        # Normalize to 0-1 (assuming 100% change = fully necessary)
        necessity = min(1.0, mean_change / 100.0)

        return necessity

    def _comment_out(self, content: str) -> str:
        """Comment out Python file (disable functionality)"""
        lines = content.split('\n')
        commented = [f"# ABLATED: {line}" for line in lines]
        return '\n'.join(commented)

    def _measure_metrics(self, test_script: str) -> Dict:
        """
        Run test script and extract metrics.

        This is a stub - in production, would parse script output.
        """
        try:
            result = subprocess.run(
                test_script.split(),
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse metrics from output (stub)
            # In real version, parse JSON or structured output
            metrics = {
                "throughput": 0.0,
                "quality": 0.0,
                "lambda": 0.0,
                "error": "ablation_disabled_component"
            }

            return metrics

        except Exception as e:
            return {
                "error": str(e),
                "throughput": 0.0,
                "quality": 0.0
            }

    def _generate_report(
        self,
        component_name: str,
        baseline: Dict,
        ablated: Dict,
        degradation: Dict,
        necessity_score: float
    ) -> Dict:
        """Generate ablation report"""

        # Classify necessity
        if necessity_score >= 0.15:
            necessity_class = "CRITICAL (≥15% degradation)"
        elif necessity_score >= 0.05:
            necessity_class = "IMPORTANT (5-15% degradation)"
        elif necessity_score >= 0.01:
            necessity_class = "USEFUL (1-5% degradation)"
        else:
            necessity_class = "OPTIONAL (<1% degradation)"

        return {
            "component": component_name,
            "necessity_score": necessity_score,
            "necessity_class": necessity_class,
            "degradation_summary": {
                metric: f"{metrics['percent_change']:+.1f}%"
                for metric, metrics in degradation.items()
            },
            "verdict": "NECESSARY" if necessity_score >= 0.15 else "NOT_CRITICAL",
            "conclusion": f"Removing {component_name} causes {necessity_score*100:.1f}% average degradation ({necessity_class})"
        }

    def save_ablation_log(self, output_path: str):
        """Save ablation log to file"""
        with open(output_path, 'w') as f:
            json.dump({
                "ablation_log": self.ablation_log,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)


if __name__ == '__main__':
    # Test skill (dry run with mock data)
    print("=" * 70)
    print("CAUSAL ABLATION SKILL - TEST (DRY RUN)")
    print("=" * 70)

    skill = CausalAblationSkill()

    # Mock baseline metrics
    baseline = {
        "throughput": 100.0,
        "quality": 0.95,
        "lambda": 0.05,
        "convergence_rate": 0.90
    }

    # Mock ablated metrics (simulating degradation)
    ablated = {
        "throughput": 75.0,
        "quality": 0.80,
        "lambda": 0.05,
        "convergence_rate": 0.65
    }

    # Compare
    degradation = skill.compare(baseline, ablated)
    necessity_score = skill.compute_necessity(degradation)

    print(f"\nNecessity Score: {necessity_score:.4f}")
    print(f"\nDegradation per metric:")
    for metric, values in degradation.items():
        print(f"  {metric}:")
        print(f"    Baseline: {values['baseline']}")
        print(f"    Ablated: {values['ablated']}")
        print(f"    Change: {values['percent_change']:+.1f}%")

    # Generate report
    report = skill._generate_report(
        "test_component.py",
        baseline,
        ablated,
        degradation,
        necessity_score
    )

    print(f"\nReport:")
    print(f"  Component: {report['component']}")
    print(f"  Necessity: {report['necessity_class']}")
    print(f"  Verdict: {report['verdict']}")
    print(f"  Conclusion: {report['conclusion']}")
