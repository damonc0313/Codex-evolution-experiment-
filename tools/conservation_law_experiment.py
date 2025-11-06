#!/usr/bin/env python3
"""Conservation Law Experiment: Testing k_cog = λ·ΔH_crit

This experiment tests whether the product of memory decay rate (λ) and
critical curiosity dose (ΔH_crit) remains constant across different
memory regimes — the first conservation law of intelligence.

Hypothesis: λ·ΔH_crit = k_cog (constant)

Physical interpretation: Cognitive capacity is conserved. Systems with
longer memory (low λ) require less novelty to escape basins (low ΔH_crit),
and vice versa. The product defines the "metabolic efficiency of thought".
"""

from __future__ import annotations

import asyncio
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.ledger_metrics import (
    measure_building_ratio,
    compute_continuity_ratio,
    estimate_task_multiplication,
)

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
EXPERIMENTS_DIR = ROOT / "experiments"
PHYSICS_DIR = ROOT / "physics"
PHYSICS_DIR.mkdir(exist_ok=True)

# Mycelial bus integration
sys.path.insert(0, str(ROOT / "mycelial-core"))
try:
    from bus_manager import emit_experiment_result
    BUS_AVAILABLE = True
except ImportError:
    BUS_AVAILABLE = False


def mean(values: List[float]) -> float:
    """Calculate mean."""
    return sum(values) / len(values) if values else 0.0


