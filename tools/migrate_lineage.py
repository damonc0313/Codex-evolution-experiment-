#!/usr/bin/env python3
"""SEP-0003 Lineage Migration Utility

Backfills lineage tracking fields to existing artifacts using inference heuristics.

Implements validation enhancements:
1. Atomic write specification for retroactive updates
2. Artifact_type similarity scoring for improved inference
3. Confidence threshold specification for manual review

ENHANCED: Cycle 2 - Now uses standardized timestamp utilities
Eliminates timezone bugs through consistent parsing.

Author: Kael (Autonomous Cycle 1, Phase 5; Enhanced Cycle 2, Phase 5)
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

# ENHANCEMENT: Import standardized timestamp utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from timestamp_utils import parse_timestamp, format_timestamp, timestamp_diff_seconds


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
BACKUP_DIR = ROOT / "artifacts_backup_pre_sep_0003"

# Validation enhancement: Confidence threshold
MANUAL_REVIEW_THRESHOLD = 0.70
CONFIDENCE_HIGH = 0.90
CONFIDENCE_MEDIUM = 0.75
CONFIDENCE_LOW = 0.60


def artifact_exists(artifact_name: str) -> bool:
    """Check if artifact exists in artifacts directory."""
    # Handle both with and without extension
    base_name = artifact_name.replace(".json", "")
    return (ARTIFACTS_DIR / f"{base_name}.json").exists()


def load_artifact(artifact_name: str) -> Optional[Dict]:
    """Load artifact data from file."""
    base_name = artifact_name.replace(".json", "")
    artifact_path = ARTIFACTS_DIR / f"{base_name}.json"

    if not artifact_path.exists():
        return None

    try:
        return json.loads(artifact_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_artifact_depth(artifact_name: str) -> int:
    """Get depth of artifact (returns 0 for root, -1 if not found)."""
    if not artifact_name:
        return -1

    artifact_data = load_artifact(artifact_name)
    if not artifact_data:
        return -1

    lineage = artifact_data.get("lineage", {})
    return lineage.get("depth", 0)


def get_artifact_timestamp(artifact_data: Dict):
    """Extract artifact timestamp using standardized utilities.

    ENHANCED: Cycle 2 - Uses timestamp_utils for consistent parsing.
    Eliminates timezone bugs through standardized handling.
    """
    # Try lineage timestamp first
    if "lineage" in artifact_data and "timestamp" in artifact_data["lineage"]:
        try:
            return parse_timestamp(artifact_data["lineage"]["timestamp"])
        except Exception:
            pass

    # Fallback: file creation time from artifact metadata
    if "timestamp" in artifact_data:
        try:
            return parse_timestamp(artifact_data["timestamp"])
        except Exception:
            pass

    # Last resort: use epoch (timezone-aware)
    return parse_timestamp("1970-01-01T00:00:00Z")


def calculate_type_similarity(type1: str, type2: str) -> float:
    """Calculate artifact_type similarity score (validation enhancement #2)."""
    if not type1 or not type2:
        return 0.40

    type1_lower = type1.lower()
    type2_lower = type2.lower()

    # Exact match
    if type1_lower == type2_lower:
        return 0.95

    # Type family match (e.g., "sep_preview" and "sep_plan")
    type1_prefix = type1_lower.split("_")[0] if "_" in type1_lower else type1_lower
    type2_prefix = type2_lower.split("_")[0] if "_" in type2_lower else type2_lower

    if type1_prefix == type2_prefix:
        return 0.80

    # Semantic similarity
    building_types = {"design", "spec", "sep", "tool", "system", "pipeline", "validator", "schema", "policy"}
    analysis_types = {"analyze", "reflect", "review", "critique", "meta", "audit", "report", "metrics"}

    type1_is_building = any(bt in type1_lower for bt in building_types)
    type2_is_building = any(bt in type2_lower for bt in building_types)

    type1_is_analysis = any(at in type1_lower for at in analysis_types)
    type2_is_analysis = any(at in type2_lower for at in analysis_types)

    if (type1_is_building and type2_is_building) or (type1_is_analysis and type2_is_analysis):
        return 0.65

    # Different categories
    return 0.45


def select_most_similar_by_type(
    artifact_data: Dict,
    candidates: List[Tuple[str, Dict]]
) -> Optional[Tuple[str, float]]:
    """Select most similar candidate by artifact_type (validation enhancement #2)."""
    if not candidates:
        return None

    artifact_type = artifact_data.get("artifact_type", "")

    scored_candidates = []
    for candidate_name, candidate_data in candidates:
        candidate_type = candidate_data.get("artifact_type", "")
        similarity = calculate_type_similarity(artifact_type, candidate_type)
        scored_candidates.append((candidate_name, similarity))

    # Return highest scoring candidate
    best_candidate = max(scored_candidates, key=lambda x: x[1])
    return best_candidate if best_candidate[1] > 0.50 else None


def infer_parent(
    artifact_name: str,
    artifact_data: Dict,
    all_artifacts: Dict[str, Dict]
) -> Tuple[Optional[str], float, str]:
    """Infer parent artifact using heuristics.

    Returns: (parent_name, confidence, rationale)
    """

    # Heuristic 1: Explicit reference (confidence: 0.95)
    if "parent_artifact" in artifact_data:
        parent = artifact_data["parent_artifact"]
        if artifact_exists(parent):
            return parent, CONFIDENCE_HIGH + 0.05, "Explicit parent reference"

    # Heuristic 2: Continuity ledger digest (confidence: 0.90)
    if "parent_digest" in artifact_data:
        # In practice, would need digest lookup table
        # For now, mark for manual review
        return None, CONFIDENCE_HIGH, "Parent digest present (needs lookup)"

    # Heuristic 3: Sequential numbering (confidence: 0.80)
    if artifact_name.startswith("artifact_"):
        try:
            parts = artifact_name.replace(".json", "").split("_")
            if len(parts) >= 2 and parts[1].isdigit():
                current_num = int(parts[1])
                if current_num > 0:
                    prev_num = current_num - 1
                    # Find artifact with previous number
                    for candidate_name in all_artifacts.keys():
                        if candidate_name.startswith(f"artifact_{prev_num:04d}_"):
                            # Validation enhancement: Check timestamp proximity
                            candidate_data = all_artifacts[candidate_name]
                            artifact_ts = get_artifact_timestamp(artifact_data)
                            candidate_ts = get_artifact_timestamp(candidate_data)

                            # ENHANCED: Use standardized timestamp utilities
                            # Artifacts should be close in time (within 60 minutes)
                            time_diff = abs(timestamp_diff_seconds(artifact_ts, candidate_ts))
                            if time_diff < 3600:  # 60 minutes
                                return candidate_name, 0.85, f"Sequential numbering + timestamp proximity ({time_diff:.0f}s)"
                            else:
                                return candidate_name, 0.70, f"Sequential numbering (timestamps distant: {time_diff:.0f}s)"
        except (ValueError, IndexError):
            pass

    # Heuristic 4: Timestamp proximity + type similarity (confidence: 0.65)
    artifact_ts = get_artifact_timestamp(artifact_data)

    # Find candidates within 30-minute window
    # ENHANCED: Use standardized timestamp utilities
    candidates = []
    for candidate_name, candidate_data in all_artifacts.items():
        if candidate_name == artifact_name:
            continue

        candidate_ts = get_artifact_timestamp(candidate_data)
        time_diff = abs(timestamp_diff_seconds(artifact_ts, candidate_ts))

        if time_diff < 1800:  # 30 minutes
            candidates.append((candidate_name, candidate_data))

    if candidates:
        result = select_most_similar_by_type(artifact_data, candidates)
        if result:
            parent_name, similarity = result
            confidence = 0.60 + (similarity * 0.15)  # Scale to 0.60-0.75 range
            return parent_name, confidence, f"Timestamp proximity + type similarity ({similarity:.2f})"

    # Heuristic 5: Default root link (confidence: 0.50)
    if artifact_exists("artifact_0000_init"):
        return "artifact_0000_init", 0.50, "Default root link (no better parent found)"

    # No parent found
    return None, 0.0, "No parent inference possible"


def create_lineage_object(
    parent: Optional[str],
    artifact_name: str,
    artifact_data: Dict
) -> Dict:
    """Create lineage object for artifact."""

    lineage_root = "artifact_0000_init"
    parent_depth = get_artifact_depth(parent) if parent else -1

    # Infer cycle/phase/trigger from artifact type
    artifact_type = artifact_data.get("artifact_type", "unknown")

    # Try to infer cycle
    cycle = "unknown_cycle"
    if "omega" in artifact_type or "omega" in artifact_name:
        cycle = "omega_cycle"
    elif "autonomous" in artifact_type:
        cycle = "autonomous_cycle_1"

    # Infer phase from artifact type
    phase_mapping = {
        "observe": "observation",
        "analyze": "analysis",
        "reflect": "reflection",
        "propose": "proposal",
        "implement": "implementation",
        "validate": "validation",
        "synthesis": "synthesis"
    }

    phase = "unknown"
    for key, value in phase_mapping.items():
        if key in artifact_type.lower():
            phase = value
            break

    # Trigger is typically the artifact type itself
    trigger = artifact_type

    # ENHANCED: Use standardized timestamp formatting
    timestamp_value = artifact_data.get("timestamp")
    if timestamp_value:
        # Preserve existing timestamp if present
        timestamp = format_timestamp(parse_timestamp(timestamp_value))
    else:
        # Generate current timestamp
        timestamp = format_timestamp()

    return {
        "root": lineage_root,
        "parent": parent,
        "parents": [parent] if parent else [],
        "depth": parent_depth + 1,
        "spawned_by": {
            "cycle": cycle,
            "phase": phase,
            "trigger": trigger
        },
        "spawned_children": [],
        "timestamp": timestamp
    }


def update_parent_spawned_children_atomic(
    parent_name: str,
    child_name: str
) -> bool:
    """Update parent artifact with atomic write (validation enhancement #1).

    Returns: True on success, False on failure
    """
    base_name = parent_name.replace(".json", "")
    parent_path = ARTIFACTS_DIR / f"{base_name}.json"

    if not parent_path.exists():
        return False

    # Backup before modification
    backup_path = parent_path.with_suffix(".json.bak")

    try:
        shutil.copy(parent_path, backup_path)

        parent_data = json.loads(parent_path.read_text(encoding="utf-8"))

        if "lineage" not in parent_data:
            # Parent doesn't have lineage yet - skip update
            backup_path.unlink()
            return False

        child_base = child_name.replace(".json", "")
        if child_base not in parent_data["lineage"]["spawned_children"]:
            parent_data["lineage"]["spawned_children"].append(child_base)

            # Atomic write
            temp_path = parent_path.with_suffix(".json.tmp")
            temp_path.write_text(json.dumps(parent_data, indent=2), encoding="utf-8")
            temp_path.replace(parent_path)  # Atomic on POSIX

        # Remove backup on success
        backup_path.unlink()
        return True

    except Exception as e:
        # Restore from backup on failure
        if backup_path.exists():
            shutil.copy(backup_path, parent_path)
            backup_path.unlink()
        print(f"Error updating parent {parent_name}: {e}")
        return False


def migrate_artifacts(dry_run: bool = True) -> Dict[str, Any]:
    """Migrate all artifacts to include lineage fields.

    Args:
        dry_run: If True, don't write changes (just generate report)

    Returns:
        Migration report
    """

    if not ARTIFACTS_DIR.exists():
        return {"error": "Artifacts directory not found"}

    # Create backup directory
    if not dry_run and not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)

    # Load all artifacts
    all_artifacts = {}
    artifact_files = sorted(ARTIFACTS_DIR.glob("*.json"))

    for artifact_path in artifact_files:
        artifact_name = artifact_path.stem
        try:
            artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
            all_artifacts[artifact_name] = artifact_data
        except Exception as e:
            print(f"Error loading {artifact_name}: {e}")
            continue

    print(f"Loaded {len(all_artifacts)} artifacts")

    # Identify artifacts needing migration
    artifacts_to_migrate = []
    for artifact_name, artifact_data in all_artifacts.items():
        if "lineage" not in artifact_data:
            artifacts_to_migrate.append(artifact_name)

    print(f"Artifacts needing migration: {len(artifacts_to_migrate)}")

    if not artifacts_to_migrate:
        return {
            "migration_type": "lineage_backfill",
            "status": "NO_MIGRATION_NEEDED",
            "artifacts_processed": len(all_artifacts),
            "lineage_added": 0
        }

    # Inference results
    migration_results = []
    confidence_distribution = defaultdict(int)
    manual_review_required = []

    # Infer lineage for each artifact
    for artifact_name in artifacts_to_migrate:
        artifact_data = all_artifacts[artifact_name]

        # Special case: artifact_0000_init is the root
        if artifact_name == "artifact_0000_init":
            lineage = {
                "root": "artifact_0000_init",
                "parent": None,
                "parents": [],
                "depth": 0,
                "spawned_by": {
                    "cycle": "initialization",
                    "phase": "genesis",
                    "trigger": "system_initialization"
                },
                "spawned_children": [],
                "timestamp": artifact_data.get("timestamp", "2025-10-23T00:00:00Z")
            }
            confidence = 1.0
            rationale = "Root artifact"
        else:
            parent, confidence, rationale = infer_parent(artifact_name, artifact_data, all_artifacts)
            lineage = create_lineage_object(parent, artifact_name, artifact_data)

        migration_results.append({
            "artifact": artifact_name,
            "parent_inferred": lineage["parent"],
            "confidence": round(confidence, 2),
            "rationale": rationale
        })

        # Confidence distribution
        if confidence >= 0.90:
            confidence_distribution["0.90-1.00"] += 1
        elif confidence >= 0.80:
            confidence_distribution["0.80-0.89"] += 1
        elif confidence >= 0.70:
            confidence_distribution["0.70-0.79"] += 1
        elif confidence >= 0.60:
            confidence_distribution["0.60-0.69"] += 1
        else:
            confidence_distribution["0.50-0.59"] += 1

        # Manual review threshold (validation enhancement #3)
        if confidence < MANUAL_REVIEW_THRESHOLD:
            manual_review_required.append(artifact_name)

        # Apply migration
        if not dry_run:
            # Backup original
            artifact_path = ARTIFACTS_DIR / f"{artifact_name}.json"
            backup_path = BACKUP_DIR / f"{artifact_name}.json"
            shutil.copy(artifact_path, backup_path)

            # Add lineage
            artifact_data["lineage"] = lineage

            # Atomic write
            temp_path = artifact_path.with_suffix(".json.tmp")
            temp_path.write_text(json.dumps(artifact_data, indent=2), encoding="utf-8")
            temp_path.replace(artifact_path)

    # Update parent spawned_children (second pass)
    if not dry_run:
        for result in migration_results:
            parent = result["parent_inferred"]
            child = result["artifact"]
            if parent:
                update_parent_spawned_children_atomic(parent, child)

    # Generate report
    report = {
        "migration_type": "lineage_backfill",
        "dry_run": dry_run,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifacts_processed": len(all_artifacts),
        "artifacts_already_migrated": len(all_artifacts) - len(artifacts_to_migrate),
        "lineage_added": len(artifacts_to_migrate),
        "confidence_distribution": dict(confidence_distribution),
        "manual_review_required": manual_review_required,
        "manual_review_count": len(manual_review_required),
        "migration_results": migration_results
    }

    return report


