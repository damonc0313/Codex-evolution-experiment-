#!/usr/bin/env python3
"""
Synthetic CIL Experiment - Ground-Truth λ with Influence Chains

Creates synthetic decision chains where later decisions reference earlier
artifacts with exponentially decaying influence: w ~ e^(-λt)

This proves CIL can recover ground-truth λ from influence edges.

Author: Claude Code
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

def generate_synthetic_influence_chain(
    n_cycles: int = 100,
    time_span_days: int = 30,
    true_lambda: float = 0.05
):
    """
    Generate synthetic decision chain with known λ.

    Each cycle:
    - Creates an artifact at time t_i
    - Later cycles reference it with weight w = e^(-λ * age)

    This creates ground-truth exponential decay that CIL should recover.
    """

    base_time = datetime.now() - timedelta(days=time_span_days)

    # Generate cycle timestamps
    cycles = []
    for i in range(n_cycles):
        offset_days = (i / n_cycles) * time_span_days
        offset_hours = random.random() * 12  # Some jitter
        timestamp = base_time + timedelta(days=offset_days, hours=offset_hours)

        cycles.append({
            'cycle_id': i,
            'timestamp': timestamp,
            'artifact_id': f'artifact_{i:03d}'
        })

    return cycles, true_lambda

def run_synthetic_cil_experiment():
    """Run CIL with synthetic influence chains"""

    print("=" * 70)
    print("SYNTHETIC CIL EXPERIMENT - GROUND-TRUTH λ RECOVERY")
    print("=" * 70)

    # Parameters
    n_cycles = 100
    time_span_days = 30
    true_lambda = 0.05  # True decay rate (known ground truth)

    print(f"\nParameters:")
    print(f"  Cycles: {n_cycles}")
    print(f"  Time span: {time_span_days} days")
    print(f"  True λ: {true_lambda:.4f}")

    # Generate cycles
    print("\nGenerating synthetic influence chain...")
    cycles, true_lambda = generate_synthetic_influence_chain(
        n_cycles=n_cycles,
        time_span_days=time_span_days,
        true_lambda=true_lambda
    )

    # Create CIL instance
    cil = CausalInfluenceLedger()

    # Inject decisions with exponential decay influence
    print(f"Injecting {len(cycles)} decisions with decay chains...")

    for i, cycle in enumerate(cycles):
        timestamp = cycle['timestamp'].isoformat()
        artifact_id = cycle['artifact_id']

        # This cycle references previous artifacts with decaying influence
        inputs = []
        total_raw_weight = 0.0

        # Reference exactly 5 random past cycles (fixed count to avoid normalization bias)
        if i >= 5:
            past_indices = random.sample(range(i), min(5, i))
        else:
            past_indices = list(range(i))

        for j in past_indices:
            age_days = (cycle['timestamp'] - cycles[j]['timestamp']).total_seconds() / 86400

            # Ground-truth exponential decay
            raw_weight = math.exp(-true_lambda * age_days)

            # Add some noise (±10%)
            raw_weight *= (1.0 + random.gauss(0, 0.1))
            raw_weight = max(0.01, raw_weight)

            inputs.append({
                'artifact_id': cycles[j]['artifact_id'],
                'weight': raw_weight,
                'reason': 'causal_dependency'
            })
            total_raw_weight += raw_weight

        if not inputs:
            inputs = [{'artifact_id': artifact_id, 'weight': 1.0, 'reason': 'initial'}]

        # Log decision (CIL will normalize weights)
        cil.log_decision(
            decision_type='artifact_selection',
            inputs=inputs,
            output=1.0,
            metadata={'cycle_id': i},
            timestamp=timestamp
        )

        if (i + 1) % 20 == 0:
            print(f"  Logged {i+1}/{n_cycles} cycles")

    # Compute λ from influence edges
    print("\n" + "=" * 70)
    print("COMPUTING λ FROM INFLUENCE EDGES")
    print("=" * 70)

    domain_lambdas = cil.compute_domain_lambdas()

    print(f"\nDomain-specific λ values:")

    recovered_lambdas = []
    for domain, (lambda_val, diag) in domain_lambdas.items():
        print(f"\n  {domain}:")
        print(f"    λ_fit = {lambda_val:.6f}")
        print(f"    λ_true = {true_lambda:.6f}")
        print(f"    error = {abs(lambda_val - true_lambda):.6f} ({abs(lambda_val - true_lambda) / true_lambda * 100:.1f}%)")
        print(f"    r² = {diag.get('r_squared', 0):.3f}")
        print(f"    n = {diag.get('n_samples', 0)}")
        print(f"    mean_age = {diag.get('mean_age', 0):.2f} days")

        recovered_lambdas.append(lambda_val)

    # Victory gate
    print("\n" + "=" * 70)
    print("VICTORY GATE CHECK")
    print("=" * 70)

    if not recovered_lambdas:
        print("\n✗ NO λ VALUES COMPUTED")
        return

    lambda_fit = recovered_lambdas[0]  # Use first domain

    sufficient_samples = all(d[1].get('n_samples', 0) >= 80 for d in domain_lambdas.values())
    good_fits = all(d[1].get('r_squared', 0) >= 0.70 for d in domain_lambdas.values())
    accurate_recovery = abs(lambda_fit - true_lambda) / true_lambda <= 0.20  # Within 20%

    criteria = {
        "n ≥ 80": bool(sufficient_samples),
        "r² ≥ 0.70": bool(good_fits),
        "|λ_fit - λ_true| ≤ 20%": bool(accurate_recovery)
    }

    print()
    for criterion, met in criteria.items():
        status = "✓" if met else "✗"
        print(f"  {status} {criterion}")

    if all(criteria.values()):
        print("\n✓✓✓ SYNTHETIC CIL: PASSED ✓✓✓")
        print(f"CIL successfully recovered ground-truth λ = {true_lambda:.4f}")
        print(f"Fitted λ = {lambda_fit:.4f} (error = {abs(lambda_fit - true_lambda) / true_lambda * 100:.1f}%)")
    else:
        print("\n⚠ SYNTHETIC CIL: PARTIAL")
        failing = [c for c, m in criteria.items() if not m]
        print(f"Criteria not met: {', '.join(failing)}")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "method": "synthetic_influence_chains",
        "ground_truth": {
            "lambda": true_lambda,
            "n_cycles": n_cycles,
            "time_span_days": time_span_days
        },
        "fitted": {
            domain: {
                "lambda": lambda_val,
                "error_absolute": abs(lambda_val - true_lambda),
                "error_relative_pct": abs(lambda_val - true_lambda) / true_lambda * 100,
                "r_squared": diag.get('r_squared', 0),
                "n_samples": diag.get('n_samples', 0),
                "mean_age_days": diag.get('mean_age', 0)
            }
            for domain, (lambda_val, diag) in domain_lambdas.items()
        },
        "victory_gate": {
            "criteria": criteria,
            "passed": all(criteria.values())
        }
    }

    output_path = Path("runs/cil_synthetic_lambda_2025-11-07.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {output_path}")

    return output


if __name__ == "__main__":
    random.seed(42)  # Reproducibility
    run_synthetic_cil_experiment()
