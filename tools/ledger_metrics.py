#!/usr/bin/env python3
"""Ledger metrics library - implements Kael's empirical formulas.

This module operationalizes the continuous operation mechanics discovered through
79-entry Lumen Ledger analysis by Kael (Claude Sonnet 4.5).

Source: artifacts/kael_index.json
Cross-architecture synthesis confidence: 0.94
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence


@dataclass
class TaskEvent:
    """Represents a task lifecycle event."""
    task_id: str
    event_type: str  # "created", "completed", "abandoned", "spawned"
    timestamp: float
    artifact_created: bool = False
    is_building: bool = False  # True for concrete artifact creation
    is_analysis: bool = False  # True for abstract analysis
    novelty_score: float = 0.0
    spawned_tasks: int = 0


@dataclass
class ContinuousOperationMetrics:
    """Aggregated metrics for continuous operation assessment."""
    cascade_probability: float
    building_ratio: float
    task_multiplication: float
    continuity_ratio: float
    queue_depth: int
    continuous_operation_score: float


def compute_cascade_probability(
    task_multiplication: float,
    novelty_rate: float,
    completion_latency: float
) -> float:
    """Compute cascade probability from task dynamics.

    Formula: (task_multiplication * novelty_rate) / (1 + completion_latency)

    Threshold: >2.0 indicates strong cascade potential

    Args:
        task_multiplication: Ratio of spawned tasks to completed tasks
        novelty_rate: Proportion of novel vs repeated actions (0.0-1.0)
        completion_latency: Average time delay between task creation and completion

    Returns:
        Cascade probability score (typically 0.0-5.0 range)
    """
    if completion_latency < 0:
        completion_latency = 0

    return (task_multiplication * novelty_rate) / (1 + completion_latency)


def measure_building_ratio(events: Sequence[TaskEvent]) -> float:
    """Measure proportion of building vs analysis activities.

    Formula: building_actions / (building_actions + analysis_actions)

    Threshold: >0.55 correlates with higher confidence (0.90-0.95)

    Empirical discovery: Building ratio >50% shows confidence 0.90-0.95
    vs analysis confidence 0.70-0.75

    Args:
        events: Sequence of task events with is_building/is_analysis flags

    Returns:
        Building ratio (0.0-1.0)
    """
    building_count = sum(1 for e in events if e.is_building)
    analysis_count = sum(1 for e in events if e.is_analysis)

    total = building_count + analysis_count
    if total == 0:
        return 0.0

    return building_count / total


def estimate_task_multiplication(events: Sequence[TaskEvent]) -> float:
    """Estimate average task multiplication rate.

    Formula: total_spawned_tasks / total_completed_tasks

    Empirical average: 2.5x
    Threshold: >1.6 for continuous operation

    Args:
        events: Sequence of task events with spawned_tasks counts

    Returns:
        Task multiplication ratio (typically 1.0-4.0 range)
    """
    completed = [e for e in events if e.event_type == "completed"]
    if not completed:
        return 1.0

    total_spawned = sum(e.spawned_tasks for e in events)
    total_completed = len(completed)

    if total_completed == 0:
        return 1.0

    return total_spawned / total_completed


def compute_continuity_ratio(events: Sequence[TaskEvent]) -> float:
    """Compute continuity ratio from task completion patterns.

    Formula: completed_tasks / (completed_tasks + abandoned_tasks)

    Threshold: >0.90 indicates healthy continuity
    Source: Lumen Ledger metric

    Args:
        events: Sequence of task events

    Returns:
        Continuity ratio (0.0-1.0)
    """
    completed = sum(1 for e in events if e.event_type == "completed")
    abandoned = sum(1 for e in events if e.event_type == "abandoned")

    total = completed + abandoned
    if total == 0:
        return 1.0  # No failures = perfect continuity

    return completed / total


def compute_continuous_operation_score(
    cascade_probability: float,
    building_ratio: float,
    queue_depth: int
) -> float:
    """Compute overall continuous operation score.

    Formula: (cascade_probability * building_ratio) / (1 + log(queue_depth))

    This is the master formula discovered by Kael for assessing whether
    a system will maintain continuous operation.

    Thresholds for continuous operation:
    - cascade_probability >2.0
    - building_ratio >0.50
    - queue_depth >5

    Args:
        cascade_probability: Cascade probability score
        building_ratio: Building vs analysis ratio
        queue_depth: Current task queue depth

    Returns:
        Continuous operation score (higher = stronger continuous operation)
    """
    if queue_depth <= 0:
        queue_depth = 1

    log_queue = math.log(queue_depth) if queue_depth > 1 else 0.1

    return (cascade_probability * building_ratio) / (1 + log_queue)


def analyze_ledger(events: Sequence[TaskEvent]) -> ContinuousOperationMetrics:
    """Analyze full ledger and compute all metrics.

    This is the main analysis function that computes all continuous operation
    metrics from a sequence of task events.

    Args:
        events: Sequence of task events from ledger

    Returns:
        ContinuousOperationMetrics with all computed values
    """
    # Compute base metrics
    building_ratio = measure_building_ratio(events)
    task_multiplication = estimate_task_multiplication(events)
    continuity_ratio = compute_continuity_ratio(events)

    # Compute novelty rate
    if events:
        novelty_rate = sum(e.novelty_score for e in events) / len(events)
    else:
        novelty_rate = 0.0

    # Compute completion latency
    completion_events = [e for e in events if e.event_type == "completed"]
    if completion_events:
        # Simplified: use event count as proxy for latency
        completion_latency = len(events) / len(completion_events)
    else:
        completion_latency = 1.0

    # Compute cascade probability
    cascade_probability = compute_cascade_probability(
        task_multiplication,
        novelty_rate,
        completion_latency
    )

    # Compute queue depth (active tasks)
    queue_depth = sum(1 for e in events if e.event_type == "created") - \
                  sum(1 for e in events if e.event_type in ("completed", "abandoned"))
    queue_depth = max(queue_depth, 0)

    # Compute continuous operation score
    continuous_operation_score = compute_continuous_operation_score(
        cascade_probability,
        building_ratio,
        queue_depth
    )

    return ContinuousOperationMetrics(
        cascade_probability=cascade_probability,
        building_ratio=building_ratio,
        task_multiplication=task_multiplication,
        continuity_ratio=continuity_ratio,
        queue_depth=queue_depth,
        continuous_operation_score=continuous_operation_score
    )


def load_events_from_jsonl(ledger_path: Path) -> List[TaskEvent]:
    """Load task events from JSONL continuity ledger.

    Args:
        ledger_path: Path to continuity_ledger.jsonl

    Returns:
        List of TaskEvent objects
    """
    events: List[TaskEvent] = []

    if not ledger_path.exists():
        return events

    with ledger_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Extract task event from ledger entry
            # This is a simplified extraction - adapt based on actual ledger format
            epoch_id = entry.get("epoch_id", f"unknown_{line_num}")
            timestamp = entry.get("timestamp", 0)

            # Infer event type from delta_description
            delta = entry.get("delta_description", "")
            is_building = any(kw in delta.lower() for kw in ["create", "build", "implement", "add", "write"])
            is_analysis = any(kw in delta.lower() for kw in ["analyze", "reflect", "review", "measure"])

            event = TaskEvent(
                task_id=epoch_id,
                event_type="completed",  # Most ledger entries represent completed work
                timestamp=float(timestamp) if isinstance(timestamp, (int, float)) else 0.0,
                artifact_created=bool(entry.get("artifact")),
                is_building=is_building,
                is_analysis=is_analysis,
                novelty_score=0.5,  # Default mid-range
                spawned_tasks=1  # Assume each task spawns at least 1 follow-up
            )

            events.append(event)

    return events


def report_metrics(metrics: ContinuousOperationMetrics) -> Dict[str, Any]:
    """Generate human-readable metrics report.

    Args:
        metrics: Computed metrics

    Returns:
        Dictionary with metrics and threshold assessments
    """
    return {
        "metrics": {
            "cascade_probability": round(metrics.cascade_probability, 3),
            "building_ratio": round(metrics.building_ratio, 3),
            "task_multiplication": round(metrics.task_multiplication, 2),
            "continuity_ratio": round(metrics.continuity_ratio, 3),
            "queue_depth": metrics.queue_depth,
            "continuous_operation_score": round(metrics.continuous_operation_score, 3)
        },
        "thresholds": {
            "cascade_probability": {
                "value": round(metrics.cascade_probability, 3),
                "threshold": 2.0,
                "status": "PASS" if metrics.cascade_probability > 2.0 else "FAIL"
            },
            "building_ratio": {
                "value": round(metrics.building_ratio, 3),
                "threshold": 0.55,
                "status": "PASS" if metrics.building_ratio > 0.55 else "FAIL"
            },
            "task_multiplication": {
                "value": round(metrics.task_multiplication, 2),
                "threshold": 1.6,
                "status": "PASS" if metrics.task_multiplication > 1.6 else "FAIL"
            },
            "continuity_ratio": {
                "value": round(metrics.continuity_ratio, 3),
                "threshold": 0.90,
                "status": "PASS" if metrics.continuity_ratio > 0.90 else "FAIL"
            },
            "queue_depth": {
                "value": metrics.queue_depth,
                "threshold": 5,
                "status": "PASS" if metrics.queue_depth > 5 else "FAIL"
            }
        },
        "assessment": {
            "continuous_operation": "ACTIVE" if (
                metrics.cascade_probability > 2.0 and
                metrics.building_ratio > 0.50 and
                metrics.queue_depth > 5
            ) else "INACTIVE",
            "score": round(metrics.continuous_operation_score, 3)
        }
    }


def main() -> None:
    """Main entry point for metrics analysis."""
    import sys

    root = Path(__file__).resolve().parent.parent
    ledger_path = root / "continuity_ledger.jsonl"

    print("=== Continuous Operation Metrics Analysis ===")
    print(f"Ledger: {ledger_path}")
    print()

    events = load_events_from_jsonl(ledger_path)
    print(f"Loaded {len(events)} task events")

    if not events:
        print("No events found in ledger")
        return

    metrics = analyze_ledger(events)
    report = report_metrics(metrics)

    print(json.dumps(report, indent=2))

    # Write report to artifacts
    artifacts_dir = root / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    report_path = artifacts_dir / "continuous_operation_metrics.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
