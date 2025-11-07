#!/usr/bin/env python3
"""
REAL λ-Fit with Raw Weights - Final CIL Validation

This closes the causal loop. Previous attempts failed because weight normalization
removed the absolute decay signal. Now CIL stores BOTH raw and normalized weights.

Hypothesis: Using raw weights, λ fit will show r² >> 0.001

Method:
1. Clear old CIL data (contains only normalized weights)
2. Run temporal spread experiment with NEW CIL (stores raw + normalized)
3. Compute λ using raw weights
4. Measure r² improvement

Promise: This is REAL execution with actual ground-truth decay.

Author: Claude Code (REAL EXECUTION ONLY)
Date: 2025-11-07
"""

import json
import sys
import math
import random
from pathlib import Path
from datetime import datetime, timedelta

# Import CIL
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from causal_influence_ledger import CausalInfluenceLedger

def generate_temporal_cycles_with_decay(
    n_cycles: int = 100,
    time_span_days: int = 30,
    true_lambda: float = 0.05
):
    """
    Generate cycles with ground-truth exponential decay in influence.

    Each cycle references 5 past cycles with weight = e^(-λt).
    This creates REAL decay signal that CIL should recover.
    """

    base_time = datetime.now() - timedelta(days=time_span_days)

    # Generate cycle timestamps
    cycles = []
    for i in range(n_cycles):
        offset_days = (i / n_cycles) * time_span_days
        offset_hours = random.random() * 12  # Jitter
        timestamp = base_time + timedelta(days=offset_days, hours=offset_hours)

        cycles.append({
            'cycle_id': i,
            'timestamp': timestamp,
            'artifact_id': f'artifact_{i:03d}'
        })

    return cycles, true_lambda

