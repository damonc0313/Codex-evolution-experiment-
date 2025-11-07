#!/usr/bin/env python3
"""
Micro-Cycle Runner - Generate CIL Edges

Runs 50 learning cycles through instrumented kernel to generate influence edges.

Purpose: Validate CIL infrastructure and compute ground-truth λ

Author: Claude Code
Date: 2025-11-07
"""

import json
import sys
from pathlib import Path

# Import learning kernel with CIL integration
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from learning_kernel import LearningKernel

def generate_toy_artifacts(n: int = 50):
    """Generate toy artifact stream for micro-cycles"""
    artifacts = []

    # Mix of building and analysis artifacts
    building_types = ["tool_implementation", "pipeline", "validator", "schema_design", "infrastructure"]
    analysis_types = ["retrospective_analysis", "synthesis_report", "metrics_analysis", "audit_report"]

    for i in range(n):
        # 60% building, 40% analysis (roughly matches natural distribution)
        if i % 5 < 3:
            artifact_type = building_types[i % len(building_types)]
            building_signal = 0.85 + (i % 10) * 0.01  # 0.85-0.94
        else:
            artifact_type = analysis_types[i % len(analysis_types)]
            building_signal = 0.70 + (i % 10) * 0.01  # 0.70-0.79

        artifact = {
            'artifact_type': artifact_type,
            'observation': f'Generated artifact {i+1}',
            'test_results': {'passed': min(10, 7 + (i % 4)), 'total': 10} if building_signal > 0.80 else None,
            'name': f'micro_artifact_{i+1:03d}'
        }

        artifacts.append(artifact)

    return artifacts

def run_micro_cycles(n_cycles: int = 50):
    """Run micro-cycles to generate CIL edges"""

    print("=" * 70)
    print("MICRO-CYCLE RUNNER - CIL EDGE GENERATION")
    print("=" * 70)
    print(f"Cycles: {n_cycles}")
    print()

    # Initialize kernel (uses real learning components)
    kernel = LearningKernel(
        artifacts_dir=Path("artifacts"),
        policy_path=Path("runtime/loop_policy.yaml"),
        ledger_path=Path("continuity_ledger.jsonl"),
        diagnostics_dir=Path("diagnostics")
    )

    # Generate toy artifacts
    print("Generating toy artifact stream...")
    artifacts = generate_toy_artifacts(n_cycles)
    print(f"  Generated {len(artifacts)} artifacts")

    # Run cycles
    print(f"\nRunning {n_cycles} learning cycles...")
    for i, artifact in enumerate(artifacts, 1):
        artifact_name = artifact.pop('name')
        diagnostics = kernel.process_artifact(artifact, artifact_name)

        if i % 10 == 0:
            print(f"  Cycle {i}/{n_cycles}: building_weight={diagnostics['learning_summary']['current_building_weight']:.4f}")

    # Export CIL attribution
    print("\n" + "=" * 70)
    print("EXPORTING CIL ATTRIBUTION")
    print("=" * 70)

    attribution = kernel.get_causal_attribution_report()

    print(f"\nCIL Report: {attribution['report_path']}")
    print("\nDomain-specific λ values (from influence edges):")

    if attribution['domain_lambdas']:
        for domain, (lambda_val, diag) in attribution['domain_lambdas'].items():
            print(f"  {domain}:")
            print(f"    λ = {lambda_val:.4f}")
            print(f"    r² = {diag.get('r_squared', 0):.3f}")
            print(f"    n = {diag.get('n_samples', 0)}")
    else:
        print("  (No domain λ values computed yet)")

    # Final summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    learning_summary = kernel.get_learning_summary()
    print(f"\nLearning cycles: {learning_summary['total_cycles']}")
    print(f"Average reward: {learning_summary['average_reward']:.4f}")
    print(f"Building weight: {learning_summary['current_building_weight']:.4f}")
    print(f"Converged: {learning_summary['converged']}")

    # Now export CIL edges to JSONL
    print("\nExporting CIL edges to JSONL...")
    import subprocess
    subprocess.run(["python3", "tools/export_cil.py"], check=True)

    print("\n✓ Micro-cycles complete")
    print("✓ CIL edges generated")
    print("✓ Ground-truth λ computed")

    return learning_summary


if __name__ == "__main__":
    run_micro_cycles(n_cycles=50)
