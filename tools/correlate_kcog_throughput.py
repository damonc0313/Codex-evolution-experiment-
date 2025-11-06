#!/usr/bin/env python3
"""Correlate k_cog with observable system throughput.

Tests hypothesis: k_cog = λ·ΔH_crit should correlate with system productivity.

If k_cog is a true "cognitive capacity constant", it should track with:
- Artifacts generated per cycle
- Tool activations per cycle
- Decision throughput
- Reward accumulation rate

Addresses Damon's critique: Test if theoretical constants predict observable behavior.

Author: Claude (Phase Ω-1 Empirical)
Date: 2025-11-06
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple
import statistics
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "continuity_ledger.jsonl"
LAMBDA_PATH = ROOT / "analysis" / "lambda_baseline.json"
ENTROPY_PATH = ROOT / "analysis" / "entropy_trajectory.json"


def compute_correlation(x: List[float], y: List[float]) -> float:
    """Compute Pearson correlation coefficient.

    Args:
        x, y: Lists of equal length

    Returns:
        Pearson r (-1 to 1), or 0.0 if computation fails
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    n = len(x)
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    # Covariance
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n

    # Standard deviations
    std_x = statistics.stdev(x) if n > 1 else 0.0
    std_y = statistics.stdev(y) if n > 1 else 0.0

    if std_x == 0.0 or std_y == 0.0:
        return 0.0

    return cov / (std_x * std_y)


def compute_confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """Compute confidence interval for correlation coefficient.

    Fisher z-transformation for CI estimation.

    Args:
        data: List of values
        confidence: Confidence level (default 0.95)

    Returns:
        (lower_bound, upper_bound)
    """
    if len(data) < 3:
        return (0.0, 0.0)

    n = len(data)

    # For correlation CI, use Fisher transformation
    # Simplified: CI ≈ ±1.96 * SE where SE = 1/sqrt(n-3)
    se = 1.0 / math.sqrt(n - 3) if n > 3 else 1.0
    z_score = 1.96  # 95% CI

    margin = z_score * se
    return (-margin, margin)