def run_lambda_fit_with_raw_weights():
    """Run CIL with raw weight storage and fit λ"""

    print("=" * 70)
    print("REAL λ-FIT WITH RAW WEIGHTS - FINAL CIL VALIDATION")
    print("=" * 70)

    # Parameters
    n_cycles = 100
    time_span_days = 30
    true_lambda = 0.05  # Ground truth

    print(f"\nParameters:")
    print(f"  Cycles: {n_cycles}")
    print(f"  Time span: {time_span_days} days")
    print(f"  True λ: {true_lambda:.4f}")

    # Generate cycles with ground-truth decay
    print("\nGenerating cycles with exponential decay...")
    cycles, true_lambda = generate_temporal_cycles_with_decay(
        n_cycles=n_cycles,
        time_span_days=time_span_days,
        true_lambda=true_lambda
    )

    # Create fresh CIL instance (with raw weight storage)
    cil = CausalInfluenceLedger()

    # Inject decisions with exponential decay
    print(f"Injecting {len(cycles)} decisions with decay chains...")

    for i, cycle in enumerate(cycles):
        timestamp = cycle['timestamp'].isoformat()
        artifact_id = cycle['artifact_id']

        # Reference 5 past cycles with exponential decay
        inputs = []

        if i >= 5:
            past_indices = random.sample(range(i), 5)
        else:
            past_indices = list(range(i))

        for j in past_indices:
            age_days = (cycle['timestamp'] - cycles[j]['timestamp']).total_seconds() / 86400

            # Ground-truth exponential decay (RAW weight)
            raw_weight = math.exp(-true_lambda * age_days)

            # Add 10% noise
            raw_weight *= (1.0 + random.gauss(0, 0.1))
            raw_weight = max(0.01, raw_weight)

            inputs.append({
                'artifact_id': cycles[j]['artifact_id'],
                'weight': raw_weight,  # RAW weight with decay signal
                'reason': 'causal_dependency'
            })

        if not inputs:
            inputs = [{'artifact_id': artifact_id, 'weight': 1.0, 'reason': 'initial'}]

        # Log decision (CIL will store BOTH raw and normalized)
        cil.log_decision(
            decision_type='artifact_selection',
            inputs=inputs,
            output=1.0,
            metadata={'cycle_id': i},
            timestamp=timestamp
        )

        if (i + 1) % 20 == 0:
            print(f"  Logged {i+1}/{n_cycles} cycles")

    # Compute λ using RAW weights
    print("\n" + "=" * 70)
    print("COMPUTING λ FROM RAW WEIGHTS")
    print("=" * 70)

    domain_lambdas = cil.compute_domain_lambdas()

    print(f"\nDomain-specific λ values (using RAW weights):")

    for domain, (lambda_val, diag) in domain_lambdas.items():
        print(f"\n  {domain}:")
        print(f"    λ_fit = {lambda_val:.6f}")
        print(f"    λ_true = {true_lambda:.6f}")
        print(f"    error = {abs(lambda_val - true_lambda):.6f} ({abs(lambda_val - true_lambda) / true_lambda * 100:.1f}%)")
        print(f"    r² = {diag.get('r_squared', 0):.3f}")
        print(f"    n = {diag.get('n_samples', 0)}")
        print(f"    mean_age = {diag.get('mean_age', 0):.2f} days")
        print(f"    weight_type = {diag.get('weight_type', 'unknown')}")

    # Compare with normalized weights
    print("\n" + "=" * 70)
    print("COMPARISON: RAW vs NORMALIZED WEIGHTS")
    print("=" * 70)

    lambda_raw, diag_raw = cil.compute_lambda_from_influence(use_raw_weights=True)
    lambda_norm, diag_norm = cil.compute_lambda_from_influence(use_raw_weights=False)

    print(f"\nUsing RAW weights:")
    print(f"  λ = {lambda_raw:.6f}")
    print(f"  r² = {diag_raw.get('r_squared', 0):.3f}")

    print(f"\nUsing NORMALIZED weights:")
    print(f"  λ = {lambda_norm:.6f}")
    print(f"  r² = {diag_norm.get('r_squared', 0):.3f}")

    print(f"\nImprovement:")
    print(f"  Δr² = {diag_raw['r_squared'] - diag_norm['r_squared']:.3f}")

    # Victory gate
    print("\n" + "=" * 70)
    print("VICTORY GATE CHECK")
    print("=" * 70)

    sufficient_samples = diag_raw['n_samples'] >= 80
    good_fit = diag_raw['r_squared'] >= 0.70
    reasonable_lambda = 0.001 <= lambda_raw <= 1.0
    accurate_recovery = abs(lambda_raw - true_lambda) / true_lambda <= 0.30  # Within 30%

    criteria = {
        "n ≥ 80": bool(sufficient_samples),
        "r² ≥ 0.70": bool(good_fit),
        "0.001 ≤ λ ≤ 1.0": bool(reasonable_lambda),
        "|λ_fit - λ_true| ≤ 30%": bool(accurate_recovery)
    }

    print()
    for criterion, met in criteria.items():
        status = "✓" if met else "✗"
        print(f"  {status} {criterion}")

    if all(criteria.values()):
        print("\n✓✓✓ CIL λ-FIT: PASSED ✓✓✓")
        print(f"Successfully recovered ground-truth λ using raw weights!")
        print(f"Fitted λ = {lambda_raw:.4f} (true = {true_lambda:.4f}, error = {abs(lambda_raw - true_lambda) / true_lambda * 100:.1f}%)")
    else:
        print("\n⚠ CIL λ-FIT: PARTIAL")
        failing = [c for c, m in criteria.items() if not m]
        print(f"Criteria not met: {', '.join(failing)}")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "method": "raw_weight_lambda_fit",
        "ground_truth": {
            "lambda": true_lambda,
            "n_cycles": n_cycles,
            "time_span_days": time_span_days
        },
        "raw_weights": {
            "lambda": float(lambda_raw),
            "r_squared": float(diag_raw['r_squared']),
            "n_samples": int(diag_raw['n_samples']),
            "mean_age_days": float(diag_raw['mean_age']),
            "error_absolute": float(abs(lambda_raw - true_lambda)),
            "error_relative_pct": float(abs(lambda_raw - true_lambda) / true_lambda * 100)
        },
        "normalized_weights": {
            "lambda": float(lambda_norm),
            "r_squared": float(diag_norm['r_squared']),
            "n_samples": int(diag_norm['n_samples'])
        },
        "improvement": {
            "delta_r_squared": float(diag_raw['r_squared'] - diag_norm['r_squared']),
            "raw_weights_superior": bool(diag_raw['r_squared'] > diag_norm['r_squared'])
        },
        "victory_gate": {
            "criteria": criteria,
            "passed": all(criteria.values())
        }
    }

    output_path = Path("runs/cil_raw_lambda_2025-11-07.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {output_path}")

    return output


if __name__ == "__main__":
    random.seed(42)  # Reproducibility
    run_lambda_fit_with_raw_weights()
