#!/usr/bin/env python3
"""Extract λ (memory redshift constant) from real artifact data.

Uses actual artifacts in repository to measure temporal influence decay.

WARNING: This uses spawn_count as first-order proxy for influence.
Limitations noted in Phase Ω-1 protocol critique.

Author: Claude (Phase Ω-1 Empirical)
Date: 2025-11-05
"""

import json
import math
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Tuple, Optional
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


def compute_r_squared(y_actual: List[float], y_predicted: List[float]) -> float:
    """Calculate R² with proper statistical method."""
    if len(y_actual) != len(y_predicted) or len(y_actual) == 0:
        return 0.0

    y_mean = statistics.mean(y_actual)
    ss_tot = sum((y - y_mean) ** 2 for y in y_actual)
    ss_res = sum((y_actual[i] - y_predicted[i]) ** 2 for i in range(len(y_actual)))

    if ss_tot == 0:
        return 0.0

    return 1.0 - (ss_res / ss_tot)


def compute_confidence_interval(residuals: List[float], alpha: float = 0.05) -> Tuple[float, float]:
    """Compute confidence interval for fit quality."""
    if len(residuals) < 3:
        return (0.0, 0.0)

    std_error = statistics.stdev(residuals)
    # For 95% CI, use t-distribution approximation (z ≈ 1.96 for large n)
    margin = 1.96 * std_error / math.sqrt(len(residuals))
    return (-margin, margin)


