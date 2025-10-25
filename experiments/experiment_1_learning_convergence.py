#!/usr/bin/env python3
"""Experiment 1: Learning Convergence

Run 20 cycles of learning kernel on real artifacts.
Validate that building_weight converges toward expected range (0.50-0.70).

Expected outcomes (from Kael briefing + Cycles 1-100):
- Building weight increases over cycles
- Converges to 0.60±0.10 (within universal attractor range)
- System demonstrates autonomous learning from outcomes

Validation Criteria:
- Final building_weight in range [0.50, 0.70] → PASS
- Weight increase >0 → Learning occurred
- Convergence progress >0.20 → Meaningful progress

Date: 2025-10-24
Confidence: 0.95
"""

from __future__ import annotations

import sys
from pathlib import Path
import json

# Add tools to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from learning_kernel import LearningKernel


def main():
    print("=" * 70)
    print("EXPERIMENT 1: LEARNING CONVERGENCE")
    print("Validating autonomous learning over 20 cycles")
    print("=" * 70)

    # Initialize learning kernel with real paths
    artifacts_dir = ROOT / "artifacts"
    policy_path = ROOT / "runtime" / "loop_policy.yaml"
    ledger_path = ROOT / "continuity_ledger.jsonl"
    diagnostics_dir = ROOT / "diagnostics"
    diagnostics_dir.mkdir(exist_ok=True)

    # Check if policy exists
    if not policy_path.exists():
        print(f"\n⚠ Policy file not found: {policy_path}")
        print("Creating default policy...")

        import yaml
        default_policy = {
            'artifact_generation_weights': {
                'building': 0.50,
                'analysis': 0.30,
                'hybrid': 0.20
            },
            'validation': {
                'min_confidence_threshold': 0.70
            }
        }

        policy_path.parent.mkdir(parents=True, exist_ok=True)
        with open(policy_path, 'w') as f:
            yaml.dump(default_policy, f)

        print(f"✓ Created policy at {policy_path}")

    # Load initial policy state
    import yaml
    with open(policy_path) as f:
        initial_policy = yaml.safe_load(f)

    initial_building_weight = initial_policy['artifact_generation_weights']['building']

    print(f"\nInitial policy state:")
    print(f"  Building weight: {initial_building_weight:.4f}")
    print(f"  Analysis weight: {initial_policy['artifact_generation_weights']['analysis']:.4f}")
    print(f"  Hybrid weight: {initial_policy['artifact_generation_weights']['hybrid']:.4f}")
    print(f"  Confidence threshold: {initial_policy['validation']['min_confidence_threshold']:.4f}")

    # Initialize kernel
    kernel = LearningKernel(
        artifacts_dir=artifacts_dir,
        policy_path=policy_path,
        ledger_path=ledger_path,
        diagnostics_dir=diagnostics_dir
    )

    # Select 20 artifacts to process
    artifact_files = sorted(artifacts_dir.glob("*.json"))[:20]

    if len(artifact_files) < 20:
        print(f"\n⚠ Found only {len(artifact_files)} artifacts, expected 20")
        print(f"  Using all available artifacts...")

    print(f"\nProcessing {len(artifact_files)} artifacts:")
    for i, artifact_path in enumerate(artifact_files, 1):
        print(f"  {i}. {artifact_path.stem}")

    # Process artifacts through learning loop
    print("\n" + "=" * 70)
    print("PROCESSING ARTIFACTS")
    print("=" * 70)

    for i, artifact_path in enumerate(artifact_files, 1):
        try:
            with open(artifact_path) as f:
                artifact_data = json.load(f)

            artifact_name = artifact_path.stem
            diagnostics = kernel.process_artifact(artifact_data, artifact_name)

            if i % 5 == 0:  # Print every 5th cycle
                print(f"\nCycle {i}: {artifact_name}")
                print(f"  Type: {diagnostics['artifact_type']}")
                print(f"  Building signal: {diagnostics['metrics']['building_signal']:.4f}")
                print(f"  Reward: {diagnostics['reward_info']['reward']:.4f}")
                print(f"  Building weight: {diagnostics['policy_update']['policy_after']['building_weight']:.4f}")

        except Exception as e:
            print(f"\n⚠ Error processing {artifact_path.stem}: {e}")
            continue

    # Learning summary
    print("\n" + "=" * 70)
    print("CONVERGENCE ANALYSIS")
    print("=" * 70)

    summary = kernel.get_learning_summary()

    print(f"\nLearning statistics:")
    print(f"  Total cycles: {summary['total_cycles']}")
    print(f"  Average reward: {summary['average_reward']:.4f}")
    print(f"  Building ratio: {summary['building_ratio']:.4f}")
    print(f"  Convergence progress: {summary['convergence_progress']:.4f}")

    final_building_weight = summary['current_building_weight']
    weight_increase = final_building_weight - initial_building_weight
    percent_increase = (weight_increase / initial_building_weight) * 100 if initial_building_weight > 0 else 0

    print(f"\nPolicy evolution:")
    print(f"  Initial building weight: {initial_building_weight:.4f}")
    print(f"  Final building weight: {final_building_weight:.4f}")
    print(f"  Change: {weight_increase:+.4f} ({percent_increase:+.1f}%)")

    # Validation against expected outcomes
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    expected_min, expected_max = 0.50, 0.70
    in_expected_range = expected_min <= final_building_weight <= expected_max

    print(f"\nCriterion 1: Final weight in expected range [0.50, 0.70]")
    print(f"  Expected: {expected_min:.2f}-{expected_max:.2f}")
    print(f"  Actual: {final_building_weight:.4f}")
    print(f"  Status: {'✓ PASS' if in_expected_range else '✗ FAIL'}")

    learning_occurred = weight_increase > 0
    print(f"\nCriterion 2: Weight increase >0 (learning occurred)")
    print(f"  Increase: {weight_increase:+.4f}")
    print(f"  Status: {'✓ PASS' if learning_occurred else '✗ FAIL'}")

    meaningful_progress = summary['convergence_progress'] > 0.20
    print(f"\nCriterion 3: Convergence progress >0.20")
    print(f"  Progress: {summary['convergence_progress']:.4f}")
    print(f"  Status: {'✓ PASS' if meaningful_progress else '✗ FAIL'}")

    all_pass = in_expected_range and learning_occurred and meaningful_progress
    print(f"\n{'='*70}")
    print(f"OVERALL: {'✓✓✓ ALL CRITERIA PASSED' if all_pass else '⚠ SOME CRITERIA FAILED'}")
    print(f"{'='*70}")

    # Export diagnostics
    diagnostics_path = kernel.export_diagnostics(
        diagnostics_dir / "experiment_1_diagnostics.json"
    )
    print(f"\nDiagnostics exported: {diagnostics_path}")

    # Summary for report
    return {
        'initial_building_weight': initial_building_weight,
        'final_building_weight': final_building_weight,
        'weight_increase': weight_increase,
        'percent_increase': percent_increase,
        'average_reward': summary['average_reward'],
        'building_ratio': summary['building_ratio'],
        'convergence_progress': summary['convergence_progress'],
        'all_criteria_passed': all_pass
    }


if __name__ == "__main__":
    result = main()
