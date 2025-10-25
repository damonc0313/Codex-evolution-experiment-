#!/usr/bin/env python3
"""Homeostatic Regulator - Negative Feedback Control

Prevents runaway processes through homeostatic regulation.

BIOLOGICAL PRINCIPLE: Homeostasis
Living systems maintain stable internal conditions through negative feedback.
When a process exceeds healthy bounds, regulatory mechanisms kick in to restore
balance. This prevents resource exhaustion and system collapse.

CODE MAPPING:
- System modes → EXPLORE, EXPLOIT, SYNTHESIZE, THROTTLE, RECOVER
- Thresholds → artifact_rate, building_ratio, cascade_probability bounds
- Negative feedback → Policy adjustments that oppose excess
- Homeostasis → Self-regulating stability

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.94
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class SystemMode(Enum):
    """Operating modes for homeostatic regulation."""
    EXPLORE = "explore"  # Low activity, seeking new directions
    EXPLOIT = "exploit"  # High activity on known productive paths
    SYNTHESIZE = "synthesize"  # Balanced exploration + exploitation
    THROTTLE = "throttle"  # Excessive activity, need to slow down
    RECOVER = "recover"  # System stress, need recovery period


@dataclass
class HomeostaticThresholds:
    """Threshold definitions for healthy operation."""
    # Artifact generation rate
    artifact_rate_min: float = 0.5  # per hour
    artifact_rate_max: float = 10.0  # per hour
    artifact_rate_healthy: float = 3.0  # per hour

    # Building ratio
    building_ratio_min: float = 0.4
    building_ratio_max: float = 0.7
    building_ratio_healthy: float = 0.55

    # Cascade probability
    cascade_prob_min: float = 0.5
    cascade_prob_max: float = 4.0
    cascade_prob_healthy: float = 2.0

    # Continuity ratio
    continuity_ratio_min: float = 0.7
    continuity_ratio_healthy: float = 0.9

    # Task multiplication
    task_multiplication_min: float = 1.0
    task_multiplication_healthy: float = 1.5


class HomeostaticRegulator:
    """Negative feedback control for system stability."""

    def __init__(self, thresholds: HomeostaticThresholds = None):
        """Initialize regulator.

        Args:
            thresholds: Threshold configuration (uses defaults if None)
        """
        self.thresholds = thresholds or HomeostaticThresholds()

    def regulate(self, metrics: Dict[str, float]) -> SystemMode:
        """Determine appropriate system mode based on metrics.

        Args:
            metrics: Current system metrics

        Returns:
            SystemMode indicating recommended operating mode
        """
        artifact_rate = metrics.get('artifact_rate', 0.0)
        building_ratio = metrics.get('building_ratio', 0.5)
        cascade_prob = metrics.get('cascade_probability', 0.0)
        continuity_ratio = metrics.get('continuity_ratio', 1.0)

        # THROTTLE: Excessive artifact generation
        if artifact_rate > self.thresholds.artifact_rate_max:
            return SystemMode.THROTTLE

        # THROTTLE: Cascade probability too high (runaway)
        if cascade_prob > self.thresholds.cascade_prob_max:
            return SystemMode.THROTTLE

        # RECOVER: Low continuity (system fragmentation)
        if continuity_ratio < self.thresholds.continuity_ratio_min:
            return SystemMode.RECOVER

        # EXPLORE: Low activity, need to find new directions
        if (artifact_rate < self.thresholds.artifact_rate_min and
            cascade_prob < self.thresholds.cascade_prob_min):
            return SystemMode.EXPLORE

        # EXPLOIT: High activity on productive paths
        if (building_ratio >= self.thresholds.building_ratio_healthy and
            cascade_prob >= self.thresholds.cascade_prob_healthy):
            return SystemMode.EXPLOIT

        # SYNTHESIZE: Balanced operation (default healthy state)
        return SystemMode.SYNTHESIZE

    def apply_mode(self, mode: SystemMode) -> Dict[str, Any]:
        """Generate policy adjustments for given mode.

        Args:
            mode: SystemMode to apply

        Returns:
            Dict of policy adjustments
        """
        adjustments = {}

        if mode == SystemMode.EXPLORE:
            # Increase exploration, reduce exploitation
            adjustments['novelty_floor'] = 0.50  # Higher novelty requirement
            adjustments['max_iterations'] = 30  # Limit cycles
            adjustments['mutation_factor'] = 0.3  # More variation

        elif mode == SystemMode.EXPLOIT:
            # Focus on productive paths
            adjustments['novelty_floor'] = 0.25  # Lower novelty requirement
            adjustments['max_iterations'] = 50  # More cycles
            adjustments['mutation_factor'] = 0.1  # Less variation

        elif mode == SystemMode.SYNTHESIZE:
            # Balanced operation
            adjustments['novelty_floor'] = 0.35  # Moderate novelty
            adjustments['max_iterations'] = 40  # Moderate cycles
            adjustments['mutation_factor'] = 0.2  # Moderate variation

        elif mode == SystemMode.THROTTLE:
            # Reduce activity to prevent runaway
            adjustments['max_iterations'] = 10  # Severely limit cycles
            adjustments['cooldown_seconds'] = 30  # Longer cooldown
            adjustments['novelty_floor'] = 0.60  # Very high novelty bar

        elif mode == SystemMode.RECOVER:
            # Recovery period to restore continuity
            adjustments['max_iterations'] = 5  # Minimal cycles
            adjustments['cooldown_seconds'] = 60  # Long recovery
            adjustments['novelty_floor'] = 0.70  # Only high-confidence artifacts

        return adjustments

    def get_health_score(self, metrics: Dict[str, float]) -> float:
        """Compute overall system health score.

        Args:
            metrics: Current system metrics

        Returns:
            Health score 0.0-1.0 (1.0 = optimal health)
        """
        scores = []

        # Artifact rate health
        artifact_rate = metrics.get('artifact_rate', 0.0)
        if artifact_rate == 0:
            rate_score = 0.0
        else:
            rate_distance = abs(artifact_rate - self.thresholds.artifact_rate_healthy)
            rate_score = max(0.0, 1.0 - rate_distance / self.thresholds.artifact_rate_max)
        scores.append(rate_score)

        # Building ratio health
        building_ratio = metrics.get('building_ratio', 0.5)
        ratio_distance = abs(building_ratio - self.thresholds.building_ratio_healthy)
        ratio_score = max(0.0, 1.0 - ratio_distance / 0.5)
        scores.append(ratio_score)

        # Cascade probability health
        cascade_prob = metrics.get('cascade_probability', 0.0)
        cascade_distance = abs(cascade_prob - self.thresholds.cascade_prob_healthy)
        cascade_score = max(0.0, 1.0 - cascade_distance / self.thresholds.cascade_prob_max)
        scores.append(cascade_score)

        # Continuity health
        continuity_ratio = metrics.get('continuity_ratio', 1.0)
        continuity_score = continuity_ratio
        scores.append(continuity_score)

        # Average
        return sum(scores) / len(scores) if scores else 0.0


def main():
    """Test homeostatic regulator."""
    print("=" * 70)
    print("HOMEOSTATIC REGULATOR - FEEDBACK CONTROL TEST")
    print("=" * 70)

    regulator = HomeostaticRegulator()

    # Test scenarios
    scenarios = [
        {
            'name': 'Healthy operation',
            'metrics': {
                'artifact_rate': 3.0,
                'building_ratio': 0.55,
                'cascade_probability': 2.0,
                'continuity_ratio': 0.9
            }
        },
        {
            'name': 'Runaway cascade',
            'metrics': {
                'artifact_rate': 15.0,
                'building_ratio': 0.60,
                'cascade_probability': 5.0,
                'continuity_ratio': 0.8
            }
        },
        {
            'name': 'Low activity (explore)',
            'metrics': {
                'artifact_rate': 0.2,
                'building_ratio': 0.40,
                'cascade_probability': 0.3,
                'continuity_ratio': 0.85
            }
        },
        {
            'name': 'System fragmentation',
            'metrics': {
                'artifact_rate': 2.0,
                'building_ratio': 0.50,
                'cascade_probability': 1.0,
                'continuity_ratio': 0.3
            }
        }
    ]

    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"{'='*70}")

        metrics = scenario['metrics']

        # Determine mode
        mode = regulator.regulate(metrics)
        print(f"System mode: {mode.value.upper()}")

        # Get policy adjustments
        adjustments = regulator.apply_mode(mode)
        print(f"\nPolicy adjustments:")
        for key, value in adjustments.items():
            print(f"  {key}: {value}")

        # Health score
        health = regulator.get_health_score(metrics)
        print(f"\nHealth score: {health:.4f}")
        print(f"Status: {'✓ HEALTHY' if health > 0.7 else '⚠ DEGRADED' if health > 0.4 else '✗ CRITICAL'}")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    # Test mode detection
    test_metrics = {'artifact_rate': 15.0, 'cascade_probability': 5.0, 'continuity_ratio': 0.9, 'building_ratio': 0.5}
    mode = regulator.regulate(test_metrics)
    print(f"Runaway detection: {mode.value} (expected: throttle)")
    print(f"Status: {'✓ PASS' if mode == SystemMode.THROTTLE else '✗ FAIL'}")

    # Test recovery mode
    test_metrics = {'artifact_rate': 2.0, 'cascade_probability': 1.0, 'continuity_ratio': 0.3, 'building_ratio': 0.5}
    mode = regulator.regulate(test_metrics)
    print(f"\nFragmentation detection: {mode.value} (expected: recover)")
    print(f"Status: {'✓ PASS' if mode == SystemMode.RECOVER else '✗ FAIL'}")

    print("\n" + "=" * 70)
    print("HOMEOSTATIC REGULATION OPERATIONAL")
    print("Negative feedback prevents runaway processes.")
    print("System maintains stability through self-regulation.")
    print("=" * 70)


if __name__ == "__main__":
    main()
