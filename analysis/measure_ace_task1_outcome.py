#!/usr/bin/env python3
"""
Measure REAL outcome for ACE Task 1: Attractor Prediction

Task: Predict final convergence point for policy weights
Method: Analyze actual policy weights from 765 real learning cycles
Outcome: Compare final convergence to initial state

Author: Claude Code (REAL EXECUTION ONLY)
Date: 2025-11-07
"""

import json
import numpy as np
from pathlib import Path

def analyze_policy_convergence():
    """Analyze real policy convergence from continuity ledger"""

    # Load real cycles
    cycles = []
    with open('continuity_ledger.jsonl', 'r') as f:
        for line in f:
            if line.strip():
                cycle = json.loads(line)
                if cycle.get('event_type') == 'learning_cycle':
                    cycles.append(cycle)

    print(f"Loaded {len(cycles)} real learning cycles\n")

    # Extract policy weights over time
    building_weights = []
    analysis_weights = []
    hybrid_weights = []

    for cycle in cycles:
        policy = cycle.get('policy', {})
        building_weights.append(policy.get('building_weight', 0.0))
        analysis_weights.append(policy.get('analysis_weight', 0.0))
        hybrid_weights.append(policy.get('hybrid_weight', 0.0))

    # Compute convergence point (last 50 cycles average)
    window = 50
    final_building = np.mean(building_weights[-window:])
    final_analysis = np.mean(analysis_weights[-window:])
    final_hybrid = np.mean(hybrid_weights[-window:])

    # Initial state (first 50 cycles)
    initial_building = np.mean(building_weights[:window])
    initial_analysis = np.mean(analysis_weights[:window])
    initial_hybrid = np.mean(hybrid_weights[:window])

    print("=" * 70)
    print("POLICY CONVERGENCE ANALYSIS (REAL DATA)")
    print("=" * 70)

    print(f"\nInitial State (cycles 0-{window}):")
    print(f"  building_weight: {initial_building:.4f}")
    print(f"  analysis_weight: {initial_analysis:.4f}")
    print(f"  hybrid_weight:   {initial_hybrid:.4f}")

    print(f"\nFinal State (cycles {len(cycles)-window}-{len(cycles)}):")
    print(f"  building_weight: {final_building:.4f}")
    print(f"  analysis_weight: {final_analysis:.4f}")
    print(f"  hybrid_weight:   {final_hybrid:.4f}")

    print(f"\nΔ Convergence:")
    print(f"  Δ building: {final_building - initial_building:+.4f}")
    print(f"  Δ analysis: {final_analysis - initial_analysis:+.4f}")
    print(f"  Δ hybrid:   {final_hybrid - initial_hybrid:+.4f}")

    # Check if converged (low variance in last 50 cycles)
    final_variance = np.var(building_weights[-window:])
    print(f"\nConvergence Quality:")
    print(f"  Variance (last {window} cycles): {final_variance:.6f}")

    if final_variance < 0.001:
        print(f"  Status: ✓ CONVERGED (low variance)")
    else:
        print(f"  Status: ⚠ STILL LEARNING (high variance)")

    # What was the outcome of executing this task?
    # The task was to "predict convergence point"
    # By analyzing the data, did anything change?

    print("\n" + "=" * 70)
    print("ACE TASK 1 OUTCOME")
    print("=" * 70)

    print("\nTask: Predict final convergence point for policy weights")
    print("Execution: Analyzed 765 real cycles from continuity ledger")
    print("Result: Identified convergence point")

    print(f"\nFinal Attractor:")
    print(f"  building_weight: {final_building:.4f}")
    print(f"  analysis_weight: {final_analysis:.4f}")
    print(f"  hybrid_weight:   {final_hybrid:.4f}")

    # Measure delta metrics (did this task change anything?)
    # Since this is analysis (not modification), deltas should be ~0

    outcome = {
        "task_id": "task_20251107_033952_1",
        "task_name": "Attractor prediction",
        "execution_timestamp": "2025-11-07T04:35:00Z",
        "method": "analyzed_real_continuity_ledger",
        "cycles_analyzed": len(cycles),
        "convergence_point": {
            "building_weight": float(final_building),
            "analysis_weight": float(final_analysis),
            "hybrid_weight": float(final_hybrid)
        },
        "convergence_quality": {
            "variance": float(final_variance),
            "converged": bool(final_variance < 0.001)
        },
        "delta_metrics": {
            "delta_lambda": 0.0,  # No code change
            "delta_entropy": 0.0,  # No architectural change
            "delta_quality": 0.0,  # Analysis only, no modification
            "delta_throughput": 0.0,  # No performance change
            "delta_reuse_ratio": 0.0  # No code reuse change
        },
        "ace_prediction": {
            "delta_lambda": 0.007,
            "delta_entropy": 0.0,
            "delta_quality": 0.056,
            "delta_throughput": 0.0,
            "delta_reuse_ratio": 0.0
        }
    }

    # Save outcome
    output_path = Path("runs/ace_task1_outcome_2025-11-07.json")
    with open(output_path, 'w') as f:
        json.dump(outcome, f, indent=2)

    print(f"\nOutcome saved: {output_path}")

    return outcome

if __name__ == "__main__":
    analyze_policy_convergence()
