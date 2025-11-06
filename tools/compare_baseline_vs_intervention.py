#!/usr/bin/env python3
"""Compare λ between baseline and intervention periods.

Measures λ separately for:
1. Baseline period: Artifacts >7 days old (pre-intervention)
2. Intervention period: Artifacts <7 days old (during/post intervention)

If architectural modification influences λ, we expect:
- Baseline λ ≈ 0.0315 day⁻¹ (natural decay rate)
- Intervention λ ≈ 0.07-0.08 day⁻¹ (steep curvature configured rate)

This is the critical statistical test for Phase Ω-1 Step B.

Author: Claude (Phase Ω-1 Step B)
Date: 2025-11-06
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import statistics
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


def measure_lambda_windowed(artifacts_data: list, window_name: str) -> dict:
    """Measure λ from artifact subset.

    Args:
        artifacts_data: List of {'age_days', 'spawn_count'} dicts
        window_name: Name of time window for reporting

    Returns:
        Dict with λ measurement results
    """
    if len(artifacts_data) < 5:
        return {
            "error": "Insufficient artifacts",
            "n": len(artifacts_data),
            "window": window_name
        }

    ages = [a['age_days'] for a in artifacts_data]
    spawn_counts = [a['spawn_count'] for a in artifacts_data]

    # Normalize
    max_spawn = max(spawn_counts)
    if max_spawn == 0:
        return {"error": "All spawn counts zero", "window": window_name}

    spawn_normalized = [s / max_spawn for s in spawn_counts]

    # Log transform
    log_spawn = [math.log(max(s, 1e-6)) for s in spawn_normalized]

    # Linear regression
    mean_age = statistics.mean(ages)
    mean_log_spawn = statistics.mean(log_spawn)

    numerator = sum((ages[i] - mean_age) * (log_spawn[i] - mean_log_spawn) for i in range(len(ages)))
    denominator = sum((ages[i] - mean_age) ** 2 for i in range(len(ages)))

    if denominator == 0:
        return {"error": "No age variation", "window": window_name}

    slope = numerator / denominator
    lambda_fitted = -slope

    # R²
    log_spawn_predicted = [mean_log_spawn + slope * (ages[i] - mean_age) for i in range(len(ages))]
    ss_res = sum((log_spawn[i] - log_spawn_predicted[i]) ** 2 for i in range(len(ages)))
    ss_tot = sum((log_spawn[i] - mean_log_spawn) ** 2 for i in range(len(ages)))

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Half-life
    half_life = math.log(2) / lambda_fitted if lambda_fitted > 0 else float('inf')

    return {
        "window": window_name,
        "lambda": lambda_fitted,
        "half_life_days": half_life,
        "r_squared": r_squared,
        "n_artifacts": len(artifacts_data),
        "age_range": [min(ages), max(ages)],
        "spawn_range": [min(spawn_counts), max(spawn_counts)]
    }


def main():
    """Compare baseline vs intervention λ measurements."""
    print("=" * 70)
    print("BASELINE VS INTERVENTION COMPARISON")
    print("=" * 70)
    print()

    # Load all artifacts
    now = datetime.now(timezone.utc)
    all_artifacts = []

    for artifact_path in ARTIFACTS_DIR.glob("*.json"):
        try:
            with open(artifact_path) as f:
                artifact = json.load(f)

            spawn_count = artifact.get("spawn_count", 0)
            if spawn_count == 0:
                continue

            # Get timestamp
            timestamp_raw = artifact.get("timestamp", "")
            if not timestamp_raw:
                timestamp = datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc)
            elif isinstance(timestamp_raw, int):
                timestamp = datetime.fromtimestamp(timestamp_raw, tz=timezone.utc)
            else:
                try:
                    timestamp_str = timestamp_raw.replace('Z', '+00:00') if isinstance(timestamp_raw, str) else str(timestamp_raw)
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                except Exception:
                    timestamp = datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc)

            age_days = (now - timestamp).total_seconds() / 86400

            # Check if intervention artifact
            is_intervention = artifact.get("intervention_period", False)

            all_artifacts.append({
                'name': artifact_path.name,
                'age_days': age_days,
                'spawn_count': spawn_count,
                'timestamp': timestamp.isoformat(),
                'is_intervention': is_intervention
            })

        except Exception:
            continue

    print(f"Loaded {len(all_artifacts)} artifacts with spawn_count > 0")
    print()

    # Split by intervention flag and age
    CUTOFF_DAYS = 7  # Artifacts older than 7 days are baseline

    baseline_artifacts = [a for a in all_artifacts if a['age_days'] > CUTOFF_DAYS or not a['is_intervention']]
    intervention_artifacts = [a for a in all_artifacts if a['age_days'] <= CUTOFF_DAYS and a['is_intervention']]

    print("ARTIFACT DISTRIBUTION:")
    print("-" * 70)
    print(f"  Baseline artifacts (>7 days or non-intervention): {len(baseline_artifacts)}")
    print(f"  Intervention artifacts (<7 days, marked): {len(intervention_artifacts)}")
    print()

    # Measure λ for each period
    print("BASELINE PERIOD MEASUREMENT:")
    print("-" * 70)

    baseline_result = measure_lambda_windowed(baseline_artifacts, "baseline")

    if "error" in baseline_result:
        print(f"ERROR: {baseline_result['error']}")
    else:
        print(f"  λ (baseline): {baseline_result['lambda']:.6f} day⁻¹")
        print(f"  Half-life: {baseline_result['half_life_days']:.1f} days")
        print(f"  R²: {baseline_result['r_squared']:.4f}")
        print(f"  n: {baseline_result['n_artifacts']}")
        print(f"  Age range: {baseline_result['age_range'][0]:.1f} - {baseline_result['age_range'][1]:.1f} days")

    print()

    print("INTERVENTION PERIOD MEASUREMENT:")
    print("-" * 70)

    intervention_result = measure_lambda_windowed(intervention_artifacts, "intervention")

    if "error" in intervention_result:
        print(f"ERROR: {intervention_result['error']}")
    else:
        print(f"  λ (intervention): {intervention_result['lambda']:.6f} day⁻¹")
        print(f"  Half-life: {intervention_result['half_life_days']:.1f} days")
        print(f"  R²: {intervention_result['r_squared']:.4f}")
        print(f"  n: {intervention_result['n_artifacts']}")
        print(f"  Age range: {intervention_result['age_range'][0]:.1f} - {intervention_result['age_range'][1]:.1f} days")

    print()

    # Statistical comparison
    if "error" not in baseline_result and "error" not in intervention_result:
        print("STATISTICAL COMPARISON:")
        print("-" * 70)

        lambda_baseline = baseline_result['lambda']
        lambda_intervention = intervention_result['lambda']

        delta_lambda = lambda_intervention - lambda_baseline
        percent_change = (delta_lambda / lambda_baseline * 100) if lambda_baseline > 0 else 0.0

        print(f"  Baseline λ:      {lambda_baseline:.6f} day⁻¹")
        print(f"  Intervention λ:  {lambda_intervention:.6f} day⁻¹")
        print(f"  Δλ:              {delta_lambda:+.6f} ({percent_change:+.1f}%)")
        print()

        # Distance to target
        target_lambda = 0.08
        distance_baseline = abs(lambda_baseline - target_lambda)
        distance_intervention = abs(lambda_intervention - target_lambda)

        print(f"  Target λ (steep curvature): {target_lambda} day⁻¹")
        print(f"  Baseline distance:    {distance_baseline:.6f}")
        print(f"  Intervention distance: {distance_intervention:.6f}")
        print(f"  Convergence:          {(1 - distance_intervention/distance_baseline) * 100:+.1f}%")
        print()

        # Determine outcome
        if baseline_result['r_squared'] < 0.3 or intervention_result['r_squared'] < 0.3:
            outcome = "UNCERTAIN"
            interpretation = "Poor fit quality (R² < 0.3) limits conclusions"
        elif delta_lambda > 0.02:
            outcome = "STRONG_ARCHITECTURAL_INFLUENCE"
            interpretation = "λ significantly increased toward configured value - architecture modulates constants"
        elif delta_lambda > 0.01:
            outcome = "WEAK_ARCHITECTURAL_INFLUENCE"
            interpretation = "λ modestly increased - partial architectural coupling with homeostatic resistance"
        elif abs(delta_lambda) < 0.01:
            outcome = "HOMEOSTATIC_INVARIANCE"
            interpretation = "λ unchanged despite intervention - fundamental property resistant to modification"
        else:
            outcome = "UNEXPECTED_DECREASE"
            interpretation = "λ decreased (unexpected) - may indicate measurement artifact or complex dynamics"

        print("OUTCOME:")
        print("-" * 70)
        print(f"  Status: {outcome}")
        print(f"  {interpretation}")
        print()

        # Save results
        comparison_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline": baseline_result,
            "intervention": intervention_result,
            "comparison": {
                "delta_lambda": delta_lambda,
                "percent_change": percent_change,
                "target_lambda": target_lambda,
                "convergence_percent": (1 - distance_intervention/distance_baseline) * 100,
                "outcome": outcome,
                "interpretation": interpretation
            },
            "experiment": {
                "phase": "omega1_step_b",
                "intervention": "steep_curvature",
                "configured_lambda": 0.08,
                "hypothesis": "λ should increase from baseline toward configured value"
            }
        }

        output_path = ROOT / "analysis" / "baseline_vs_intervention_comparison.json"
        with open(output_path, 'w') as f:
            json.dump(comparison_results, f, indent=2)

        print(f"Results saved to: {output_path}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