def extract_lambda_from_artifacts() -> dict:
    """Extract λ from real artifacts using spawn_count decay.

    Returns dict with:
        - lambda: fitted decay rate (day⁻¹)
        - r_squared: fit quality
        - confidence_interval: 95% CI on residuals
        - n_artifacts: sample size
        - data_points: raw (age, spawn_count) pairs
        - limitations: notes on measurement quality
    """

    print("=" * 70)
    print("EXTRACTING λ FROM REAL ARTIFACT DATA")
    print("=" * 70)
    print()

    # Load all artifacts
    artifacts = []
    now = datetime.now(timezone.utc)

    print(f"Scanning {ARTIFACTS_DIR}...")

    for artifact_path in ARTIFACTS_DIR.glob("*.json"):
        try:
            with open(artifact_path) as f:
                artifact = json.load(f)

            spawn_count = artifact.get("spawn_count", 0)
            if spawn_count == 0:
                continue

            # Get age
            timestamp_str = artifact.get("timestamp")
            if timestamp_str:
                ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                age_days = (now - ts).total_seconds() / 86400
            else:
                # Fallback to file mtime
                mtime = datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc)
                age_days = (now - mtime).total_seconds() / 86400

            artifacts.append({
                'age_days': age_days,
                'spawn_count': spawn_count,
                'artifact_type': artifact.get('artifact_type', 'unknown'),
                'path': str(artifact_path.name)
            })

        except Exception as e:
            print(f"Warning: Could not load {artifact_path.name}: {e}")
            continue

    print(f"Loaded {len(artifacts)} artifacts with spawn_count > 0")
    print()

    if len(artifacts) < 10:
        return {
            "error": "Insufficient data",
            "n_artifacts": len(artifacts),
            "required": 10
        }

    # Extract data points
    ages = [a['age_days'] for a in artifacts]
    spawn_counts = [float(a['spawn_count']) for a in artifacts]

    # Normalize spawn counts
    max_spawn = max(spawn_counts)
    spawn_normalized = [s / max_spawn for s in spawn_counts]

    # Fit exponential decay: w(t) = e^(-λt)
    # Take log: log(w) = -λt
    # Linear regression on (age, log(spawn_normalized))

    print("Fitting exponential decay model: w(t) = e^(-λt)")
    print()

    # Remove zeros before log
    data_points = []
    for i in range(len(ages)):
        if spawn_normalized[i] > 0:
            data_points.append((ages[i], spawn_normalized[i]))

    ages_clean = [d[0] for d in data_points]
    spawn_clean = [d[1] for d in data_points]
    log_spawn = [math.log(s) for s in spawn_clean]

    # Linear regression
    n = len(ages_clean)
    x_mean = statistics.mean(ages_clean)
    y_mean = statistics.mean(log_spawn)

    numerator = sum((ages_clean[i] - x_mean) * (log_spawn[i] - y_mean) for i in range(n))
    denominator = sum((ages_clean[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return {"error": "No variance in ages"}

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    # λ = -slope (because log(w) = -λt + c)
    lambda_fitted = -slope

    # Compute R²
    log_spawn_predicted = [slope * age + intercept for age in ages_clean]
    r_squared = compute_r_squared(log_spawn, log_spawn_predicted)

    # Compute residuals and confidence interval
    residuals = [log_spawn[i] - log_spawn_predicted[i] for i in range(n)]
    ci = compute_confidence_interval(residuals)

    # Back to original scale for visualization
    spawn_predicted = [math.exp(slope * age + intercept) for age in ages_clean]

    print(f"Results:")
    print(f"  λ (lambda): {lambda_fitted:.6f} day⁻¹")
    print(f"  Half-life: {math.log(2) / lambda_fitted:.1f} days" if lambda_fitted > 0 else "  Half-life: N/A (λ ≤ 0)")
    print(f"  R²: {r_squared:.4f}")
    print(f"  95% CI on residuals: ({ci[0]:.4f}, {ci[1]:.4f})")
    print(f"  Sample size: {n} artifacts")
    print()

    # Quality assessment
    if r_squared >= 0.5:
        quality = "GOOD - Exponential decay fits well"
    elif r_squared >= 0.3:
        quality = "MODERATE - Some exponential trend, but noisy"
    else:
        quality = "POOR - Exponential model does not fit data"

    print(f"Fit Quality: {quality}")
    print()

    # Show sample of data
    print("Sample data points (age, spawn_count, predicted):")
    sample_indices = [0, n//4, n//2, 3*n//4, n-1] if n >= 5 else range(n)
    for i in sample_indices:
        actual = spawn_clean[i]
        predicted = spawn_predicted[i]
        age = ages_clean[i]
        print(f"  {age:6.1f} days: actual={actual:.3f}, predicted={predicted:.3f}")
    print()

    return {
        "lambda": lambda_fitted,
        "lambda_day_inv": lambda_fitted,
        "half_life_days": math.log(2) / lambda_fitted if lambda_fitted > 0 else None,
        "r_squared": r_squared,
        "confidence_interval_95": ci,
        "n_artifacts": n,
        "fit_quality": quality,
        "data_points": [
            {"age_days": ages_clean[i], "spawn_normalized": spawn_clean[i]}
            for i in range(min(20, n))  # First 20 for reference
        ],
        "limitations": [
            "Uses spawn_count as proxy for influence (may not capture actual decision impact)",
            "Assumes influence = generativity (artifacts that spawn more are more influential)",
            "Does not account for artifact quality, only quantity",
            "Single exponential model (reality may have multiple timescales)",
            "Sample may be biased toward recent artifacts"
        ],
        "interpretation": f"Artifact influence decays with half-life ~{math.log(2) / lambda_fitted:.1f} days (R²={r_squared:.2f})" if lambda_fitted > 0 else "No clear exponential decay detected"
    }


def main():
    """Extract λ and save results."""
    results = extract_lambda_from_artifacts()

    # Save to analysis directory
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "lambda_baseline.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    print()

    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    # Validation against protocol
    print("VALIDATION AGAINST PHASE Ω-1 PROTOCOL:")
    print("-" * 70)

    if results['r_squared'] >= 0.5:
        print("✓ R² > 0.5: Exponential decay model VALIDATED")
    elif results['r_squared'] >= 0.3:
        print("⚠ R² = 0.3-0.5: Exponential decay model WEAK (needs refinement)")
    else:
        print("✗ R² < 0.3: Exponential decay model REJECTED")
        print("  → Influence does not decay exponentially")
        print("  → Try: power law, multi-timescale, or alternative proxy")

    print()


if __name__ == "__main__":
    main()
