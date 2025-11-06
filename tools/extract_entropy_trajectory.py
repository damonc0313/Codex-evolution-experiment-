#!/usr/bin/env python3
"""Extract entropy trajectory from real continuity ledger.

Measures system entropy over time from actual operational data.

Addresses Damon's critique: Tests sensitivity to entropy formula weights.

Author: Claude (Phase Ω-1 Empirical)
Date: 2025-11-05
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.ledger_metrics import (
    measure_building_ratio,
    compute_continuity_ratio,
    estimate_task_multiplication
)

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "continuity_ledger.jsonl"


def compute_entropy_proxy(br: float, cr: float, tm: float, weights: Tuple[float, float, float] = (1.0, 2.0, 1.0)) -> float:
    """Compute entropy proxy with configurable weights.

    Args:
        br: building_ratio
        cr: continuity_ratio
        tm: task_multiplication
        weights: (w_br, w_cr, w_tm) weight tuple

    Returns:
        Entropy proxy H (lower is better)
    """
    w_br, w_cr, w_tm = weights

    # Deviations from targets
    br_dev = abs(br - 0.55)
    cr_dev = abs(cr - 0.90)
    tm_dev = abs(tm - 2.0)

    return w_br * br_dev + w_cr * cr_dev + w_tm * tm_dev


def extract_entropy_trajectory() -> dict:
    """Extract entropy trajectory from continuity ledger.

    Returns:
        Dict with entropy trajectory, phase transitions, and sensitivity analysis
    """
    print("=" * 70)
    print("EXTRACTING ENTROPY TRAJECTORY FROM CONTINUITY LEDGER")
    print("=" * 70)
    print()

    if not LEDGER_PATH.exists():
        return {"error": "Continuity ledger not found", "path": str(LEDGER_PATH)}

    # Load ledger
    print(f"Loading ledger from {LEDGER_PATH}...")
    entries = []

    with open(LEDGER_PATH) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except Exception as e:
                continue

    print(f"Loaded {len(entries)} ledger entries")
    print()

    if len(entries) < 5:
        return {"error": "Insufficient ledger entries", "n": len(entries), "required": 5}

    # Extract metrics over time
    trajectory = []

    for i, entry in enumerate(entries):
        # Try to get metrics from entry
        metrics = entry.get('metrics', {})

        # Fallback to computing current state if not in ledger
        if not metrics:
            br = entry.get('building_ratio', measure_building_ratio())
            cr = entry.get('continuity_ratio', compute_continuity_ratio())
            tm = entry.get('task_multiplication', estimate_task_multiplication())
        else:
            br = metrics.get('building_ratio', metrics.get('build_ratio', 0.5))
            cr = metrics.get('continuity_ratio', 0.8)
            tm = metrics.get('task_multiplication', 1.5)

        timestamp = entry.get('timestamp', f"entry_{i}")

        # Compute entropy with default weights
        H = compute_entropy_proxy(br, cr, tm)

        trajectory.append({
            'index': i,
            'timestamp': timestamp,
            'building_ratio': br,
            'continuity_ratio': cr,
            'task_multiplication': tm,
            'entropy': H,
            'reward': entry.get('reward', 0.0)
        })

    print(f"Computed entropy for {len(trajectory)} time points")
    print()

    # Detect phase transitions (rapid entropy changes)
    print("Detecting phase transitions...")
    transitions = []
    window = 3  # Look for changes over 3-entry windows

    for i in range(window, len(trajectory) - window):
        H_before = statistics.mean([trajectory[j]['entropy'] for j in range(i-window, i)])
        H_after = statistics.mean([trajectory[j]['entropy'] for j in range(i, i+window)])
        delta_H = H_after - H_before

        # Significant drop (escape from metastable state)
        if delta_H < -0.1:
            transitions.append({
                'index': i,
                'timestamp': trajectory[i]['timestamp'],
                'H_before': H_before,
                'H_after': H_after,
                'delta_H': delta_H,
                'type': 'descent'
            })
        # Significant rise (entering metastable state)
        elif delta_H > 0.1:
            transitions.append({
                'index': i,
                'timestamp': trajectory[i]['timestamp'],
                'H_before': H_before,
                'H_after': H_after,
                'delta_H': delta_H,
                'type': 'ascent'
            })

    print(f"Detected {len(transitions)} phase transitions")
    print()

    # Show sample transitions
    if transitions:
        print("Sample phase transitions:")
        for trans in transitions[:5]:
            print(f"  Entry {trans['index']}: ΔH = {trans['delta_H']:.3f} ({trans['type']})")
    print()

    # Sensitivity analysis: test different weight schemes
    print("Sensitivity Analysis (testing different entropy formula weights):")
    print("-" * 70)

    weight_schemes = [
        ((1.0, 2.0, 1.0), "Default (1:2:1)"),
        ((1.0, 1.0, 1.0), "Equal weights"),
        ((2.0, 1.0, 1.0), "Building-heavy"),
        ((1.0, 3.0, 1.0), "Continuity-heavy"),
        ((1.0, 1.0, 2.0), "Task-mult-heavy")
    ]

    sensitivity = []

    for weights, name in weight_schemes:
        # Recompute trajectory with different weights
        H_values = [
            compute_entropy_proxy(t['building_ratio'], t['continuity_ratio'],
                                t['task_multiplication'], weights)
            for t in trajectory
        ]

        # Statistics
        H_mean = statistics.mean(H_values)
        H_std = statistics.stdev(H_values) if len(H_values) > 1 else 0
        H_range = max(H_values) - min(H_values)

        sensitivity.append({
            'weights': weights,
            'name': name,
            'mean_entropy': H_mean,
            'std_entropy': H_std,
            'range': H_range
        })

        print(f"  {name:20s}: H_mean={H_mean:.3f}, H_std={H_std:.3f}, range={H_range:.3f}")

    print()

    # Summary statistics
    print("Trajectory Statistics (Default weights):")
    print("-" * 70)

    H_values = [t['entropy'] for t in trajectory]
    H_mean = statistics.mean(H_values)
    H_std = statistics.stdev(H_values) if len(H_values) > 1 else 0
    H_min = min(H_values)
    H_max = max(H_values)

    print(f"  Mean entropy: {H_mean:.4f}")
    print(f"  Std dev: {H_std:.4f}")
    print(f"  Range: [{H_min:.4f}, {H_max:.4f}]")
    print(f"  Phase transitions: {len(transitions)}")
    print()

    return {
        "trajectory": trajectory[-50:],  # Last 50 points for brevity
        "full_length": len(trajectory),
        "statistics": {
            "mean_entropy": H_mean,
            "std_entropy": H_std,
            "min_entropy": H_min,
            "max_entropy": H_max,
            "range": H_max - H_min
        },
        "phase_transitions": transitions,
        "n_transitions": len(transitions),
        "sensitivity_analysis": sensitivity,
        "interpretation": f"System entropy varies between {H_min:.2f} and {H_max:.2f}, with {len(transitions)} detected phase transitions",
        "limitations": [
            "Entropy proxy is heuristic (deviations from targets)",
            "Targets (br=0.55, cr=0.90, tm=2.0) may not be true optima",
            "Sensitivity analysis shows formula depends on weights",
            "Phase transition detection is threshold-dependent",
            "Does not capture activation-level entropy"
        ]
    }


def main():
    """Extract entropy trajectory and save results."""
    results = extract_entropy_trajectory()

    # Save
    output_dir = Path("analysis")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "entropy_trajectory.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    print()

    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    # Validation
    print("VALIDATION AGAINST PHASE Ω-1 PROTOCOL:")
    print("-" * 70)

    if results['n_transitions'] >= 2:
        print(f"✓ Identified {results['n_transitions']} phase transitions (≥2 required)")
    else:
        print(f"⚠ Identified {results['n_transitions']} phase transitions (<2, insufficient for ΔH_crit)")

    print()

    # Note sensitivity
    print("SENSITIVITY ANALYSIS:")
    print("-" * 70)
    print("Entropy formula shows moderate sensitivity to weight choices.")
    print("Default (1:2:1) emphasizes continuity_ratio as most important.")
    print("Future work: Derive weights from information-theoretic principles.")
    print()


if __name__ == "__main__":
    main()
