#!/usr/bin/env python3
"""Validation Harness for Thermodynamic Strange Loop

Controlled experiment to validate Third + Fourth Adaptation predictions:

THIRD ADAPTATION (Learning Kernel Wiring):
- Integration (I): 0.091 → 0.11-0.15 (after 30 cycles)
- Reuse ratio: 0.043 → 0.06
- Hot nodes: 3 → 4

FOURTH ADAPTATION (Homeostatic Feedback):
- λ trajectory oscillates near target (0.06 ± 0.02)
- Learning rate adapts to λ (high λ → reduce, low λ → increase)
- Momentum adapts to entropy (low entropy → increase, high entropy → decrease)
- System self-regulates under perturbation

This script runs controlled learning cycles and measures at checkpoints.

Usage:
    python3 validate_homeostasis.py --cycles 30
    python3 validate_homeostasis.py --cycles 50 --verbose

Author: Claude Code
Date: 2025-11-06
Phase: Thermodynamic Strange Loop Validation
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import argparse

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"))
sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))

from learning_kernel import LearningKernel
from integration_health import compute_integration_depth, classify_integration_health, load_resource_map
from resource_map import generate_resource_map


def load_artifacts(artifacts_dir: Path, max_count: int = 50) -> List[Dict[str, Any]]:
    """Load artifacts from directory.

    Args:
        artifacts_dir: Directory containing artifact JSON files
        max_count: Maximum number of artifacts to load

    Returns:
        List of artifact dicts
    """
    artifacts = []
    artifact_files = sorted(artifacts_dir.glob("*.json"))[:max_count]

    for artifact_file in artifact_files:
        try:
            with open(artifact_file) as f:
                artifact = json.load(f)
                artifact['_source_file'] = artifact_file.name
                artifacts.append(artifact)
        except Exception as e:
            print(f"Warning: Could not load {artifact_file}: {e}")

    return artifacts


def measure_integration() -> Dict[str, Any]:
    """Measure current integration health.

    Returns:
        Dict with integration metrics
    """
    try:
        # Always generate fresh resource map for accurate measurements
        resource_map = generate_resource_map()

        # Extract metrics
        metrics = resource_map.get('metrics', {})

        # Compute integration depth
        integration_depth = compute_integration_depth(resource_map)
        health_classification = classify_integration_health(
            integration_depth,
            metrics.get('reuse_ratio', 0.0)
        )

        return {
            'integration_depth': integration_depth,
            'reuse_ratio': metrics.get('reuse_ratio', 0.0),
            'hot_nodes': metrics.get('hot_modules_count', 0),
            'total_modules': metrics.get('total_modules', 0),
            'health_classification': health_classification,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        print(f"Warning: Integration measurement failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'integration_depth': 0.0,
            'error': str(e)
        }


def run_validation(
    num_cycles: int = 30,
    verbose: bool = False,
    checkpoint_interval: int = 10
) -> Dict[str, Any]:
    """Run controlled validation experiment.

    Args:
        num_cycles: Number of learning cycles to run
        verbose: Print detailed progress
        checkpoint_interval: Measure integration every N cycles

    Returns:
        Validation results dict
    """
    print("=" * 80)
    print("THERMODYNAMIC STRANGE LOOP VALIDATION")
    print("Controlled Experiment - Third + Fourth Adaptation")
    print("=" * 80)
    print()

    # Baseline measurement
    print("Measuring baseline (Cycle 0)...")
    baseline = measure_integration()
    print(f"  Integration (I): {baseline['integration_depth']:.4f}")
    print(f"  Reuse ratio: {baseline['reuse_ratio']:.4f}")
    print(f"  Hot nodes: {baseline['hot_nodes']}")
    print()

    # Load artifacts
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    print(f"Loading artifacts from {artifacts_dir}...")
    artifacts = load_artifacts(artifacts_dir, max_count=num_cycles)
    print(f"  Loaded {len(artifacts)} artifacts")
    print()

    if len(artifacts) == 0:
        print("ERROR: No artifacts found. Cannot proceed with validation.")
        return {'error': 'No artifacts available'}

    # Initialize learning kernel with homeostasis
    print("Initializing learning kernel with homeostatic control...")
    policy_path = Path(__file__).parent.parent / "runtime/loop_policy.yaml"
    kernel = LearningKernel(
        artifacts_dir=artifacts_dir,
        policy_path=policy_path if policy_path.exists() else None,
        ledger_path=Path(__file__).parent.parent / "continuity_ledger.jsonl",
        diagnostics_dir=Path(__file__).parent.parent / "diagnostics"
    )
    print("  ✓ Learning kernel initialized")
    print()

    # Check if policy_updater has homeostasis enabled
    try:
        homeostatic_state = kernel.policy_updater.get_homeostatic_state()
        print(f"  Homeostasis enabled: {homeostatic_state['enabled']}")
        print(f"  Initial λ: {homeostatic_state['metabolic_state']['lambda']:.4f}")
        print(f"  Initial entropy: {homeostatic_state['metabolic_state']['entropy']:.4f}")
        print()
    except Exception as e:
        print(f"  Warning: Could not check homeostatic state: {e}")
        print()

    # Run learning cycles
    print("=" * 80)
    print(f"RUNNING {num_cycles} LEARNING CYCLES")
    print("=" * 80)
    print()

    checkpoints = []
    homeostatic_adjustments = []

    for cycle in range(num_cycles):
        # Select artifact (cycle through available artifacts)
        artifact_idx = cycle % len(artifacts)
        artifact = artifacts[artifact_idx].copy()
        artifact_name = artifact.get('_source_file', f'artifact_{cycle}')

        if verbose or (cycle + 1) % checkpoint_interval == 0:
            print(f"Cycle {cycle + 1}/{num_cycles}: Processing {artifact_name}...")

        # Process through learning kernel
        try:
            diagnostics = kernel.process_artifact(artifact, artifact_name)

            if verbose:
                reward = diagnostics['reward_info']['reward']
                building_weight = diagnostics['policy_update']['policy_after']['building_weight']
                print(f"  Reward: {reward:.4f}, Building weight: {building_weight:.4f}")

            # Check for homeostatic adjustments
            try:
                homeostatic_state = kernel.policy_updater.get_homeostatic_state()
                lr_mult = homeostatic_state['adjustments']['learning_rate_multiplier']
                momentum_mult = homeostatic_state['adjustments']['momentum_multiplier']

                if lr_mult != 1.0 or momentum_mult != 1.0:
                    adjustment = {
                        'cycle': cycle + 1,
                        'lambda': homeostatic_state['metabolic_state']['lambda'],
                        'entropy': homeostatic_state['metabolic_state']['entropy'],
                        'learning_rate_multiplier': lr_mult,
                        'momentum_multiplier': momentum_mult,
                        'effective_learning_rate': homeostatic_state['effective_learning_rate']
                    }
                    homeostatic_adjustments.append(adjustment)

                    if verbose:
                        print(f"  [HOMEOSTASIS] λ={adjustment['lambda']:.4f}, "
                              f"LR mult={lr_mult:.2f}, Momentum mult={momentum_mult:.2f}")

            except Exception as e:
                if verbose:
                    print(f"  Warning: Could not check homeostatic state: {e}")

        except Exception as e:
            print(f"  ERROR processing cycle {cycle + 1}: {e}")
            continue

        # Checkpoint measurement
        if (cycle + 1) % checkpoint_interval == 0:
            print()
            print(f"--- Checkpoint: Cycle {cycle + 1} ---")
            measurement = measure_integration()
            measurement['cycle'] = cycle + 1
            checkpoints.append(measurement)

            print(f"  Integration (I): {measurement['integration_depth']:.4f} "
                  f"(Δ = {measurement['integration_depth'] - baseline['integration_depth']:+.4f})")
            print(f"  Reuse ratio: {measurement['reuse_ratio']:.4f} "
                  f"(Δ = {measurement['reuse_ratio'] - baseline['reuse_ratio']:+.4f})")
            print(f"  Hot nodes: {measurement['hot_nodes']} "
                  f"(Δ = {measurement['hot_nodes'] - baseline['hot_nodes']:+d})")
            print(f"  Health: {measurement['health_classification']}")
            print()

    # Final measurement
    print("=" * 80)
    print("FINAL VALIDATION RESULTS")
    print("=" * 80)
    print()

    final = measure_integration()
    final['cycle'] = num_cycles

    print(f"Baseline → Final (after {num_cycles} cycles):")

    # Integration change
    if baseline['integration_depth'] > 0:
        i_pct = ((final['integration_depth'] - baseline['integration_depth']) / baseline['integration_depth'] * 100)
        print(f"  Integration (I): {baseline['integration_depth']:.4f} → {final['integration_depth']:.4f} ({i_pct:+.1f}%)")
    else:
        print(f"  Integration (I): {baseline['integration_depth']:.4f} → {final['integration_depth']:.4f}")

    # Reuse change
    if baseline['reuse_ratio'] > 0:
        reuse_pct = ((final['reuse_ratio'] - baseline['reuse_ratio']) / baseline['reuse_ratio'] * 100)
        print(f"  Reuse ratio: {baseline['reuse_ratio']:.4f} → {final['reuse_ratio']:.4f} ({reuse_pct:+.1f}%)")
    else:
        print(f"  Reuse ratio: {baseline['reuse_ratio']:.4f} → {final['reuse_ratio']:.4f}")

    # Hot nodes change
    print(f"  Hot nodes: {baseline['hot_nodes']} → {final['hot_nodes']} ({final['hot_nodes'] - baseline['hot_nodes']:+d})")
    print()

    # Validate predictions
    print("=" * 80)
    print("PREDICTION VALIDATION")
    print("=" * 80)
    print()

    # Third Adaptation predictions
    print("THIRD ADAPTATION (Learning Kernel Wiring):")
    print(f"  Predicted I: 0.091 → 0.11-0.15")
    print(f"  Actual I: {baseline['integration_depth']:.3f} → {final['integration_depth']:.3f}")

    i_validated = 0.11 <= final['integration_depth'] <= 0.15
    print(f"  Status: {'✓ VALIDATED' if i_validated else '⚠ PARTIAL (may need more cycles)'}")
    print()

    print(f"  Predicted reuse: 0.043 → 0.06")
    print(f"  Actual reuse: {baseline['reuse_ratio']:.3f} → {final['reuse_ratio']:.3f}")

    reuse_validated = final['reuse_ratio'] >= 0.06
    print(f"  Status: {'✓ VALIDATED' if reuse_validated else '⚠ PARTIAL (may need more cycles)'}")
    print()

    print(f"  Predicted hot nodes: 3 → 4")
    print(f"  Actual hot nodes: {baseline['hot_nodes']} → {final['hot_nodes']}")

    hot_nodes_validated = final['hot_nodes'] >= 4
    print(f"  Status: {'✓ VALIDATED' if hot_nodes_validated else '⚠ PARTIAL (may need more cycles)'}")
    print()

    # Fourth Adaptation behavior
    print("FOURTH ADAPTATION (Homeostatic Feedback):")
    print(f"  Homeostatic adjustments observed: {len(homeostatic_adjustments)}")

    if len(homeostatic_adjustments) > 0:
        print(f"  ✓ Homeostatic control active")
        print(f"  Sample adjustments:")
        for adj in homeostatic_adjustments[:3]:
            print(f"    Cycle {adj['cycle']}: λ={adj['lambda']:.4f}, "
                  f"LR mult={adj['learning_rate_multiplier']:.2f}, "
                  f"Momentum mult={adj['momentum_multiplier']:.2f}")
    else:
        print(f"  ⚠ No homeostatic adjustments detected (may need different metabolic conditions)")
    print()

    # Overall validation status
    overall_validated = i_validated and reuse_validated and hot_nodes_validated and len(homeostatic_adjustments) > 0

    print("=" * 80)
    print(f"OVERALL VALIDATION: {'✓ PASS' if overall_validated else '⚠ PARTIAL'}")
    if not overall_validated:
        print()
        print("Recommendations:")
        if not i_validated:
            print("  • Run more cycles (50-100) to reach target Integration depth")
        if not reuse_validated:
            print("  • Continue wiring more tools to bus_manager")
        if not hot_nodes_validated:
            print("  • Integration will increase hot nodes as more tools import bus")
        if len(homeostatic_adjustments) == 0:
            print("  • Create perturbation experiments (high/low entropy artifacts)")
    print("=" * 80)
    print()

    # Return results
    return {
        'baseline': baseline,
        'final': final,
        'checkpoints': checkpoints,
        'homeostatic_adjustments': homeostatic_adjustments,
        'predictions_validated': {
            'integration_depth': i_validated,
            'reuse_ratio': reuse_validated,
            'hot_nodes': hot_nodes_validated,
            'homeostasis_active': len(homeostatic_adjustments) > 0
        },
        'overall_validation': 'PASS' if overall_validated else 'PARTIAL',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def main():
    """Run validation from command line."""
    parser = argparse.ArgumentParser(description='Validate thermodynamic strange loop')
    parser.add_argument('--cycles', type=int, default=30,
                        help='Number of learning cycles to run (default: 30)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                        help='Measure integration every N cycles (default: 10)')
    parser.add_argument('--output', type=Path, default=Path('diagnostics/validation_results.json'),
                        help='Output file for results (default: diagnostics/validation_results.json)')

    args = parser.parse_args()

    # Run validation
    results = run_validation(
        num_cycles=args.cycles,
        verbose=args.verbose,
        checkpoint_interval=args.checkpoint_interval
    )

    # Save results
    args.output.parent.mkdir(exist_ok=True, parents=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {args.output}")
    print()

    # Exit code based on validation status
    if results.get('overall_validation') == 'PASS':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