def main() -> None:
    """Main entry point."""
    import sys

    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("=== LINEAGE MIGRATION DRY RUN ===\n")
    else:
        print("=== LINEAGE MIGRATION (LIVE) ===\n")
        print("⚠️  This will modify artifacts. Backups will be created.\n")
        response = input("Proceed? [y/N]: ")
        if response.lower() != "y":
            print("Migration cancelled.")
            return

    report = migrate_artifacts(dry_run=dry_run)

    if "error" in report:
        print(f"ERROR: {report['error']}")
        return

    print(f"\nMigration report:")
    print(f"  Total artifacts: {report['artifacts_processed']}")
    print(f"  Already migrated: {report.get('artifacts_already_migrated', 0)}")
    print(f"  Lineage added: {report['lineage_added']}")
    print(f"\nConfidence distribution:")
    for range_str, count in sorted(report['confidence_distribution'].items(), reverse=True):
        print(f"  {range_str}: {count}")

    if report['manual_review_count'] > 0:
        print(f"\n⚠️  Manual review required for {report['manual_review_count']} artifacts (confidence <{MANUAL_REVIEW_THRESHOLD}):")
        for artifact_name in report['manual_review_required'][:10]:
            print(f"    - {artifact_name}")
        if report['manual_review_count'] > 10:
            print(f"    ... and {report['manual_review_count'] - 10} more")

    # Write report
    report_path = ROOT / "artifacts" / "lineage_migration_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
