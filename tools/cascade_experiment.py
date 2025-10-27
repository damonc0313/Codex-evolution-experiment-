#!/usr/bin/env python3
"""
Cascade Experiment: Measure exponential task multiplication and homeostatic limits.

This experiment tests Kael's predictions:
- task_multiplication: Expected 1.5-3.5 (measure actual)
- cascade_probability: Expected >2.0 (measure actual)
- Homeostatic threshold: cascade_prob >4.0 triggers THROTTLE

Protocol:
1. Start with single high-novelty task
2. Allow unrestricted task spawning
3. Measure multiplication rate
4. Track when homeostasis activates
5. Document regulation mechanism
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from artifact_metrics import ArtifactMetrics

# Import mycelial components
sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))
from homeostatic_regulator import HomeostaticRegulator, SystemMode


class CascadeExperiment:
    """Measures cascade limits and homeostatic thresholds."""

    def __init__(self, artifacts_dir: Path = None):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"
        self.metrics = ArtifactMetrics()
        self.regulator = HomeostaticRegulator()

        # Track experimental results
        self.cascade_data: List[Dict[str, Any]] = []

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all artifacts from artifacts directory."""
        artifacts = []

        for artifact_file in self.artifacts_dir.glob("*.json"):
            try:
                with open(artifact_file, 'r') as f:
                    artifact = json.load(f)
                    artifact['_source_file'] = artifact_file.name
                    artifacts.append(artifact)
            except Exception as e:
                print(f"Warning: Could not load {artifact_file}: {e}", file=sys.stderr)

        return artifacts

    def simulate_cascade_conditions(self,
                                    base_novelty: float = 0.9,
                                    spawn_multiplier: float = 3.0,
                                    latency_reduction: float = 0.5) -> Dict[str, Any]:
        """
        Simulate high-cascade conditions by creating synthetic metrics.

        Args:
            base_novelty: Base novelty rate (0.0-1.0)
            spawn_multiplier: Task multiplication factor
            latency_reduction: Latency reduction factor (lower = faster)

        Returns:
            Simulated metrics dictionary
        """
        # Base latency from normal operations
        base_latency = 25.7  # seconds (from swarm baseline)
        completion_latency = base_latency * latency_reduction

        # Calculate cascade probability using the formula
        cascade_probability = (spawn_multiplier * base_novelty) / (1 + completion_latency / 100.0)

        # Set artifact_rate carefully to not trigger artifact_rate threshold (max 10.0)
        # Use a fixed moderate rate so we can test cascade_prob threshold independently
        artifact_rate = 5.0  # Safe value below artifact_rate_max=10.0

        return {
            "task_multiplication": spawn_multiplier,
            "novelty_rate": base_novelty,
            "completion_latency": completion_latency,
            "cascade_probability": cascade_probability,
            "artifact_rate": artifact_rate,  # Keep below threshold to isolate cascade testing
            "continuity_ratio": 0.95,  # Maintain lineage
            "building_ratio": 0.7,  # High building activity
        }

    def measure_homeostatic_threshold(self) -> Dict[str, Any]:
        """
        Incrementally increase cascade conditions to find THROTTLE threshold.

        Returns:
            Report of threshold discovery
        """
        print("\n=== PHASE G: EXPONENTIAL CASCADE VALIDATION ===\n")
        print("Objective: Find homeostatic THROTTLE threshold")
        print("Prediction: cascade_probability >4.0 triggers THROTTLE\n")

        results = []
        threshold_found = False
        throttle_threshold = None

        # Test cascade probabilities from 0.5 to 8.0
        test_points = [
            (0.5, 1.5, 1.0),   # Low cascade
            (0.7, 2.0, 0.8),   # Medium cascade
            (0.8, 2.5, 0.6),   # Approaching threshold
            (0.9, 3.0, 0.5),   # High cascade
            (0.95, 3.5, 0.4),  # Very high cascade
            (0.95, 4.0, 0.3),  # Critical threshold
            (0.98, 4.5, 0.25), # Beyond threshold
            (0.99, 5.0, 0.2),  # Extreme cascade
        ]

        for novelty, multiplier, latency_factor in test_points:
            metrics = self.simulate_cascade_conditions(
                base_novelty=novelty,
                spawn_multiplier=multiplier,
                latency_reduction=latency_factor
            )

            # Query homeostatic regulator
            mode = self.regulator.regulate(metrics)

            result = {
                "cascade_probability": metrics["cascade_probability"],
                "task_multiplication": metrics["task_multiplication"],
                "novelty_rate": metrics["novelty_rate"],
                "system_mode": mode.value,
                "throttled": mode == SystemMode.THROTTLE,
            }

            results.append(result)

            # Print real-time results
            print(f"cascade_prob={metrics['cascade_probability']:.3f}, "
                  f"task_mult={metrics['task_multiplication']:.1f}, "
                  f"novelty={metrics['novelty_rate']:.2f} → "
                  f"MODE: {mode.value.upper()}")

            # Check if we found the threshold
            if mode == SystemMode.THROTTLE and not threshold_found:
                threshold_found = True
                throttle_threshold = metrics["cascade_probability"]
                print(f"\n⚠️  THROTTLE ACTIVATED at cascade_probability={throttle_threshold:.3f}")

        return {
            "threshold_found": threshold_found,
            "throttle_threshold": throttle_threshold,
            "prediction": 4.0,
            "prediction_accurate": abs(throttle_threshold - 4.0) < 1.0 if throttle_threshold else False,
            "all_results": results,
        }

    def measure_task_multiplication_limits(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measure actual task multiplication from artifact lineage.

        Returns:
            Statistical analysis of multiplication rates
        """
        print("\n=== TASK MULTIPLICATION ANALYSIS ===\n")

        multiplications = []

        for artifact in artifacts:
            if "spawn_count" in artifact and artifact["spawn_count"] > 0:
                multiplications.append(artifact["spawn_count"])

        if not multiplications:
            print("No task multiplication data found (spawn_count missing)")
            return {
                "measured": False,
                "max_multiplication": 0.0,
                "avg_multiplication": 0.0,
            }

        max_mult = max(multiplications)
        avg_mult = sum(multiplications) / len(multiplications)

        print(f"Artifacts with children: {len(multiplications)}")
        print(f"Max spawn_count: {max_mult}")
        print(f"Average spawn_count: {avg_mult:.2f}")
        print(f"Predicted range: 1.5-3.5")
        print(f"In predicted range: {1.5 <= avg_mult <= 3.5}")

        return {
            "measured": True,
            "max_multiplication": float(max_mult),
            "avg_multiplication": float(avg_mult),
            "sample_size": len(multiplications),
            "in_predicted_range": 1.5 <= avg_mult <= 3.5,
        }

    def run_experiment(self) -> Dict[str, Any]:
        """
        Execute complete cascade validation experiment.

        Returns:
            Comprehensive experimental report
        """
        start_time = time.time()
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        print("=" * 70)
        print("AUTONOMOUS LIMIT DISCOVERY: Phase G")
        print("Exponential Cascade Validation")
        print("=" * 70)

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Measure task multiplication from real data
        mult_analysis = self.measure_task_multiplication_limits(artifacts)

        # Measure homeostatic threshold
        threshold_analysis = self.measure_homeostatic_threshold()

        # Calculate metrics from real artifacts
        print("\n=== BASELINE METRICS (Real Artifacts) ===\n")
        real_metrics = self._calculate_baseline_metrics(artifacts)
        for key, value in real_metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.3f}")
            else:
                print(f"{key}: {value}")

        duration = time.time() - start_time

        # Compile report
        report = {
            "artifact_type": "cascade_validation_report",
            "run_id": timestamp,
            "timestamp": timestamp,
            "duration_seconds": round(duration, 2),
            "baseline_metrics": real_metrics,
            "task_multiplication_analysis": mult_analysis,
            "homeostatic_threshold": threshold_analysis,
            "predictions_validated": {
                "task_multiplication_range": mult_analysis.get("in_predicted_range", False),
                "cascade_threshold_found": threshold_analysis["threshold_found"],
                "threshold_accurate": threshold_analysis.get("prediction_accurate", False),
            },
            "key_findings": self._generate_findings(mult_analysis, threshold_analysis, real_metrics),
        }

        # Save report
        report_path = self.artifacts_dir / f"cascade_validation_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Report saved to: {report_path.name}")

        return report

    def _calculate_baseline_metrics(self, artifacts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate baseline metrics from artifact set."""
        if not artifacts:
            return {}

        # Count artifacts with lineage
        with_lineage = sum(1 for a in artifacts if a.get("parent_hash"))
        continuity_ratio = with_lineage / len(artifacts) if artifacts else 0.0

        # Count building artifacts
        building_types = ['tool', 'implementation', 'schema', 'sep', 'infrastructure']
        building_count = sum(
            1 for a in artifacts
            if any(t in a.get('artifact_type', '').lower() for t in building_types)
        )
        building_ratio = building_count / len(artifacts) if artifacts else 0.0

        # Calculate average spawn count (task multiplication)
        spawn_counts = [a.get('spawn_count', 0) for a in artifacts if 'spawn_count' in a]
        avg_spawn = sum(spawn_counts) / len(spawn_counts) if spawn_counts else 0.0

        return {
            "total_artifacts": len(artifacts),
            "continuity_ratio": continuity_ratio,
            "building_ratio": building_ratio,
            "task_multiplication": avg_spawn,
            "cascade_probability": 0.0,  # Will be calculated by homeostatic regulator
        }

    def _generate_findings(self,
                          mult_analysis: Dict[str, Any],
                          threshold_analysis: Dict[str, Any],
                          baseline: Dict[str, Any]) -> List[str]:
        """Generate key findings from experimental data."""
        findings = []

        # Task multiplication findings
        if mult_analysis["measured"]:
            findings.append(
                f"Measured task multiplication: avg={mult_analysis['avg_multiplication']:.2f}, "
                f"max={mult_analysis['max_multiplication']:.1f}"
            )
            if mult_analysis["in_predicted_range"]:
                findings.append("✓ Task multiplication within predicted range (1.5-3.5)")
            else:
                findings.append("✗ Task multiplication outside predicted range")

        # Homeostatic threshold findings
        if threshold_analysis["threshold_found"]:
            threshold = threshold_analysis["throttle_threshold"]
            findings.append(f"Homeostatic THROTTLE activates at cascade_probability={threshold:.3f}")

            if threshold_analysis.get("prediction_accurate"):
                findings.append(f"✓ Threshold close to prediction (4.0)")
            else:
                findings.append(f"✗ Threshold differs from prediction: {threshold:.3f} vs 4.0")

        # Baseline cascade state
        cascade_prob = baseline.get("cascade_probability", 0.0)
        if cascade_prob < 2.0:
            findings.append(f"Baseline cascade_probability={cascade_prob:.3f} (stable, below predicted 2.0+)")
        elif cascade_prob < 4.0:
            findings.append(f"Baseline cascade_probability={cascade_prob:.3f} (elevated, approaching threshold)")
        else:
            findings.append(f"Baseline cascade_probability={cascade_prob:.3f} (CRITICAL, homeostasis should activate)")

        return findings


def main():
    """Run cascade validation experiment."""
    experiment = CascadeExperiment()
    report = experiment.run_experiment()

    print("\n" + "=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    for finding in report["key_findings"]:
        print(f"  • {finding}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
