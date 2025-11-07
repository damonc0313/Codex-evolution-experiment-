#!/usr/bin/env python3
"""
REAL Ablation Experiment - NO SIMULATION

Actually comments out code and runs real learning cycles.
Measures actual degradation from disabled components.

Promise: No more simulated degradation. This is REAL.

Author: Claude Code (REAL EXECUTION ONLY)
Date: 2025-11-07
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add tools to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

def backup_learning_kernel():
    """Backup original learning_kernel.py"""
    original = ROOT / "tools" / "learning_kernel.py"
    backup = ROOT / "tools" / "learning_kernel.py.backup"
    shutil.copy2(original, backup)
    print(f"✓ Backed up learning_kernel.py")
    return backup

def restore_learning_kernel(backup_path):
    """Restore original learning_kernel.py"""
    original = ROOT / "tools" / "learning_kernel.py"
    shutil.copy2(backup_path, original)
    print(f"✓ Restored learning_kernel.py")

def create_ablated_kernel(component: str):
    """
    Create ablated version by commenting out component initialization and usage.

    Returns True if successful, False otherwise.
    """
    kernel_path = ROOT / "tools" / "learning_kernel.py"
    code = kernel_path.read_text()

    if component == "reward_model":
        # Comment out reward model initialization and usage
        code = code.replace(
            "self.reward_model = RewardModel(",
            "# ABLATION: Disabled reward_model\n        # self.reward_model = RewardModel("
        )
        code = code.replace(
            "        reward_info = self.reward_model.compute_reward(metrics, artifact_metadata)",
            "        # ABLATION: Skip reward computation\n        reward_info = {'reward': 0.5, 'baseline': 0.5, 'advantage': 0.0}"
        )

    elif component == "policy_updater":
        # Comment out policy updater initialization and usage
        code = code.replace(
            "self.policy_updater = PolicyUpdater(",
            "# ABLATION: Disabled policy_updater\n        # self.policy_updater = PolicyUpdater("
        )
        code = code.replace(
            "        policy_update = self.policy_updater.update_policy(",
            "        # ABLATION: Skip policy update\n        policy_update = {'policy_before': {}, 'policy_after': {}, 'weight_delta': 0.0}"
        )

    elif component == "metrics_engine":
        # Comment out metrics engine - return dummy metrics
        code = code.replace(
            "        metrics = self.metrics_engine.measure(artifact)",
            "        # ABLATION: Skip real measurement\n        metrics = {'correctness': 0.5, 'performance': 0.5, 'building_signal': 0.5, 'novelty': 0.5}"
        )

    else:
        print(f"✗ Unknown component: {component}")
        return False

    # Write ablated version
    kernel_path.write_text(code)
    print(f"✓ Created ablated kernel: {component} disabled")
    return True

def run_learning_cycles(n_cycles: int = 20):
    """Run N learning cycles and measure final quality"""

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

    # Select N artifacts
    artifact_files = sorted(artifacts_dir.glob("*.json"))[:n_cycles]

    if len(artifact_files) == 0:
        print("✗ No artifacts found - cannot run cycles")
        return None

    print(f"Running {len(artifact_files)} cycles...")

    qualities = []

    for i, artifact_path in enumerate(artifact_files, 1):
        # Load artifact
        with open(artifact_path) as f:
            artifact = json.load(f)

        # Process through kernel
        try:
            result = kernel.process_artifact(artifact, artifact_path.stem)

            # Extract quality metric
            metrics = result.get('metrics', {})
            quality = metrics.get('correctness', 0.0) * 0.5 + metrics.get('performance', 0.0) * 0.5
            qualities.append(quality)

            if i % 5 == 0:
                print(f"  Cycle {i}/{len(artifact_files)} - quality: {quality:.3f}")

        except Exception as e:
            print(f"  ✗ Cycle {i} failed: {e}")
            qualities.append(0.0)

    # Compute average quality
    if qualities:
        avg_quality = sum(qualities) / len(qualities)
        return avg_quality
    else:
        return None

def run_real_ablation_suite():
    """Run full ablation suite with REAL code modifications"""

    print("=" * 70)
    print("REAL ABLATION EXPERIMENT - NO SIMULATION")
    print("=" * 70)
    print("\nPromise: Only real execution. No synthetic data.")
    print("Method: Comment out actual code, run real cycles, measure degradation.")

    # Backup original
    backup_path = backup_learning_kernel()

    results = []

    try:
        # Run baseline (all components enabled)
        print("\n" + "-" * 70)
        print("BASELINE: All components enabled")
        print("-" * 70)
        baseline_quality = run_learning_cycles(n_cycles=20)

        if baseline_quality is None:
            print("✗ Baseline failed - aborting")
            restore_learning_kernel(backup_path)
            return

        print(f"\nBaseline quality: {baseline_quality:.4f}")

        # Run ablations
        components = ["reward_model", "policy_updater", "metrics_engine"]

        for component in components:
            print("\n" + "-" * 70)
            print(f"ABLATION: {component} disabled")
            print("-" * 70)

            # Restore original first
            restore_learning_kernel(backup_path)

            # Reload module to clear cache
            import importlib
            if 'learning_kernel' in sys.modules:
                del sys.modules['learning_kernel']

            # Create ablated version
            if not create_ablated_kernel(component):
                continue

            # Run cycles with ablation
            ablated_quality = run_learning_cycles(n_cycles=20)

            if ablated_quality is None:
                print(f"✗ Ablation {component} failed")
                continue

            # Compute degradation
            delta = baseline_quality - ablated_quality
            pct_degradation = (delta / baseline_quality) * 100

            print(f"\nAblated quality: {ablated_quality:.4f}")
            print(f"Δ Quality: {delta:.4f} ({pct_degradation:.1f}% degradation)")

            results.append({
                "component": component,
                "baseline_quality": baseline_quality,
                "ablated_quality": ablated_quality,
                "delta_quality": delta,
                "pct_degradation": pct_degradation,
                "method": "real_code_ablation",
                "n_cycles": 20
            })

        # Restore original
        restore_learning_kernel(backup_path)

        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "method": "real_ablations_no_simulation",
            "baseline_quality": baseline_quality,
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
            print(f"\n{result['component']}:")
            print(f"  Degradation: {result['pct_degradation']:.1f}%")
            print(f"  Status: {'✓ NECESSARY' if result['pct_degradation'] >= 15.0 else '⚠ OPTIONAL'}")

        print(f"\nResults saved: {output_path}")

    finally:
        # Always restore original
        restore_learning_kernel(backup_path)
        backup_path.unlink()  # Delete backup

if __name__ == "__main__":
    run_real_ablation_suite()
