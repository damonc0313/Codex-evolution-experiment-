#!/usr/bin/env python3
"""Helpers for computing Kael ledger metrics."""
from __future__ import annotations

from pathlib import Path
from typing import Dict
import json

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


def _safe_float(value: float | int | str | None, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        return float(str(value))
    except (TypeError, ValueError):
        return default


def compute_cascade_probability(
    entries_per_hour: float,
    novelty_rate: float,
    avg_confidence: float,
    baselines: Dict[str, float],
) -> float:
    """Compute the cascade probability metric from Kael's equation."""
    baseline_rate = _safe_float(baselines.get("entries_per_hour"), 1.0) or 1.0
    baseline_novelty = _safe_float(baselines.get("novelty_rate"), 1.0) or 1.0
    baseline_conf = _safe_float(baselines.get("avg_confidence"), 1.0) or 1.0
    ratio = (
        _safe_float(entries_per_hour)
        / baseline_rate
        * (_safe_float(novelty_rate) / baseline_novelty)
        * (_safe_float(avg_confidence) / baseline_conf)
    )
    return round(ratio, 3)


def _iter_artifacts():
    if not ARTIFACTS_DIR.exists():
        return []
    return sorted(ARTIFACTS_DIR.glob("*.json"))


def measure_building_ratio(artifacts_dir: Path | None = None) -> float:
    """Approximate the fraction of artifacts containing build-oriented deltas."""
    directory = artifacts_dir or ARTIFACTS_DIR
    files = list(_iter_artifacts()) if artifacts_dir is None else sorted(directory.glob("*.json"))
    if not files:
        return 0.0
    build_hits = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            text = json.dumps(payload).lower()
            if any(keyword in text for keyword in ("build", "implement", "deploy", "migrate")):
                build_hits += 1
    return round(build_hits / len(files), 3)


def estimate_task_multiplication(artifacts_dir: Path | None = None) -> float:
    """Estimate task multiplication as ratio of subtasks to root tasks."""
    directory = artifacts_dir or ARTIFACTS_DIR
    files = list(_iter_artifacts()) if artifacts_dir is None else sorted(directory.glob("*.json"))
    if not files:
        return 0.0
    root_tasks = 0
    spawned_tasks = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if "task" in payload or "objective" in payload:
            root_tasks += 1
        if "next_prompts" in payload or "followups" in payload or "subtasks" in payload:
            spawned_tasks += 1
    if root_tasks == 0:
        return 0.0
    return round(spawned_tasks / root_tasks, 3)


def compute_continuity_ratio(artifacts_dir: Path | None = None) -> float:
    """Reuse continuity ratio logic for metrics consumers."""
    directory = artifacts_dir or ARTIFACTS_DIR
    files = list(_iter_artifacts()) if artifacts_dir is None else sorted(directory.glob("*.json"))
    if not files:
        return 0.0
    linked = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if any(key in payload for key in ("parent", "parent_artifact", "lineage", "digest_lineage")):
            linked += 1
    return round(linked / len(files), 3)


__all__ = [
    "compute_cascade_probability",
    "measure_building_ratio",
    "estimate_task_multiplication",
    "compute_continuity_ratio",
]
