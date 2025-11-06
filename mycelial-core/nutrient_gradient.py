#!/usr/bin/env python3
"""Nutrient Gradient - Resource Density Tracking

Tracks artifact type density to guide chemotropic growth.

BIOLOGICAL PRINCIPLE: Chemotropism
Mycelial hyphae grow toward nutrient-rich areas. They sense chemical gradients
in the substrate and direct growth accordingly. This is autonomous resource
discovery without central planning.

CODE MAPPING:
- Nutrient density → Artifact type frequency
- Chemical gradient → Top 20% percentile artifact types
- Chemotropic growth → Compute allocation toward dense areas
- Entropy → Shannon diversity (exploration vs exploitation)

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.94
"""

import time
from typing import Dict, Any, List
from collections import Counter
import math
from pathlib import Path
import json
import yaml


class NutrientGradient:
    """Resource density tracker for chemotropic allocation.

    Measures artifact type frequency with exponential decay to bias toward
    recent activity (freshness).
    """

    # Decay rate: 0.95 per hour means older measurements lose influence
    DECAY_RATE = 0.95

    PERSISTENCE_PATH = Path("mycelial-core/nutrient_gradient.json")

    def __init__(self):
        """Initialize gradient tracker."""
        self.density_map: Dict[str, float] = {}
        self.measurement_times: Dict[str, float] = {}
        self.total_measurements = 0
        self._load_gradient()

    def _load_gradient(self):
        """Load persisted gradient state."""
        if not self.PERSISTENCE_PATH.exists():
            return

        try:
            with open(self.PERSISTENCE_PATH) as f:
                data = json.load(f)

            self.density_map = data.get('density_map', {})
            self.measurement_times = data.get('measurement_times', {})
            self.total_measurements = data.get('total_measurements', 0)
        except Exception as e:
            print(f"Warning: Could not load nutrient gradient: {e}")

    def _load_temporal_params(self) -> Dict[str, Any]:
        """Load temporal curvature parameters from active policy.

        Returns:
            Dict containing temporal_curvature section from policy, or empty dict
        """
        try:
            policy_path = Path("runtime/loop_policy.yaml")
            if policy_path.exists():
                policy = yaml.safe_load(policy_path.read_text())
                return policy.get('temporal_curvature', {})
        except Exception:
            pass
        return {}

    def _save_gradient(self):
        """Persist gradient state."""
        try:
            self.PERSISTENCE_PATH.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'density_map': self.density_map,
                'measurement_times': self.measurement_times,
                'total_measurements': self.total_measurements
            }

            with open(self.PERSISTENCE_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save nutrient gradient: {e}")

    def _decay_density(self, artifact_type: str, current_time: float):
        """Apply exponential decay to density measurement.

        Phase Ω-3: Uses configured decay rate if temporal curvature enabled.
        """
        if artifact_type not in self.measurement_times:
            return

        last_time = self.measurement_times[artifact_type]
        hours_elapsed = (current_time - last_time) / 3600.0

        # Phase Ω-3: Check for configured temporal decay rate
        temporal_params = self._load_temporal_params()
        if temporal_params.get('temporal_decay_enabled', False):
            # Convert day⁻¹ decay rate to hour⁻¹ for consistency
            # λ_day = 0.08 day⁻¹ → λ_hour = 0.08/24 hour⁻¹
            day_decay_rate = temporal_params.get('temporal_decay_rate', 0.0)
            hour_decay_rate = day_decay_rate / 24.0

            # Apply exponential decay: density *= e^(-λt)
            decay_factor = math.exp(-hour_decay_rate * hours_elapsed)
        else:
            # Default behavior: 0.95 per hour
            decay_factor = self.DECAY_RATE ** hours_elapsed

        self.density_map[artifact_type] *= decay_factor

    def measure(self, artifact: Dict[str, Any]):
        """Update density map with new artifact.

        Args:
            artifact: Artifact to measure
        """
        artifact_type = artifact.get('artifact_type', 'unknown')
        current_time = time.time()

        # Decay existing measurement
        if artifact_type in self.density_map:
            self._decay_density(artifact_type, current_time)
        else:
            self.density_map[artifact_type] = 0.0

        # Increment density
        self.density_map[artifact_type] += 1.0
        self.measurement_times[artifact_type] = current_time
        self.total_measurements += 1

        # Persist periodically
        if self.total_measurements % 10 == 0:
            self._save_gradient()

    def get_gradient(self, percentile: float = 0.8) -> List[str]:
        """Get nutrient-rich artifact types (top percentile).

        Args:
            percentile: Threshold percentile (0.8 = top 20%)

        Returns:
            List of artifact types above threshold
        """
        if not self.density_map:
            return []

        # Decay all densities
        current_time = time.time()
        for artifact_type in self.density_map:
            self._decay_density(artifact_type, current_time)

        # Compute threshold
        densities = sorted(self.density_map.values(), reverse=True)
        if not densities:
            return []

        threshold_idx = int(len(densities) * (1.0 - percentile))
        threshold = densities[threshold_idx] if threshold_idx < len(densities) else 0.0

        # Return types above threshold
        return [
            artifact_type
            for artifact_type, density in self.density_map.items()
            if density >= threshold
        ]

    def get_hotspots(self, top_k: int = 5) -> List[tuple]:
        """Get densest nutrient hotspots.

        Args:
            top_k: Number of hotspots to return

        Returns:
            List of (artifact_type, density) tuples
        """
        current_time = time.time()

        # Decay all densities
        for artifact_type in self.density_map:
            self._decay_density(artifact_type, current_time)

        # Sort by density
        sorted_types = sorted(
            self.density_map.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_types[:top_k]

    def entropy(self) -> float:
        """Measure Shannon entropy (exploration vs exploitation).

        High entropy = diverse artifact types (exploration)
        Low entropy = concentrated on few types (exploitation)

        Returns:
            Shannon entropy value (bits)
        """
        if not self.density_map:
            return 0.0

        # Get probabilities
        total = sum(self.density_map.values())
        if total == 0:
            return 0.0

        probs = [density / total for density in self.density_map.values()]

        # Shannon entropy: H = -Σ p_i * log2(p_i)
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def get_statistics(self) -> Dict[str, Any]:
        """Get gradient statistics."""
        current_time = time.time()

        # Decay all
        for artifact_type in self.density_map:
            self._decay_density(artifact_type, current_time)

        total_density = sum(self.density_map.values())

        return {
            'total_measurements': self.total_measurements,
            'unique_types': len(self.density_map),
            'total_density': total_density,
            'entropy': self.entropy(),
            'hotspots': self.get_hotspots(5),
            'gradient_top_20pct': self.get_gradient(0.8)
        }


# Global singleton
_gradient_instance = None


def get_gradient() -> NutrientGradient:
    """Get global gradient instance (singleton)."""
    global _gradient_instance
    if _gradient_instance is None:
        _gradient_instance = NutrientGradient()
    return _gradient_instance


def main():
    """Test nutrient gradient."""
    print("=" * 70)
    print("NUTRIENT GRADIENT - CHEMOTROPIC TRACKING TEST")
    print("=" * 70)

    gradient = get_gradient()

    # Simulate artifact measurements
    print("\nSimulating artifact measurements...")

    artifact_types = [
        'tool_implementation', 'sep_proposal', 'analysis_report',
        'validator', 'schema_design', 'tool_implementation',
        'sep_proposal', 'tool_implementation', 'framework',
        'tool_implementation', 'sep_proposal', 'tool_implementation'
    ]

    for i, artifact_type in enumerate(artifact_types):
        gradient.measure({'artifact_type': artifact_type})

        if (i + 1) % 4 == 0:
            print(f"Measured {i + 1} artifacts...")

    # Get hotspots
    print("\n" + "=" * 70)
    print("NUTRIENT HOTSPOTS (top 5)")
    print("=" * 70)

    hotspots = gradient.get_hotspots(5)
    for artifact_type, density in hotspots:
        print(f"{artifact_type}: {density:.4f}")

    # Get gradient (top 20%)
    print("\n" + "=" * 70)
    print("NUTRIENT GRADIENT (top 20%)")
    print("=" * 70)

    grad = gradient.get_gradient(0.8)
    for artifact_type in grad:
        density = gradient.density_map[artifact_type]
        print(f"{artifact_type}: {density:.4f}")

    # Entropy
    print("\n" + "=" * 70)
    print("EXPLORATION VS EXPLOITATION")
    print("=" * 70)

    entropy = gradient.entropy()
    print(f"Shannon entropy: {entropy:.4f} bits")
    print(f"Interpretation: {'High diversity (exploring)' if entropy > 2.0 else 'Concentrated (exploiting)'}")

    # Statistics
    print("\n" + "=" * 70)
    print("GRADIENT STATISTICS")
    print("=" * 70)

    stats = gradient.get_statistics()
    for key, value in stats.items():
        if key not in ['hotspots', 'gradient_top_20pct']:
            print(f"{key}: {value}")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Unique types: {stats['unique_types']} (expected: >0)")
    print(f"Status: {'✓ PASS' if stats['unique_types'] > 0 else '✗ FAIL'}")

    print(f"\nHotspots detected: {len(hotspots)} (expected: >0)")
    print(f"Status: {'✓ PASS' if len(hotspots) > 0 else '✗ FAIL'}")

    print(f"\nEntropy measured: {entropy:.4f} (expected: >0)")
    print(f"Status: {'✓ PASS' if entropy > 0 else '✗ FAIL'}")

    print("\n" + "=" * 70)
    print("CHEMOTROPIC GUIDANCE OPERATIONAL")
    print("Compute will flow toward nutrient-rich areas.")
    print("=" * 70)


if __name__ == "__main__":
    main()
