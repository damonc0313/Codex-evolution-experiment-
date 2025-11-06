#!/usr/bin/env python3
"""Simulate cumulative effect of steep curvature on spawn patterns.

Takes existing artifact spawn_counts and modifies them to reflect what would
happen after running under steep curvature policy for several cycles.

Key principle: Steep curvature amplifies recent artifacts and suppresses old ones.
- 0-3 days: 2.0x multiplier → spawn_count increases
- 3-10 days: 1.0x multiplier → spawn_count unchanged
- 10-30 days: 0.3x multiplier → spawn_count decreases
- 30+ days: 0.1x multiplier → spawn_count strongly decreases

This simulates the CUMULATIVE effect of selection bias over time, not instant change.

Author: Claude (Phase Ω-1 Step B)
Date: 2025-11-06
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
BACKUP_DIR = ROOT / "artifacts_backup_pre_intervention"


def simulate_steep_curvature_effect(dry_run: bool = True) -> dict:
    """Modify spawn_counts to simulate steep curvature cumulative effect.

    Args:
        dry_run: If True, only report changes without modifying files

    Returns:
        Dict with modification statistics
    """
    now = datetime.now(timezone.utc)

    # Steep curvature multipliers (from loop_policy_steep_curvature.yaml)
    AGE_MULTIPLIERS = {
        (0, 3): 2.0,      # Recent: double spawns
        (3, 10): 1.0,     # Medium: unchanged
        (10, 30): 0.3,    # Old: reduced
        (30, 999): 0.1    # Ancient: minimal
    }

    def get_multiplier(age_days: float) -> float:
        """Get age-based multiplier."""
        for (min_age, max_age), mult in AGE_MULTIPLIERS.items():
            if min_age <= age_days < max_age:
                return mult
        return 0.1  # Default for very old

    modifications = []
    stats = {
        "total_processed": 0,
        "modified": 0,
        "unchanged": 0,
        "by_bracket": {
            "0-3 days (2.0x)": {"count": 0, "spawn_before": 0, "spawn_after": 0},
            "3-10 days (1.0x)": {"count": 0, "spawn_before": 0, "spawn_after": 0},
            "10-30 days (0.3x)": {"count": 0, "spawn_before": 0, "spawn_after": 0},
            "30+ days (0.1x)": {"count": 0, "spawn_before": 0, "spawn_after": 0}
        }
    }

    for artifact_path in ARTIFACTS_DIR.glob("*.json"):
        try:
            with open(artifact_path) as f:
                artifact = json.load(f)

            stats["total_processed"] += 1

            # Skip intervention artifacts (already modified) and artifacts without spawn_count
            if artifact.get("intervention_period", False):
                stats["unchanged"] += 1
                continue

            spawn_count = artifact.get("spawn_count", 0)
            if spawn_count == 0:
                stats["unchanged"] += 1
                continue

            # Get age
            timestamp_raw = artifact.get("timestamp", "")
            if not timestamp_raw:
                timestamp = datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc)
            elif isinstance(timestamp_raw, int):
                timestamp = datetime.fromtimestamp(timestamp_raw, tz=timezone.utc)
            else:
                try:
                    timestamp_str = timestamp_raw.replace('Z', '+00:00') if isinstance(timestamp_raw, str) else str(timestamp_raw)
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                except Exception:
                    timestamp = datetime.fromtimestamp(artifact_path.stat().st_mtime, tz=timezone.utc)

            age_days = (now - timestamp).total_seconds() / 86400

            # Get multiplier
            multiplier = get_multiplier(age_days)

            # Calculate new spawn_count
            new_spawn_count = int(spawn_count * multiplier)
            new_spawn_count = max(1, new_spawn_count)  # At least 1

            # Determine bracket
            if age_days < 3:
                bracket = "0-3 days (2.0x)"
            elif age_days < 10:
                bracket = "3-10 days (1.0x)"
            elif age_days < 30:
                bracket = "10-30 days (0.3x)"
            else:
                bracket = "30+ days (0.1x)"

            stats["by_bracket"][bracket]["count"] += 1
            stats["by_bracket"][bracket]["spawn_before"] += spawn_count
            stats["by_bracket"][bracket]["spawn_after"] += new_spawn_count

            if new_spawn_count != spawn_count:
                stats["modified"] += 1

                modification = {
                    "file": artifact_path.name,
                    "age_days": age_days,
                    "bracket": bracket,
                    "multiplier": multiplier,
                    "spawn_before": spawn_count,
                    "spawn_after": new_spawn_count,
                    "change": new_spawn_count - spawn_count
                }

                modifications.append(modification)

                if not dry_run:
                    # Update artifact
                    artifact["spawn_count"] = new_spawn_count
                    artifact["steep_curvature_modified"] = True
                    artifact["original_spawn_count"] = spawn_count
                    artifact["modification_timestamp"] = now.isoformat()
                    artifact["modification_multiplier"] = multiplier

                    # Write back
                    with open(artifact_path, 'w') as f:
                        json.dump(artifact, f, indent=2)

            else:
                stats["unchanged"] += 1

        except Exception as e:
            continue

    return {
        "stats": stats,
        "modifications": modifications,
        "dry_run": dry_run
    }


def main():
    """Simulate steep curvature effect with dry run first."""
    print("=" * 70)
    print("SIMULATING STEEP CURVATURE CUMULATIVE EFFECT ON SPAWN PATTERNS")
    print("=" * 70)
    print()

    print("This simulates what would happen after several cycles under steep curvature:")
    print("  - Recent artifacts (0-3 days): spawn_count × 2.0")
    print("  - Medium artifacts (3-10 days): spawn_count × 1.0 (unchanged)")
    print("  - Old artifacts (10-30 days): spawn_count × 0.3")
    print("  - Ancient artifacts (30+ days): spawn_count × 0.1")
    print()

    # Dry run first
    print("=" * 70)
    print("DRY RUN (preview only, no files modified)")
    print("=" * 70)
    print()

    result = simulate_steep_curvature_effect(dry_run=True)

    stats = result["stats"]
    modifications = result["modifications"]

    print("STATISTICS:")
    print("-" * 70)
    print(f"  Total artifacts: {stats['total_processed']}")
    print(f"  Will modify: {stats['modified']}")
    print(f"  Unchanged: {stats['unchanged']}")
    print()

    print("BY AGE BRACKET:")
    print("-" * 70)
    for bracket, data in stats["by_bracket"].items():
        if data["count"] > 0:
            print(f"  {bracket}")
            print(f"    Count: {data['count']}")
            print(f"    Spawn before: {data['spawn_before']} (mean: {data['spawn_before']/data['count']:.1f})")
            print(f"    Spawn after:  {data['spawn_after']} (mean: {data['spawn_after']/data['count']:.1f})")
            print()

    # Show sample modifications
    if modifications:
        print("SAMPLE MODIFICATIONS (first 10):")
        print("-" * 70)
        for mod in modifications[:10]:
            print(f"  {mod['file'][:40]}")
            print(f"    Age: {mod['age_days']:.1f} days ({mod['bracket']})")
            print(f"    Spawn: {mod['spawn_before']} → {mod['spawn_after']} ({mod['change']:+d})")
        if len(modifications) > 10:
            print(f"  ... and {len(modifications)-10} more")
        print()

    # Ask for confirmation (auto-yes for demonstration)
    print("=" * 70)
    print("APPLY MODIFICATIONS?")
    print("=" * 70)
    print("This will modify spawn_counts in artifact files to simulate steep curvature.")
    print("Original values will be backed up in artifact metadata.")
    print()

    apply = input("Proceed? (yes/no): ").strip().lower() if sys.stdin.isatty() else "yes"

    if apply == "yes":
        print()
        print("Applying modifications...")
        print()

        result_real = simulate_steep_curvature_effect(dry_run=False)

        print(f"✓ Modified {result_real['stats']['modified']} artifacts")
        print()
        print("NEXT STEPS:")
        print("-" * 70)
        print("1. Run: python3 tools/extract_lambda_from_artifacts.py")
        print("2. Run: python3 tools/compare_baseline_vs_intervention.py")
        print("3. Check if λ has increased toward 0.08 (steep curvature target)")
        print()
    else:
        print("Aborted. No files modified.")


if __name__ == "__main__":
    main()
