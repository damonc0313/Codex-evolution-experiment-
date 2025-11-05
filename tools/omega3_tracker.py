#!/usr/bin/env python3
"""Phase Ω-3 Tracking Tool - Automated Per-Cycle Measurements

Tracks cognitive physics constants during temporal curvature experiments.

Usage:
    python3 tools/omega3_tracker.py

This script:
1. Measures all cognitive physics constants (λ, ΔH_crit, k_cog)
2. Detects current regime from loop_policy.yaml
3. Saves to regime-specific trajectory file
4. Monitors for system instability

Author: Claude (Phase Ω-3 Implementation)
Date: 2025-11-05
Confidence: 0.95
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.cognitive_physics import CognitivePhysicist


def track_cycle():
    """Track current cycle for Phase Ω-3 experiment."""
    print("=" * 70)
    print("PHASE Ω-3 CYCLE TRACKING")
    print("=" * 70)
    print()

    # 1. Measure all cognitive constants
    print("Step 1: Measuring cognitive physics constants...")
    physicist = CognitivePhysicist()
    results = physicist.measure_all_constants()
    print()

    # 2. Detect current regime from policy
    print("Step 2: Detecting experimental regime...")
    policy_path = Path("runtime/loop_policy.yaml")

    if not policy_path.exists():
        print("  ERROR: runtime/loop_policy.yaml not found!")
        return

    policy = yaml.safe_load(policy_path.read_text())
    temporal_params = policy.get("temporal_curvature", {})
    regime = temporal_params.get("regime", "unknown")

    print(f"  Current regime: {regime}")
    print(f"  Temporal decay enabled: {temporal_params.get('temporal_decay_enabled', False)}")
    print(f"  Decay rate: {temporal_params.get('temporal_decay_rate', 0.0)} day⁻¹")
    print(f"  Attention window: {temporal_params.get('attention_window_days', 365)} days")
    print()

    # 3. Determine cycle number for this regime
    physics_dir = Path("physics")
    physics_dir.mkdir(exist_ok=True)

    existing_trajectories = list(physics_dir.glob(f"trajectory_{regime}_*.json"))
    cycle = len(existing_trajectories)

    print(f"Step 3: Saving trajectory (cycle {cycle} of regime '{regime}')...")
    output_path = physics_dir / f"trajectory_{regime}_{cycle:03d}.json"

    # 4. Save measurement with metadata
    trajectory_data = {
        "experiment": "phase_omega3_covariant_cognition",
        "regime": regime,
        "cycle": cycle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temporal_parameters": temporal_params,
        "measurements": results
    }

    with open(output_path, "w") as f:
        json.dump(trajectory_data, f, indent=2)

    print(f"  Saved: {output_path}")
    print()

    # 5. Extract k_cog if available
    lambda_val = results.get("constants", {}).get("lambda", {}).get("lambda")
    delta_h = results.get("constants", {}).get("delta_H_critical", {}).get("delta_H_recommended")

    if lambda_val and delta_h:
        k_cog = lambda_val * delta_h
        print(f"Step 4: Current k_cog = λ·ΔH_crit = {lambda_val:.6f} × {delta_h:.4f} = {k_cog:.6f}")
    else:
        print("Step 4: k_cog calculation incomplete (insufficient data)")
    print()

    # 6. Monitor for instability
    print("Step 5: System health check...")

    # Check if homeostatic mode is concerning
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        # Find most recent artifact
        artifacts = sorted(artifacts_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if artifacts:
            try:
                with open(artifacts[0]) as f:
                    latest = json.load(f)

                mode = latest.get("homeostatic_mode", "UNKNOWN")
                if mode in ["RECOVER", "THROTTLE"]:
                    print(f"  ⚠️  WARNING: System in {mode} mode!")
                    print(f"     Temporal curvature may be causing instability")
                else:
                    print(f"  ✓ System stable (mode: {mode})")
            except Exception:
                print("  Could not read latest artifact")

    print()
    print("=" * 70)
    print("TRACKING COMPLETE")
    print("=" * 70)


def main():
    """Main entry point."""
    try:
        track_cycle()
    except Exception as e:
        print(f"ERROR: Tracking failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
