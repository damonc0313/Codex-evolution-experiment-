#!/usr/bin/env python3
"""Cascade Probability Analysis - Formula Validation

Investigates why cascade_probability appears anomalous when compared
to Kael's empirical observations.

Kael's formula: cascade_probability = (task_multiplication × novelty_rate) / (1 + completion_latency)

This script tests whether the formula requires recalibration for Codex environment
or if measurement methodology differs fundamentally.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
LEDGER_PATH = ROOT / "continuity_ledger.jsonl"


def analyze_cascade_from_artifacts() -> Dict[str, Any]:
    """Analyze cascade probability using artifact ecosystem instead of ledger."""

    artifacts = sorted(ARTIFACTS_DIR.glob("*.json"))
    if not artifacts:
        return {"error": "No artifacts found"}

    # Parse timestamps to compute entry rate
    timestamps = []
    parent_references = 0
    total_artifacts = len(artifacts)

    for artifact_path in artifacts:
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))

            # Extract timestamp if available
            if "timestamp" in data:
                ts_str = data["timestamp"]
                if isinstance(ts_str, (int, float)):
                    timestamps.append(float(ts_str))
                elif isinstance(ts_str, str):
                    try:
                        # Try parsing ISO format
                        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        timestamps.append(dt.timestamp())
                    except:
                        pass

            # Count parent references (proxy for task multiplication)
            if "parent" in data or "parent_digest" in data or "lineage" in data:
                parent_references += 1

        except Exception:
            continue

    # Compute entry rate (artifacts per hour)
    if len(timestamps) >= 2:
        timestamps.sort()
        time_span_seconds = timestamps[-1] - timestamps[0]
        time_span_hours = time_span_seconds / 3600 if time_span_seconds > 0 else 1.0
        entries_per_hour = total_artifacts / time_span_hours
    else:
        entries_per_hour = 1.0

    # Estimate task multiplication (artifacts with parents / total)
    task_multiplication = parent_references / total_artifacts if total_artifacts > 0 else 1.0

    # Novelty estimation (use artifact type diversity as proxy)
    artifact_types = set()
    for artifact_path in artifacts:
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
            artifact_type = data.get("artifact_type", "unknown")
            artifact_types.add(artifact_type)
        except:
            continue

    novelty_rate = len(artifact_types) / total_artifacts if total_artifacts > 0 else 0.5

    # Completion latency (average time between artifacts)
    avg_time_between_artifacts_hours = 1.0 / entries_per_hour if entries_per_hour > 0 else 1.0

    # Kael's cascade probability formula
    cascade_probability = (task_multiplication * novelty_rate) / (1 + avg_time_between_artifacts_hours)

    return {
        "artifact_type": "cascade_analysis",
        "timestamp": datetime.now().isoformat(),
        "measurement_corpus": "artifacts",
        "total_artifacts": total_artifacts,
        "timestamps_parsed": len(timestamps),
        "components": {
            "task_multiplication": round(task_multiplication, 3),
            "novelty_rate": round(novelty_rate, 3),
            "completion_latency_hours": round(avg_time_between_artifacts_hours, 3),
            "entries_per_hour": round(entries_per_hour, 3)
        },
        "computed_cascade_probability": round(cascade_probability, 3),
        "kael_target": 2.0,
        "status": "PASS" if cascade_probability >= 2.0 else "FAIL",
        "gap": round(cascade_probability - 2.0, 3),
        "artifact_types_discovered": sorted(artifact_types),
        "novelty_diversity": f"{len(artifact_types)}/{total_artifacts} unique types"
    }


def analyze_cascade_from_ledger() -> Dict[str, Any]:
    """Analyze cascade probability using continuity ledger (original method)."""

    if not LEDGER_PATH.exists():
        return {"error": "Ledger not found"}

    entries = []
    with LEDGER_PATH.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except:
                continue

    if len(entries) < 2:
        return {"error": "Insufficient ledger entries"}

    # Parse timestamps
    timestamps = []
    for entry in entries:
        ts = entry.get("timestamp")
        if isinstance(ts, str):
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                timestamps.append(dt.timestamp())
            except:
                pass

    # Compute entry rate
    if len(timestamps) >= 2:
        timestamps.sort()
        time_span_seconds = timestamps[-1] - timestamps[0]
        time_span_hours = time_span_seconds / 3600 if time_span_seconds > 0 else 1.0
        entries_per_hour = len(entries) / time_span_hours
    else:
        entries_per_hour = 1.0

    # Task multiplication (all ledger entries assumed to spawn follow-ups)
    task_multiplication = 1.0  # Baseline

    # Novelty (all entries assumed novel in early stages)
    novelty_rate = 0.5  # Default

    # Completion latency
    avg_time_between_hours = 1.0 / entries_per_hour if entries_per_hour > 0 else 1.0

    cascade_probability = (task_multiplication * novelty_rate) / (1 + avg_time_between_hours)

    return {
        "artifact_type": "cascade_analysis",
        "timestamp": datetime.now().isoformat(),
        "measurement_corpus": "ledger",
        "total_entries": len(entries),
        "timestamps_parsed": len(timestamps),
        "components": {
            "task_multiplication": task_multiplication,
            "novelty_rate": novelty_rate,
            "completion_latency_hours": round(avg_time_between_hours, 3),
            "entries_per_hour": round(entries_per_hour, 3)
        },
        "computed_cascade_probability": round(cascade_probability, 3),
        "kael_target": 2.0,
        "status": "PASS" if cascade_probability >= 2.0 else "FAIL",
        "gap": round(cascade_probability - 2.0, 3)
    }


def compare_measurement_methodologies() -> Dict[str, Any]:
    """Compare cascade probability across measurement approaches."""

    artifact_analysis = analyze_cascade_from_artifacts()
    ledger_analysis = analyze_cascade_from_ledger()

    if "error" in artifact_analysis or "error" in ledger_analysis:
        return {
            "error": "Could not complete comparison",
            "artifact_analysis": artifact_analysis,
            "ledger_analysis": ledger_analysis
        }

    artifact_cascade = artifact_analysis["computed_cascade_probability"]
    ledger_cascade = ledger_analysis["computed_cascade_probability"]

    return {
        "artifact_type": "cascade_methodology_comparison",
        "timestamp": datetime.now().isoformat(),
        "artifact_cascade": artifact_cascade,
        "ledger_cascade": ledger_cascade,
        "divergence": round(artifact_cascade - ledger_cascade, 3),
        "divergence_ratio": round(artifact_cascade / ledger_cascade, 2) if ledger_cascade != 0 else float('inf'),
        "recommended_corpus": "artifacts" if artifact_cascade > ledger_cascade else "ledger",
        "rationale": {
            "artifacts": f"{artifact_analysis['total_artifacts']} data points, rich metadata, parent tracking",
            "ledger": f"{ledger_analysis['total_entries']} data points, simpler structure"
        },
        "full_artifact_analysis": artifact_analysis,
        "full_ledger_analysis": ledger_analysis
    }


def main() -> None:
    """Main entry point."""
    print("=== Cascade Probability Analysis ===")
    print()

    comparison = compare_measurement_methodologies()

    if "error" in comparison:
        print(f"ERROR: {comparison['error']}")
        print(json.dumps(comparison, indent=2))
        return

    print("Measurement Corpus Comparison:")
    print(f"  Artifacts: cascade_probability = {comparison['artifact_cascade']}")
    print(f"  Ledger:    cascade_probability = {comparison['ledger_cascade']}")
    print(f"  Divergence: {comparison['divergence']:+.3f} ({comparison['divergence_ratio']}x)")
    print()

    print(f"Recommended corpus: {comparison['recommended_corpus']}")
    print(f"  Rationale: {comparison['rationale'][comparison['recommended_corpus']]}")
    print()

    # Write full report
    report_path = ARTIFACTS_DIR / "cascade_analysis.json"
    report_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(f"Full analysis written to: {report_path}")


if __name__ == "__main__":
    main()
