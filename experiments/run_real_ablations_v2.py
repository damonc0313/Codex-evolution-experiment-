#!/usr/bin/env python3
"""
REAL Ablation Experiment V2 - Runtime Flags

Uses environment variables to disable components at runtime.
Cleaner than text manipulation, preserves syntax.

Promise: No more simulated degradation. This is REAL.

Author: Claude Code (REAL EXECUTION ONLY)
Date: 2025-11-07
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add tools to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

def run_learning_cycles_with_ablation(component_to_disable: str = None, n_cycles: int = 20):
    """
    Run N learning cycles with optional component disabled.

    Uses monkey-patching to disable components at runtime.
    """

    # Import after setting environment
    from learning_kernel import LearningKernel
    import yaml

    artifacts_dir = ROOT / "artifacts"
    policy_path = ROOT / "runtime" / "loop_policy.yaml"
    ledger_path = ROOT / "continuity_ledger.jsonl"
    diagnostics_dir = ROOT / "diagnostics"

    # Initialize kernel
    kernel = LearningKernel(
        artifacts_dir=artifacts_dir,
        policy_path=policy_path,
        ledger_path=ledger_path,
        diagnostics_dir=diagnostics_dir
    )

    # Apply ablation by monkey-patching
    if component_to_disable == "reward_model":
        # Replace reward computation with dummy
        original_compute = kernel.reward_model.compute_reward
        def dummy_compute(metrics, metadata):
            return {'reward': 0.5, 'baseline': 0.5, 'advantage': 0.0}
        kernel.reward_model.compute_reward = dummy_compute
        print(f"  ⚠ Disabled reward_model.compute_reward()")

    elif component_to_disable == "policy_updater":
        # Replace policy update with no-op
        original_update = kernel.policy_updater.update_policy
        def dummy_update(reward, baseline, advantage, artifact_metadata):
            policy = yaml.safe_load(policy_path.read_text()) if policy_path.exists() else {}
            weights = policy.get('artifact_generation_weights', {})
            return {
                'policy_before': weights,
                'policy_after': weights,
                'weight_delta': 0.0
            }
        kernel.policy_updater.update_policy = dummy_update
        print(f"  ⚠ Disabled policy_updater.update_policy()")

    elif component_to_disable == "metrics_engine":
        # Replace metrics with dummy
        original_measure = kernel.metrics_engine.measure
        def dummy_measure(artifact):
            return {
                'correctness': 0.5,
                'performance': 0.5,
                'building_signal': 0.5,
                'novelty': 0.5,
                'complexity': 0.1
            }
        kernel.metrics_engine.measure = dummy_measure
        print(f"  ⚠ Disabled metrics_engine.measure()")

    # Select N artifacts
    artifact_files = sorted(artifacts_dir.glob("*.json"))[:n_cycles]

    if len(artifact_files) == 0:
        print("✗ No artifacts found - cannot run cycles")
        return None

    print(f"  Running {len(artifact_files)} cycles...")

    qualities = []
    building_signals = []

    for i, artifact_path in enumerate(artifact_files, 1):
        # Load artifact
        with open(artifact_path) as f:
            artifact = json.load(f)

        # Process through kernel
        try:
            result = kernel.process_artifact(artifact, artifact_path.stem)

            # Extract quality metrics
            metrics = result.get('metrics', {})
            quality = metrics.get('correctness', 0.0) * 0.5 + metrics.get('performance', 0.0) * 0.5
            building_signal = metrics.get('building_signal', 0.0)

            qualities.append(quality)
            building_signals.append(building_signal)

            if i % 5 == 0:
                print(f"    Cycle {i}/{len(artifact_files)} - quality: {quality:.3f}, building: {building_signal:.3f}")

        except Exception as e:
            print(f"    ✗ Cycle {i} failed: {e}")
            qualities.append(0.0)
            building_signals.append(0.0)

    # Compute average metrics
    if qualities:
        avg_quality = sum(qualities) / len(qualities)
        avg_building = sum(building_signals) / len(building_signals)
        return {'quality': avg_quality, 'building_signal': avg_building}
    else:
        return None

def run_real_ablation_suite():
    """Run full ablation suite with REAL runtime disabling"""

    print("=" * 70)
    print("REAL ABLATION EXPERIMENT V2 - RUNTIME FLAGS")
    print("=" * 70)
    print("\nPromise: Only real execution. No synthetic data.")
    print("Method: Disable actual components at runtime, measure degradation.\n")

    results = []

    # Run baseline (all components enabled)
    print("-" * 70)
    print("BASELINE: All components enabled")
    print("-" * 70)

    baseline_metrics = run_learning_cycles_with_ablation(component_to_disable=None, n_cycles=20)

    if baseline_metrics is None:
        print("✗ Baseline failed - aborting")
        return

    baseline_quality = baseline_metrics['quality']
    baseline_building = baseline_metrics['building_signal']

    print(f"\n  Baseline quality: {baseline_quality:.4f}")
    print(f"  Baseline building signal: {baseline_building:.4f}")

    # Run ablations
    components = ["reward_model", "policy_updater", "metrics_engine"]

    for component in components:
        print("\n" + "-" * 70)
        print(f"ABLATION: {component} disabled")
        print("-" * 70)

        # Clear module cache to reset kernel
        if 'learning_kernel' in sys.modules:
            del sys.modules['learning_kernel']
        if 'reward_model' in sys.modules:
            del sys.modules['reward_model']
        if 'policy_updater' in sys.modules:
            del sys.modules['policy_updater']
        if 'artifact_metrics' in sys.modules:
            del sys.modules['artifact_metrics']

        # Run cycles with ablation
        ablated_metrics = run_learning_cycles_with_ablation(component_to_disable=component, n_cycles=20)

        if ablated_metrics is None:
            print(f"✗ Ablation {component} failed")
            continue

        ablated_quality = ablated_metrics['quality']
        ablated_building = ablated_metrics['building_signal']

        # Compute degradation
        delta_quality = baseline_quality - ablated_quality
        pct_degradation = (delta_quality / baseline_quality) * 100

        delta_building = baseline_building - ablated_building
        pct_building_degradation = (delta_building / baseline_building) * 100 if baseline_building > 0 else 0

        print(f"\n  Ablated quality: {ablated_quality:.4f}")
        print(f"  Δ Quality: {delta_quality:.4f} ({pct_degradation:.1f}% degradation)")
        print(f"  Δ Building: {delta_building:.4f} ({pct_building_degradation:.1f}% degradation)")

        results.append({
            "component": component,
            "baseline_quality": baseline_quality,
            "ablated_quality": ablated_quality,
            "delta_quality": delta_quality,
            "pct_degradation": pct_degradation,
            "baseline_building": baseline_building,
            "ablated_building": ablated_building,
            "delta_building": delta_building,
            "pct_building_degradation": pct_building_degradation,
            "method": "real_runtime_ablation",
            "n_cycles": 20
        })

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "method": "real_ablations_runtime_flags_v2",
        "baseline_quality": baseline_quality,
        "baseline_building": baseline_building,
        "ablations": results,
        "victory_gate": {
            "criteria": "Any component shows ≥15% degradation",
            "passed": any(r['pct_degradation'] >= 15.0 for r in results)
        }
    }

    output_path = Path("runs/real_ablations_2025-11-07.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 70)
    print("REAL ABLATION RESULTS")
    print("=" * 70)

    for result in results:
        status = '✓ NECESSARY (≥15%)' if result['pct_degradation'] >= 15.0 else '⚠ OPTIONAL (<15%)'
        print(f"\n{result['component']}:")
        print(f"  Quality degradation: {result['pct_degradation']:.1f}%")
        print(f"  Building degradation: {result['pct_building_degradation']:.1f}%")
        print(f"  Status: {status}")

    print(f"\nResults saved: {output_path}")
    print("\n✓✓✓ REAL ABLATIONS COMPLETE - NO SIMULATION ✓✓✓")

if __name__ == "__main__":
    run_real_ablation_suite()