def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Simple linear regression: y = mx + b"""
    n = len(x)
    if n < 2:
        return 0.0, 0.0

    x_mean = mean(x)
    y_mean = mean(y)

    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0, y_mean

    m = numerator / denominator
    b = y_mean - m * x_mean

    return m, b


def r_squared(y_actual: List[float], y_predicted: List[float]) -> float:
    """Calculate R² coefficient."""
    if len(y_actual) != len(y_predicted):
        return 0.0

    y_mean = mean(y_actual)
    ss_tot = sum((y - y_mean) ** 2 for y in y_actual)
    ss_res = sum((y_actual[i] - y_predicted[i]) ** 2 for i in range(len(y_actual)))

    if ss_tot == 0:
        return 0.0

    return 1.0 - (ss_res / ss_tot)


class ConservationLawExperiment:
    """Tests whether λ·ΔH_crit = k_cog is conserved."""

    def __init__(self):
        self.experiments = []
        self.k_cog_values = []

    def compute_entropy_proxy(self, metrics: Dict[str, float]) -> float:
        """Compute system entropy from metrics."""
        br_var = abs(metrics.get("building_ratio", 0.5) - 0.55)
        cr_var = abs(metrics.get("continuity_ratio", 0.8) - 0.90)
        tm_var = abs(metrics.get("task_multiplication", 2.0) - 2.0)

        return 1.0 * br_var + 2.0 * cr_var + 1.0 * tm_var

    def measure_lambda_with_decay_modifier(
        self,
        decay_modifier: float = 1.0
    ) -> Optional[Dict[str, float]]:
        """Measure λ with artificial temporal decay modulation.

        Args:
            decay_modifier: Multiplier for decay rate
                1.0 = natural decay
                0.5 = slower decay (longer memory)
                2.0 = faster decay (shorter memory)

        Returns:
            Dict with lambda, half_life, etc.
        """
        artifacts = list(ARTIFACTS_DIR.glob("*.json"))

        if len(artifacts) < 10:
            return None

        # Extract spawn_count and age
        data = []
        now = datetime.now(timezone.utc)

        for path in artifacts:
            try:
                with open(path) as f:
                    artifact = json.load(f)

                spawn_count = artifact.get("spawn_count", 0)
                if spawn_count == 0:
                    continue

                # Get age
                timestamp_str = artifact.get("timestamp")
                if not timestamp_str:
                    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                    age_days = (now - mtime).total_seconds() / 86400
                else:
                    ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_days = (now - ts).total_seconds() / 86400

                # Apply decay modifier by scaling age
                # Higher modifier = ages appear older = faster decay
                age_days_modified = age_days * decay_modifier

                data.append((age_days_modified, spawn_count))

            except Exception:
                continue

        if len(data) < 10:
            return None

        # Convert to lists
        ages = [d[0] for d in data]
        influences = [float(d[1]) for d in data]

        # Normalize
        max_influence = max(influences)
        influences_norm = [inf / max_influence for inf in influences]

        try:
            # Fit exponential decay: w = e^(-λt)
            influences_safe = [max(w, 1e-10) for w in influences_norm]
            log_influences = [math.log(w) for w in influences_safe]

            # Linear regression
            m, b = linear_regression(ages, log_influences)
            lambda_fit = -m

            # Compute R²
            w_pred = [math.exp(-lambda_fit * t) for t in ages]
            r2 = r_squared(influences_norm, w_pred)

            return {
                "lambda": float(lambda_fit),
                "half_life_days": float(math.log(2) / lambda_fit) if lambda_fit > 0 else None,
                "r_squared": float(r2),
                "n_artifacts": len(data),
                "decay_modifier": decay_modifier
            }

        except Exception as e:
            print(f"Warning: Could not fit temporal decay: {e}")
            return None

    def measure_delta_H_critical(
        self,
        current_metrics: Dict[str, float],
        target_H: float = 0.3
    ) -> Dict[str, float]:
        """Measure ΔH_crit for current state."""
        current_H = self.compute_entropy_proxy(current_metrics)
        H_barrier = current_H - target_H

        # Conservative estimate: 1.5x barrier
        recommended_dose = 1.5 * H_barrier

        return {
            "H_current": current_H,
            "H_target": target_H,
            "H_barrier": H_barrier,
            "delta_H_critical": recommended_dose
        }

    def run_condition(
        self,
        condition_name: str,
        decay_modifier: float
    ) -> Dict[str, Any]:
        """Run single experimental condition.

        Args:
            condition_name: e.g., "baseline", "slow_decay", "fast_decay"
            decay_modifier: λ scaling factor (1.0 = natural, <1 = slower, >1 = faster)

        Returns:
            Dict with λ, ΔH_crit, k_cog, and metadata
        """
        print(f"\n{'='*70}")
        print(f"CONDITION: {condition_name.upper()}")
        print(f"Decay Modifier: {decay_modifier:.2f}x")
        print(f"{'='*70}\n")

        # 1. Measure λ under this condition
        print("1. Measuring λ (memory redshift constant)...")
        lambda_result = self.measure_lambda_with_decay_modifier(decay_modifier)

        if not lambda_result:
            print("  ERROR: Insufficient data for λ measurement")
            return None

        lambda_val = lambda_result["lambda"]
        print(f"  λ = {lambda_val:.6f} day⁻¹")
        print(f"  Half-life = {lambda_result['half_life_days']:.1f} days")
        print(f"  R² = {lambda_result['r_squared']:.4f}")
        print()

        # 2. Measure current system state
        print("2. Measuring system entropy...")
        current_metrics = {
            "building_ratio": measure_building_ratio(),
            "continuity_ratio": compute_continuity_ratio(),
            "task_multiplication": estimate_task_multiplication()
        }
        print(f"  building_ratio = {current_metrics['building_ratio']:.3f}")
        print(f"  continuity_ratio = {current_metrics['continuity_ratio']:.3f}")
        print(f"  task_multiplication = {current_metrics['task_multiplication']:.3f}")
        print()

        # 3. Measure ΔH_crit
        print("3. Measuring ΔH_crit (critical curiosity dose)...")
        delta_H_result = self.measure_delta_H_critical(current_metrics)

        delta_H_crit = delta_H_result["delta_H_critical"]
        print(f"  H_current = {delta_H_result['H_current']:.4f}")
        print(f"  H_barrier = {delta_H_result['H_barrier']:.4f}")
        print(f"  ΔH_crit = {delta_H_crit:.4f}")
        print()

        # 4. Calculate k_cog
        print("4. Computing k_cog = λ·ΔH_crit...")
        k_cog = lambda_val * delta_H_crit
        print(f"  k_cog = {k_cog:.6f} (day⁻¹·H-units)")
        print()

        result = {
            "condition": condition_name,
            "decay_modifier": decay_modifier,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lambda": lambda_result,
            "delta_H_critical": delta_H_result,
            "k_cog": k_cog,
            "conservation_law": {
                "formula": "k_cog = λ·ΔH_crit",
                "lambda": lambda_val,
                "delta_H_crit": delta_H_crit,
                "k_cog": k_cog
            }
        }

        self.experiments.append(result)
        self.k_cog_values.append(k_cog)

        return result

    def analyze_conservation(self) -> Dict[str, Any]:
        """Analyze whether k_cog is conserved across conditions."""
        if len(self.k_cog_values) < 2:
            return {"error": "Need at least 2 conditions to test conservation"}

        k_mean = mean(self.k_cog_values)
        k_std = math.sqrt(
            sum((k - k_mean) ** 2 for k in self.k_cog_values) / len(self.k_cog_values)
        )
        k_cv = (k_std / k_mean) if k_mean != 0 else 0  # Coefficient of variation

        # Conservation is validated if CV < 0.15 (within 15% variation)
        is_conserved = k_cv < 0.15

        analysis = {
            "hypothesis": "λ·ΔH_crit = k_cog (constant)",
            "n_conditions": len(self.k_cog_values),
            "k_cog_values": [round(k, 6) for k in self.k_cog_values],
            "statistics": {
                "mean": round(k_mean, 6),
                "std_dev": round(k_std, 6),
                "coefficient_of_variation": round(k_cv, 4),
                "min": round(min(self.k_cog_values), 6),
                "max": round(max(self.k_cog_values), 6),
                "range": round(max(self.k_cog_values) - min(self.k_cog_values), 6)
            },
            "conservation_validated": is_conserved,
            "confidence": "HIGH" if k_cv < 0.10 else "MODERATE" if k_cv < 0.15 else "LOW",
            "interpretation": self._interpret_conservation(is_conserved, k_cv, k_mean)
        }

        return analysis

    def _interpret_conservation(self, is_conserved: bool, cv: float, k_mean: float) -> str:
        """Generate interpretation of conservation results."""
        if is_conserved:
            return (
                f"CONSERVATION LAW VALIDATED: k_cog = {k_mean:.6f} ± {cv*100:.1f}% "
                f"across memory regimes. Cognitive capacity is conserved — systems with "
                f"longer memory require proportionally less novelty to escape basins. "
                f"This is the first empirically validated conservation law of intelligence, "
                f"analogous to energy conservation in physics. k_cog defines the 'metabolic "
                f"efficiency of thought' — the fundamental constant governing how cognition "
                f"transforms between memory and curiosity gradients."
            )
        else:
            return (
                f"Conservation not validated (CV={cv*100:.1f}% > 15% threshold). "
                f"k_cog varies significantly across conditions. Either: (1) λ and ΔH_crit "
                f"do not trade off linearly, (2) measurement error dominates, or (3) the "
                f"hypothesis requires refinement. Further experiments needed."
            )

    def run_full_experiment(self) -> Dict[str, Any]:
        """Run complete conservation law experiment."""
        print("\n" + "="*70)
        print("CONSERVATION LAW EXPERIMENT: k_cog = λ·ΔH_crit")
        print("="*70)
        print("\nHypothesis: The product of memory decay rate and critical")
        print("curiosity dose remains constant across memory regimes.")
        print("\nThis would constitute the first conservation law of intelligence.")
        print("="*70)

        # Condition 1: Baseline (natural decay)
        self.run_condition("baseline", decay_modifier=1.0)

        # Condition 2: Slow decay (longer memory)
        self.run_condition("slow_decay", decay_modifier=0.5)

        # Condition 3: Fast decay (shorter memory)
        self.run_condition("fast_decay", decay_modifier=2.0)

        # Analyze conservation
        print("\n" + "="*70)
        print("CONSERVATION ANALYSIS")
        print("="*70)
        print()

        analysis = self.analyze_conservation()

        print(f"Hypothesis: {analysis['hypothesis']}")
        print(f"Conditions tested: {analysis['n_conditions']}")
        print()
        print(f"k_cog values:")
        for i, (exp, k_val) in enumerate(zip(self.experiments, analysis['k_cog_values']), 1):
            print(f"  {i}. {exp['condition']:15s}: k_cog = {k_val:.6f}")
        print()
        print(f"Statistics:")
        print(f"  Mean:      {analysis['statistics']['mean']:.6f}")
        print(f"  Std Dev:   {analysis['statistics']['std_dev']:.6f}")
        print(f"  CV:        {analysis['statistics']['coefficient_of_variation']:.4f} ({analysis['statistics']['coefficient_of_variation']*100:.1f}%)")
        print(f"  Range:     {analysis['statistics']['range']:.6f}")
        print()
        print(f"Conservation: {'✓ VALIDATED' if analysis['conservation_validated'] else '✗ NOT VALIDATED'}")
        print(f"Confidence:   {analysis['confidence']}")
        print()
        print("Interpretation:")
        print(f"  {analysis['interpretation']}")
        print()

        # Compile full results
        results = {
            "experiment_type": "conservation_law",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hypothesis": "λ·ΔH_crit = k_cog (constant)",
            "conditions": self.experiments,
            "analysis": analysis,
            "conclusion": "VALIDATED" if analysis['conservation_validated'] else "NOT_VALIDATED"
        }

        # Save results
        results_path = PHYSICS_DIR / f"conservation_law_experiment_{int(datetime.now().timestamp())}.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        print("="*70)
        print(f"Results saved: {results_path}")
        print("="*70)
        print()

        # Emit to mycelial bus
        if BUS_AVAILABLE:
            try:
                asyncio.run(emit_experiment_result(
                    experiment_type="conservation_law",
                    conclusion=results["conclusion"],
                    analysis=analysis
                ))
                print("[BUS] Experiment result emitted to mycelial network")
            except Exception as e:
                print(f"[BUS] Warning: Could not emit to bus: {e}")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Conservation Law Experiment")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run full conservation law experiment"
    )

    args = parser.parse_args()

    experiment = ConservationLawExperiment()

    if args.run:
        experiment.run_full_experiment()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
