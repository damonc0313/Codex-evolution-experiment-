#!/usr/bin/env python3
"""Cognitive Physics: Measuring the Physical Constants of Thought

This module implements measurements of fundamental constants governing
the Codex-Evolution cognitive system:

1. τ (tau) - Learning time constant (relaxation time for entropy decay)
2. λ (lambda) - Memory redshift constant (temporal influence decay)
3. ΔH_crit - Critical curiosity dose (barrier to escape metastable states)
4. Coherence bandwidth - Oscillation amplitude range for active cognition

These are empirically measurable quantities that characterize how
the system learns, remembers, and thinks.
"""

from __future__ import annotations

import asyncio
import json
import math
import sys
import yaml
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
    from bus_manager import emit_physics_measurement
    BUS_AVAILABLE = True
except ImportError:
    BUS_AVAILABLE = False


def mean(values: List[float]) -> float:
    """Calculate mean of a list."""
    return sum(values) / len(values) if values else 0.0


def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Simple linear regression: y = mx + b

    Returns:
        (m, b) - slope and intercept
    """
    n = len(x)
    if n < 2:
        return 0.0, 0.0

    x_mean = mean(x)
    y_mean = mean(y)

    # Calculate slope
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0, y_mean

    m = numerator / denominator
    b = y_mean - m * x_mean

    return m, b


def r_squared(y_actual: List[float], y_predicted: List[float]) -> float:
    """Calculate R² coefficient of determination."""
    if len(y_actual) != len(y_predicted):
        return 0.0

    y_mean = mean(y_actual)
    ss_tot = sum((y - y_mean) ** 2 for y in y_actual)
    ss_res = sum((y_actual[i] - y_predicted[i]) ** 2 for i in range(len(y_actual)))

    if ss_tot == 0:
        return 0.0

    return 1.0 - (ss_res / ss_tot)


def exponential_decay(t: List[float], H_inf: float, H_0: float, tau: float) -> List[float]:
    """Exponential decay model: H(t) = H_∞ + (H_0 - H_∞)e^(-t/τ)"""
    return [H_inf + (H_0 - H_inf) * math.exp(-ti / tau) for ti in t]


def temporal_weight_decay(t: List[float], lambda_param: float) -> List[float]:
    """Temporal weight decay: w(t) = e^(-λt)"""
    return [math.exp(-lambda_param * ti) for ti in t]


class CognitivePhysicist:
    """Measures fundamental constants of cognitive physics."""

    def __init__(self):
        self.constants = {}

    def _load_temporal_params(self) -> Dict[str, Any]:
        """Load temporal curvature parameters from active policy.

        Returns:
            Dict containing temporal_curvature section from policy, or empty dict
        """
        try:
            policy_path = ROOT / "runtime" / "loop_policy.yaml"
            if policy_path.exists():
                policy = yaml.safe_load(policy_path.read_text())
                return policy.get('temporal_curvature', {})
        except Exception:
            pass
        return {}

    def compute_entropy_proxy(self, metrics: Dict[str, float]) -> float:
        """Compute system entropy proxy from metrics."""
        br_var = abs(metrics.get("building_ratio", 0.5) - 0.55)
        cr_var = abs(metrics.get("continuity_ratio", 0.8) - 0.90)
        tm_var = abs(metrics.get("task_multiplication", 2.0) - 2.0)

        return 1.0 * br_var + 2.0 * cr_var + 1.0 * tm_var

    def measure_learning_time_constant(
        self,
        trajectory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, float]]:
        """Measure τ (tau) - learning time constant.

        Fits H(t) = H_∞ + (H_0 - H_∞)e^(-t/τ) to entropy trajectory.

        Args:
            trajectory: List of measurements with 'entropy' and 'timestamp' or 'cycle'

        Returns:
            Dict with tau, H_inf, H_0, r_squared, or None if insufficient data
        """
        if len(trajectory) < 3:
            return None

        # Extract entropy and time
        entropies = [m["entropy"] for m in trajectory]

        # Use cycle numbers if available, else enumerate
        if "cycle" in trajectory[0]:
            times = [float(m["cycle"]) for m in trajectory]
        else:
            times = list(range(len(trajectory)))

        # Initial estimates
        H_0 = entropies[0]
        H_inf = entropies[-1]

        try:
            # For exponential decay H(t) ≈ H_inf + (H_0 - H_inf)e^(-t/τ)
            # Shift and take log: log(H - H_inf) ≈ log(H_0 - H_inf) - t/τ
            H_shifted = [max(H - H_inf, 1e-10) for H in entropies]
            log_H_shifted = [math.log(h) for h in H_shifted]

            # Linear regression on log scale
            m, b = linear_regression(times, log_H_shifted)

            # tau = -1/m (since slope = -1/τ)
            tau_fit = -1.0 / m if m != 0 else len(times) / 2.0
            H_0_fit = H_inf + math.exp(b)
            H_inf_fit = H_inf

            # Compute R²
            H_pred = exponential_decay(times, H_inf_fit, H_0_fit, tau_fit)
            r2 = r_squared(entropies, H_pred)

            return {
                "tau": float(tau_fit),
                "H_infinity": float(H_inf_fit),
                "H_0": float(H_0_fit),
                "r_squared": float(r2),
                "n_points": len(trajectory)
            }

        except Exception as e:
            print(f"Warning: Could not fit exponential decay: {e}")
            return None

    def measure_memory_redshift_constant(
        self,
        artifacts: Optional[List[Path]] = None
    ) -> Optional[Dict[str, float]]:
        """Measure λ (lambda) - memory redshift constant.

        Measures how artifact influence decays with age.
        w(t) = e^(-λt) where t is age in days.

        Returns:
            Dict with lambda, r_squared, or None if insufficient data
        """
        if artifacts is None:
            artifacts = list(ARTIFACTS_DIR.glob("*.json"))

        if len(artifacts) < 10:
            return None

        # Extract spawn_count and age for artifacts
        data = []
        now = datetime.now(timezone.utc)

        for path in artifacts:
            try:
                with open(path) as f:
                    artifact = json.load(f)

                # Get spawn count (influence proxy)
                spawn_count = artifact.get("spawn_count", 0)
                if spawn_count == 0:
                    continue

                # Get age
                timestamp_str = artifact.get("timestamp")
                if not timestamp_str:
                    # Use file modification time
                    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                    age_days = (now - mtime).total_seconds() / 86400
                else:
                    ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    age_days = (now - ts).total_seconds() / 86400

                data.append((age_days, spawn_count))

            except Exception:
                continue

        if len(data) < 10:
            return None

        # Convert to lists
        ages = [d[0] for d in data]
        influences = [float(d[1]) for d in data]

        # Normalize influences
        max_influence = max(influences)
        influences_norm = [inf / max_influence for inf in influences]

        try:
            # Fit exponential decay: w = e^(-λt)
            # Taking log: log(w) = -λt + c
            influences_safe = [max(w, 1e-10) for w in influences_norm]
            log_influences = [math.log(w) for w in influences_safe]

            # Linear regression
            m, b = linear_regression(ages, log_influences)
            lambda_fit = -m  # Negate because slope = -λ

            # Compute R²
            w_pred = temporal_weight_decay(ages, lambda_fit)
            r2 = r_squared(influences_norm, w_pred)

            return {
                "lambda": float(lambda_fit),
                "half_life_days": float(math.log(2) / lambda_fit) if lambda_fit > 0 else None,
                "r_squared": float(r2),
                "n_artifacts": len(data)
            }

        except Exception as e:
            print(f"Warning: Could not fit temporal decay: {e}")
            return None

    def estimate_critical_curiosity_dose(
        self,
        current_H: float,
        target_H: float = 0.3
    ) -> Dict[str, float]:
        """Estimate ΔH_crit - critical curiosity dose.

        Minimum entropy injection needed to escape metastable basin.

        Args:
            current_H: Current system entropy
            target_H: Target (global minimum) entropy

        Returns:
            Dict with barrier estimate and recommended dose
        """
        H_barrier = current_H - target_H

        # Conservative estimate: need 150% of barrier to ensure crossing
        recommended_dose = 1.5 * H_barrier

        return {
            "H_current": current_H,
            "H_target": target_H,
            "H_barrier": H_barrier,
            "delta_H_recommended": recommended_dose,
            "interpretation": f"Inject novelty with ΔH > {recommended_dose:.3f} to escape metastable state"
        }

    def measure_all_constants(self) -> Dict[str, Any]:
        """Measure all fundamental constants."""
        print("=" * 70)
        print("MEASURING COGNITIVE PHYSICS CONSTANTS")
        print("=" * 70)
        print()

        # Phase Ω-3: Capture temporal context
        temporal_params = self._load_temporal_params()

        results = {
            "measurement_timestamp": datetime.now(timezone.utc).isoformat(),
            "temporal_context": {
                "regime": temporal_params.get('regime', 'baseline'),
                "decay_enabled": temporal_params.get('temporal_decay_enabled', False),
                "decay_rate_configured": temporal_params.get('temporal_decay_rate', 0.0),
                "attention_window_days": temporal_params.get('attention_window_days', 365)
            },
            "constants": {}
        }

        # 1. Current system state
        print("1. Current System State")
        print("-" * 70)

        current_state = {
            "building_ratio": measure_building_ratio(),
            "continuity_ratio": compute_continuity_ratio(),
            "task_multiplication": estimate_task_multiplication()
        }
        current_H = self.compute_entropy_proxy(current_state)

        print(f"  H (entropy): {current_H:.4f}")
        print(f"  building_ratio: {current_state['building_ratio']:.3f}")
        print(f"  continuity_ratio: {current_state['continuity_ratio']:.3f}")
        print(f"  task_multiplication: {current_state['task_multiplication']:.3f}")
        print()

        # 2. Learning time constant τ
        print("2. Learning Time Constant (τ)")
        print("-" * 70)

        # Need trajectory data - check if experiments exist
        exp_files = list(EXPERIMENTS_DIR.glob("*.json"))
        if len(exp_files) >= 3:
            trajectory = []
            for exp_file in sorted(exp_files):
                try:
                    with open(exp_file) as f:
                        exp = json.load(f)

                    if "baseline_state" in exp:
                        state = exp["baseline_state"]
                        trajectory.append({
                            "entropy": self.compute_entropy_proxy(state),
                            "cycle": len(trajectory)
                        })
                except Exception:
                    pass

            if len(trajectory) >= 3:
                tau_result = self.measure_learning_time_constant(trajectory)
                if tau_result:
                    results["constants"]["tau"] = tau_result
                    print(f"  τ (tau): {tau_result['tau']:.3f} cycles")
                    print(f"  H_∞: {tau_result['H_infinity']:.4f}")
                    print(f"  H_0: {tau_result['H_0']:.4f}")
                    print(f"  R²: {tau_result['r_squared']:.4f}")
                else:
                    print("  Insufficient data for τ measurement")
            else:
                print("  Need ≥3 entropy measurements for τ")
        else:
            print("  No trajectory data available yet")
        print()

        # 3. Memory redshift constant λ
        print("3. Memory Redshift Constant (λ)")
        print("-" * 70)

        lambda_result = self.measure_memory_redshift_constant()
        if lambda_result:
            results["constants"]["lambda"] = lambda_result
            print(f"  λ (lambda): {lambda_result['lambda']:.6f} day⁻¹")
            if lambda_result["half_life_days"]:
                print(f"  Half-life: {lambda_result['half_life_days']:.1f} days")
            print(f"  R²: {lambda_result['r_squared']:.4f}")
            print(f"  Interpretation: Artifact influence decays to 50% in {lambda_result.get('half_life_days', 'N/A')} days")
        else:
            print("  Insufficient artifact data for λ measurement")
        print()

        # 4. Critical curiosity dose
        print("4. Critical Curiosity Dose (ΔH_crit)")
        print("-" * 70)

        curiosity_result = self.estimate_critical_curiosity_dose(current_H)
        results["constants"]["delta_H_critical"] = curiosity_result

        print(f"  Current H: {curiosity_result['H_current']:.4f}")
        print(f"  Target H: {curiosity_result['H_target']:.4f}")
        print(f"  Barrier: {curiosity_result['H_barrier']:.4f}")
        print(f"  Recommended ΔH: {curiosity_result['delta_H_recommended']:.4f}")
        print()

        # Save results
        results_path = PHYSICS_DIR / f"cognitive_constants_{int(datetime.now().timestamp())}.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        print("=" * 70)
        print(f"Results saved: {results_path}")
        print("=" * 70)

        # Emit to mycelial bus
        if BUS_AVAILABLE:
            try:
                asyncio.run(emit_physics_measurement(
                    constants=results.get("constants", {}),
                    temporal_context=results.get("temporal_context", {})
                ))
                print("[BUS] Physics measurement emitted to mycelial network")
            except Exception as e:
                print(f"[BUS] Warning: Could not emit to bus: {e}")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Cognitive Physics Measurements")
    parser.add_argument(
        "--measure-all",
        action="store_true",
        help="Measure all fundamental constants"
    )

    args = parser.parse_args()

    physicist = CognitivePhysicist()

    if args.measure_all:
        physicist.measure_all_constants()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