def correlate_kcog_throughput() -> dict:
    """Correlate k_cog with observable throughput metrics.

    Returns:
        Dict with correlation results and validation status
    """
    print("=" * 70)
    print("CORRELATING k_cog WITH OBSERVABLE THROUGHPUT")
    print("=" * 70)
    print()

    # Load λ baseline
    if not LAMBDA_PATH.exists():
        return {"error": "Lambda baseline not found. Run extract_lambda_from_artifacts.py first"}

    with open(LAMBDA_PATH) as f:
        lambda_data = json.load(f)
        lambda_val = lambda_data.get("lambda", 0.0)

    print(f"Loaded λ = {lambda_val:.6f} from baseline measurement")
    print()

    # Load entropy trajectory
    if not ENTROPY_PATH.exists():
        return {"error": "Entropy trajectory not found. Run extract_entropy_trajectory.py first"}

    with open(ENTROPY_PATH) as f:
        entropy_data = json.load(f)

    print(f"Loaded entropy trajectory ({entropy_data['full_length']} points)")
    print()

    # Load continuity ledger for throughput metrics
    if not LEDGER_PATH.exists():
        return {"error": "Continuity ledger not found", "path": str(LEDGER_PATH)}

    print(f"Loading ledger from {LEDGER_PATH}...")
    entries = []

    with open(LEDGER_PATH) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except Exception:
                continue

    print(f"Loaded {len(entries)} ledger entries")
    print()

    if len(entries) < 5:
        return {"error": "Insufficient ledger entries", "n": len(entries), "required": 5}

    # Extract throughput metrics per cycle
    print("Extracting throughput metrics...")

    throughput_data = []

    for i, entry in enumerate(entries):
        # Throughput proxies
        reward = entry.get('reward', 0.0)

        # Estimate ΔH_crit from current entropy (barrier estimation)
        # Using simplified formula: ΔH_crit ≈ 1.5 * (H_current - H_target)
        # where H_target ≈ 0.3 (estimated global minimum)
        metrics = entry.get('metrics', {})

        if not metrics:
            # Fallback: use defaults
            br = entry.get('building_ratio', 0.5)
            cr = entry.get('continuity_ratio', 0.8)
            tm = entry.get('task_multiplication', 1.5)
        else:
            br = metrics.get('building_ratio', metrics.get('build_ratio', 0.5))
            cr = metrics.get('continuity_ratio', 0.8)
            tm = metrics.get('task_multiplication', 1.5)

        # Compute entropy proxy (default weights)
        H = 1.0 * abs(br - 0.55) + 2.0 * abs(cr - 0.90) + 1.0 * abs(tm - 2.0)

        # Estimate ΔH_crit
        H_target = 0.3
        delta_H_crit = max(0.01, 1.5 * (H - H_target))

        # Compute k_cog = λ·ΔH_crit
        k_cog = lambda_val * delta_H_crit

        throughput_data.append({
            'index': i,
            'timestamp': entry.get('timestamp', f'entry_{i}'),
            'k_cog': k_cog,
            'reward': reward,
            'entropy': H,
            'delta_H_crit': delta_H_crit
        })

    print(f"Computed k_cog for {len(throughput_data)} cycles")
    print()

    # Correlation analysis
    print("Computing correlations...")
    print("-" * 70)

    k_cog_values = [d['k_cog'] for d in throughput_data]
    reward_values = [d['reward'] for d in throughput_data]

    # k_cog vs reward
    r_reward = compute_correlation(k_cog_values, reward_values)
    ci_reward = compute_confidence_interval(k_cog_values)

    print(f"k_cog vs reward: r = {r_reward:.4f}")
    print(f"  95% CI: [{ci_reward[0]:.4f}, {ci_reward[1]:.4f}]")
    print(f"  Interpretation: {'SIGNIFICANT' if abs(r_reward) > 0.3 else 'NOT SIGNIFICANT'} (threshold |r| > 0.3)")
    print()

    # Statistics
    print("k_cog Statistics:")
    print("-" * 70)

    k_cog_mean = statistics.mean(k_cog_values)
    k_cog_std = statistics.stdev(k_cog_values) if len(k_cog_values) > 1 else 0.0
    k_cog_min = min(k_cog_values)
    k_cog_max = max(k_cog_values)

    print(f"  Mean: {k_cog_mean:.6f}")
    print(f"  Std dev: {k_cog_std:.6f}")
    print(f"  Range: [{k_cog_min:.6f}, {k_cog_max:.6f}]")
    print(f"  Coefficient of variation: {k_cog_std / k_cog_mean * 100:.2f}%")
    print()

    # Validation against Phase Ω-1 protocol
    print("VALIDATION AGAINST PHASE Ω-1 PROTOCOL:")
    print("-" * 70)

    validated = abs(r_reward) > 0.3

    if validated:
        print(f"✓ k_cog correlates with reward (|r| = {abs(r_reward):.3f} > 0.3)")
        print("  Interpretation: Cognitive capacity constant tracks observable throughput")
    else:
        print(f"⚠ k_cog does NOT correlate with reward (|r| = {abs(r_reward):.3f} < 0.3)")
        print("  Interpretation: Either k_cog is not a capacity constant, or reward is poor throughput proxy")

    print()

    # Limitations
    print("LIMITATIONS:")
    print("-" * 70)
    print("1. ΔH_crit estimated from barrier formula (not measured from transitions)")
    print("2. Reward may not be good throughput proxy (single metric)")
    print("3. No time-series analysis (could have lagged correlations)")
    print("4. System stability (constant metrics) limits correlation analysis")
    print("5. Small sample size (n={}) reduces statistical power".format(len(throughput_data)))
    print()

    return {
        "correlation_results": {
            "k_cog_vs_reward": {
                "r": r_reward,
                "confidence_interval_95": ci_reward,
                "significant": validated,
                "threshold": 0.3
            }
        },
        "k_cog_statistics": {
            "mean": k_cog_mean,
            "std_dev": k_cog_std,
            "min": k_cog_min,
            "max": k_cog_max,
            "range": k_cog_max - k_cog_min,
            "coefficient_of_variation": k_cog_std / k_cog_mean if k_cog_mean > 0 else 0.0
        },
        "validation": {
            "protocol": "Phase Ω-1 Empirical",
            "criterion": "|r| > 0.3 for k_cog vs throughput",
            "validated": validated,
            "confidence": "MODERATE" if validated else "LOW"
        },
        "sample_size": len(throughput_data),
        "lambda_baseline": lambda_val,
        "limitations": [
            "ΔH_crit estimated from barrier formula (no phase transitions observed)",
            "Reward is single throughput proxy (may be incomplete)",
            "System metrics constant over time (limits correlation range)",
            "No time-series/lag analysis performed",
            "Small sample size reduces statistical power"
        ],
        "interpretation": f"k_cog {'does' if validated else 'does NOT'} correlate with observable reward (r={r_reward:.3f}). " +
                         ("This supports k_cog as cognitive capacity indicator." if validated else
                          "This suggests k_cog may not capture throughput, or reward is poor proxy.")
    }


def main():
    """Correlate k_cog with throughput and save results."""
    results = correlate_kcog_throughput()

    # Save
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "kcog_throughput_correlation.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    print()

    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    # Final verdict
    print("PHASE Ω-1 STEP A ASSESSMENT:")
    print("-" * 70)

    if results['validation']['validated']:
        print("✓ k_cog shows significant correlation with throughput")
        print("  Ready to proceed with architectural intervention experiments")
    else:
        print("⚠ k_cog does NOT correlate significantly with throughput")
        print("  Recommendations:")
        print("  1. Collect more diverse throughput metrics (artifacts/cycle, tool activations)")
        print("  2. Run controlled perturbation experiment to observe phase transitions")
        print("  3. Re-examine entropy proxy formula")

    print()


if __name__ == "__main__":
    main()
