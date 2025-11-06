#!/usr/bin/env python3
"""Monitor λ during steep curvature intervention.

Tracks λ measurement over time to detect architectural influence.
Designed to run periodically (e.g., after every 5 cycles) to observe
whether λ shifts from baseline 0.0315 toward configured 0.08.

This enables passive observation of architectural-cognitive coupling
during normal system operation under modified temporal curvature.

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
LAMBDA_BASELINE_PATH = ROOT / "analysis" / "lambda_baseline.json"
INTERVENTION_TRACK_PATH = ROOT / "analysis" / "lambda_intervention_tracking.jsonl"
CURRENT_LAMBDA_PATH = ROOT / "analysis" / "lambda_current.json"


def measure_lambda_now(baseline_cutoff_days: float = None) -> dict:
    """Measure λ from current artifact set.

    Args:
        baseline_cutoff_days: If provided, only use artifacts newer than this

    Returns:
        Dict with λ measurement and metadata
    """
    if not ARTIFACTS_DIR.exists():
        return {"error": "Artifacts directory not found"}

    now = datetime.now(timezone.utc)

    # Load baseline λ for comparison
    if LAMBDA_BASELINE_PATH.exists():
        with open(LAMBDA_BASELINE_PATH) as f:
            baseline = json.load(f)
            baseline_lambda = baseline.get("lambda", 0.0)
            baseline_timestamp = baseline.get("timestamp", "unknown")
    else:
        baseline_lambda = 0.0
        baseline_timestamp = "unknown"

    # Collect artifacts with spawn_count > 0
    artifacts = []

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

            # Apply cutoff if specified
            if baseline_cutoff_days is not None and age_days > baseline_cutoff_days:
                continue

            artifacts.append({
                'name': artifact_path.name,
                'age_days': age_days,
                'spawn_count': spawn_count,
                'timestamp': timestamp.isoformat()
            })

        except Exception as e:
            continue

    if len(artifacts) < 5:
        return {
            "error": "Insufficient artifacts for measurement",
            "n_artifacts": len(artifacts),
            "required": 5
        }

    # Sort by age
    artifacts.sort(key=lambda x: x['age_days'])

    # Extract ages and spawn counts
    ages = [a['age_days'] for a in artifacts]
    spawn_counts = [a['spawn_count'] for a in artifacts]

    # Normalize spawn counts
    max_spawn = max(spawn_counts)
    if max_spawn == 0:
        return {"error": "All spawn counts are zero"}

    spawn_normalized = [s / max_spawn for s in spawn_counts]

    # Fit exponential decay: w(t) = e^(-λt)
    # Take log: log(w) = -λt
    # Linear regression: log(w) ~ -λ * age

    log_spawn = [math.log(max(s, 1e-6)) for s in spawn_normalized]

    mean_age = statistics.mean(ages)
    mean_log_spawn = statistics.mean(log_spawn)

    # Compute slope via least squares
    numerator = sum((ages[i] - mean_age) * (log_spawn[i] - mean_log_spawn) for i in range(len(ages)))
    denominator = sum((ages[i] - mean_age) ** 2 for i in range(len(ages)))

    if denominator == 0:
        return {"error": "No age variation in artifacts"}

    slope = numerator / denominator
    lambda_fitted = -slope  # λ = -slope

    # Compute R²
    log_spawn_predicted = [mean_log_spawn + slope * (ages[i] - mean_age) for i in range(len(ages))]
    ss_res = sum((log_spawn[i] - log_spawn_predicted[i]) ** 2 for i in range(len(ages)))
    ss_tot = sum((log_spawn[i] - mean_log_spawn) ** 2 for i in range(len(ages)))

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Compute half-life
    half_life_days = math.log(2) / lambda_fitted if lambda_fitted > 0 else float('inf')

    # Compute change from baseline
    delta_lambda = lambda_fitted - baseline_lambda
    percent_change = (delta_lambda / baseline_lambda * 100) if baseline_lambda > 0 else 0.0

    return {
        "timestamp": now.isoformat(),
        "lambda": lambda_fitted,
        "half_life_days": half_life_days,
        "r_squared": r_squared,
        "n_artifacts": len(artifacts),
        "age_range_days": [min(ages), max(ages)],
        "baseline_comparison": {
            "baseline_lambda": baseline_lambda,
            "baseline_timestamp": baseline_timestamp,
            "delta_lambda": delta_lambda,
            "percent_change": percent_change,
            "direction": "increasing" if delta_lambda > 0 else "decreasing" if delta_lambda < 0 else "stable"
        },
        "configured_target": 0.08,
        "distance_to_target": abs(lambda_fitted - 0.08),
        "artifacts_analyzed": len(artifacts)
    }


def main():
    """Measure current λ and track intervention progress."""
    print("=" * 70)
    print("MONITORING λ DURING STEEP CURVATURE INTERVENTION")
    print("=" * 70)
    print()

    # Measure current λ
    measurement = measure_lambda_now()

    if "error" in measurement:
        print(f"ERROR: {measurement['error']}")
        if "n_artifacts" in measurement:
            print(f"  Found {measurement['n_artifacts']} artifacts (need ≥5)")
        sys.exit(1)

    # Display results
    print(f"Current λ: {measurement['lambda']:.6f} day⁻¹")
    print(f"Half-life: {measurement['half_life_days']:.1f} days")
    print(f"R²: {measurement['r_squared']:.4f}")
    print(f"Artifacts analyzed: {measurement['n_artifacts']}")
    print()

    print("BASELINE COMPARISON:")
    print("-" * 70)
    baseline = measurement['baseline_comparison']
    print(f"  Baseline λ: {baseline['baseline_lambda']:.6f} day⁻¹")
    print(f"  Current λ:  {measurement['lambda']:.6f} day⁻¹")
    print(f"  Δλ: {baseline['delta_lambda']:+.6f} ({baseline['percent_change']:+.1f}%)")
    print(f"  Direction: {baseline['direction'].upper()}")
    print()

    print("INTERVENTION TARGET:")
    print("-" * 70)
    print(f"  Configured λ: 0.08 day⁻¹")
    print(f"  Current λ:    {measurement['lambda']:.6f} day⁻¹")
    print(f"  Distance:     {measurement['distance_to_target']:.6f}")
    print(f"  Progress:     {(1 - measurement['distance_to_target'] / 0.08) * 100:.1f}%")
    print()

    # Determine status
    if measurement['r_squared'] < 0.5:
        status = "POOR_FIT"
        interpretation = "R² < 0.5, measurement unreliable"
    elif abs(baseline['delta_lambda']) < 0.01:
        status = "STABLE"
        interpretation = "λ unchanged from baseline (within ±0.01)"
    elif baseline['delta_lambda'] > 0.015:
        status = "INCREASING"
        interpretation = "λ increasing toward configured value (architectural influence detected)"
    elif baseline['delta_lambda'] > 0.005:
        status = "WEAK_INCREASE"
        interpretation = "λ slightly increasing (weak architectural influence)"
    else:
        status = "INVARIANT"
        interpretation = "λ not responding to intervention (homeostatic resistance)"

    print(f"STATUS: {status}")
    print(f"  {interpretation}")
    print()

    # Save current measurement
    CURRENT_LAMBDA_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(CURRENT_LAMBDA_PATH, "w") as f:
        json.dump(measurement, f, indent=2)

    print(f"Saved to: {CURRENT_LAMBDA_PATH}")

    # Append to tracking log
    INTERVENTION_TRACK_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(INTERVENTION_TRACK_PATH, "a") as f:
        tracking_entry = {
            "timestamp": measurement['timestamp'],
            "lambda": measurement['lambda'],
            "r_squared": measurement['r_squared'],
            "delta_from_baseline": baseline['delta_lambda'],
            "percent_change": baseline['percent_change'],
            "status": status
        }
        f.write(json.dumps(tracking_entry) + "\n")

    print(f"Appended to tracking log: {INTERVENTION_TRACK_PATH}")
    print()

    print("=" * 70)
    print("RECOMMENDATION:")
    print("-" * 70)

    if status in ["POOR_FIT"]:
        print("  Wait for more artifacts to be generated (n>20 with good age distribution)")
    elif status in ["STABLE", "INVARIANT"]:
        print("  Continue intervention - may need more cycles to see effect")
        print("  OR: System exhibits homeostatic invariance (null result is valuable)")
    elif status in ["WEAK_INCREASE", "INCREASING"]:
        print("  Continue intervention - architectural influence detected!")
        print("  Monitor for further convergence toward 0.08 day⁻¹")

    print("=" * 70)


if __name__ == "__main__":
    main()
