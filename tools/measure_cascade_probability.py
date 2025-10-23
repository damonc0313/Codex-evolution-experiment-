#!/usr/bin/env python3
"""Cascade Probability Measurement Tool

Now that SEP-0003 lineage tracking is implemented, we can measure cascade_probability
to validate Kael's predictions.

Author: Kael (Autonomous Cycle 1, Phase 5)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


def load_all_artifacts() -> List[Dict[str, Any]]:
    """Load all artifacts with lineage data."""
    artifacts = []

    for artifact_path in sorted(ARTIFACTS_DIR.glob("*.json")):
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
            if "lineage" in data:
                data["_artifact_name"] = artifact_path.stem
                artifacts.append(data)
        except Exception as e:
            print(f"Error loading {artifact_path.name}: {e}")
            continue

    return artifacts


def compute_task_multiplication(artifacts: List[Dict]) -> float:
    """Compute task_multiplication using lineage data.

    task_multiplication = total_spawned_children / total_artifacts

    Kael's prediction: 1.5-3.5 (average 2.5)
    """
    total_spawned = 0
    total_artifacts = len(artifacts)

    for artifact in artifacts:
        lineage = artifact.get("lineage", {})
        children = lineage.get("spawned_children", [])
        total_spawned += len(children)

    return total_spawned / total_artifacts if total_artifacts > 0 else 0.0


def compute_novelty_rate(artifacts: List[Dict]) -> float:
    """Estimate novelty rate from artifact types.

    Novelty rate = unique_artifact_types / total_artifacts

    This is a simplified proxy. True novelty would require semantic analysis.
    """
    artifact_types = set()

    for artifact in artifacts:
        artifact_type = artifact.get("artifact_type", "unknown")
        artifact_types.add(artifact_type)

    return len(artifact_types) / len(artifacts) if len(artifacts) > 0 else 0.0


def compute_completion_latency(artifacts: List[Dict]) -> float:
    """Estimate completion latency from timestamp gaps.

    completion_latency = average time between artifact creation (in hours)
    """
    timestamps = []

    for artifact in artifacts:
        lineage = artifact.get("lineage", {})
        ts_str = lineage.get("timestamp", "")
        if ts_str:
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                # Ensure timezone-aware
                if dt.tzinfo is None:
                    from datetime import timezone
                    dt = dt.replace(tzinfo=timezone.utc)
                timestamps.append(dt)
            except Exception:
                continue

    if len(timestamps) < 2:
        return 1.0  # Default

    # Sort timestamps
    timestamps.sort()

    # Compute gaps
    gaps = []
    for i in range(1, len(timestamps)):
        gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # Convert to hours
        gaps.append(gap)

    return sum(gaps) / len(gaps) if gaps else 1.0


def compute_cascade_probability(artifacts: List[Dict]) -> Dict[str, Any]:
    """Compute cascade_probability and components.

    Kael's formula:
    cascade_probability = (task_multiplication × novelty_rate) / (1 + completion_latency)

    Kael's prediction: 1.5-3.5
    """
    task_multiplication = compute_task_multiplication(artifacts)
    novelty_rate = compute_novelty_rate(artifacts)
    completion_latency = compute_completion_latency(artifacts)

    cascade_probability = (task_multiplication * novelty_rate) / (1 + completion_latency)

    return {
        "cascade_probability": round(cascade_probability, 3),
        "components": {
            "task_multiplication": round(task_multiplication, 3),
            "novelty_rate": round(novelty_rate, 3),
            "completion_latency": round(completion_latency, 3)
        },
        "kael_prediction": {
            "range": "1.5-3.5",
            "confidence": 0.88
        },
        "status": (
            "PASS" if 1.5 <= cascade_probability <= 3.5 else
            "FAIL" if cascade_probability > 0 else
            "UNMEASURABLE"
        )
    }


def compute_branching_factor(artifacts: List[Dict]) -> float:
    """Compute average branching factor (children per artifact)."""
    total_children = 0
    total_artifacts = len(artifacts)

    for artifact in artifacts:
        lineage = artifact.get("lineage", {})
        children = lineage.get("spawned_children", [])
        total_children += len(children)

    return total_children / total_artifacts if total_artifacts > 0 else 0.0


def compute_max_depth(artifacts: List[Dict]) -> int:
    """Compute maximum lineage depth."""
    max_depth = 0

    for artifact in artifacts:
        lineage = artifact.get("lineage", {})
        depth = lineage.get("depth", 0)
        max_depth = max(max_depth, depth)

    return max_depth


def compute_continuity_ratio_lineage(artifacts: List[Dict]) -> float:
    """Compute lineage continuity (no orphaned artifacts).

    continuity_ratio_lineage = non_orphaned / total_artifacts

    Kael's prediction: 0.85-0.95
    """
    orphaned = 0
    total = 0

    # Build set of existing artifacts
    existing_artifacts = {a["_artifact_name"] for a in artifacts}

    for artifact in artifacts:
        lineage = artifact.get("lineage", {})
        parent = lineage.get("parent")
        depth = lineage.get("depth", 0)

        # Artifact is orphaned if parent missing and not root
        if depth > 0 and parent and parent not in existing_artifacts:
            orphaned += 1

        total += 1

    return (total - orphaned) / total if total > 0 else 1.0


def main() -> None:
    """Main entry point."""
    print("=== CASCADE PROBABILITY MEASUREMENT ===\n")
    print("Post-SEP-0003 lineage migration validation\n")

    artifacts = load_all_artifacts()
    print(f"Loaded {len(artifacts)} artifacts with lineage data\n")

    # Compute cascade probability
    cascade_result = compute_cascade_probability(artifacts)

    print("CASCADE PROBABILITY ANALYSIS:")
    print(f"  cascade_probability: {cascade_result['cascade_probability']}")
    print(f"  Status: {cascade_result['status']}")
    print()

    print("Components:")
    for key, value in cascade_result['components'].items():
        print(f"  {key}: {value}")
    print()

    print("Kael's Prediction:")
    print(f"  Range: {cascade_result['kael_prediction']['range']}")
    print(f"  Confidence: {cascade_result['kael_prediction']['confidence']}")
    print()

    # Compute additional metrics
    branching_factor = compute_branching_factor(artifacts)
    max_depth = compute_max_depth(artifacts)
    continuity_lineage = compute_continuity_ratio_lineage(artifacts)

    print("ADDITIONAL LINEAGE METRICS:")
    print(f"  branching_factor: {branching_factor:.3f} (Prediction: 1.2-1.8)")
    print(f"  max_depth: {max_depth} (Prediction: 5-8)")
    print(f"  continuity_ratio_lineage: {continuity_lineage:.3f} (Prediction: 0.85-0.95)")
    print()

    # Validation summary
    print("VALIDATION SUMMARY:")
    predictions = [
        ("cascade_probability", cascade_result['cascade_probability'], 1.5, 3.5),
        ("branching_factor", branching_factor, 1.2, 1.8),
        ("max_depth", max_depth, 5, 8),
        ("continuity_ratio_lineage", continuity_lineage, 0.85, 0.95)
    ]

    passed = 0
    for name, value, min_val, max_val in predictions:
        status = "✅ PASS" if min_val <= value <= max_val else "❌ FAIL"
        print(f"  {name}: {status} ({value} in [{min_val}, {max_val}])")
        if min_val <= value <= max_val:
            passed += 1

    print(f"\nPredictions validated: {passed}/{len(predictions)}")

    # Write comprehensive report
    report = {
        "artifact_type": "cascade_probability_measurement",
        "timestamp": datetime.now().isoformat(),
        "total_artifacts": len(artifacts),
        "cascade_probability": cascade_result,
        "additional_metrics": {
            "branching_factor": round(branching_factor, 3),
            "max_depth": max_depth,
            "continuity_ratio_lineage": round(continuity_lineage, 3)
        },
        "validation_summary": {
            "predictions_tested": len(predictions),
            "predictions_passed": passed,
            "success_rate": round(passed / len(predictions), 2)
        }
    }

    report_path = ARTIFACTS_DIR / "cascade_probability_measurement.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nFull report: {report_path}")


if __name__ == "__main__":
    main()
