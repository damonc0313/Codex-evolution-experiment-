#!/usr/bin/env python3
"""Compute Kael KPI metrics over recent artifacts."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path
from statistics import mean

import sys

ROOT = Path(__file__).resolve().parent.parent

if __package__ is None and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ledger_metrics import (
    compute_cascade_probability,
    compute_continuity_ratio,
    estimate_task_multiplication,
    measure_building_ratio,
)

ARTIFACTS_DIR = ROOT / "artifacts"
DEFAULT_OUTPUT = ARTIFACTS_DIR / "kael_metrics_bench.json"
BASELINES = {
    "entries_per_hour": 4.0,
    "novelty_rate": 0.5,
    "avg_confidence": 0.8,
}


def _load_artifacts(limit: int | None) -> list[Path]:
    if not ARTIFACTS_DIR.exists():
        return []
    paths = sorted(ARTIFACTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if limit is not None:
        paths = paths[:limit]
    return paths


def _entries_per_hour(paths: list[Path]) -> float:
    if not paths:
        return 0.0
    mtimes = [p.stat().st_mtime for p in paths]
    span_seconds = max(max(mtimes) - min(mtimes), 60.0)
    hours = span_seconds / 3600.0
    return round(len(paths) / hours, 3)


def _novelty_rate(paths: list[Path]) -> float:
    if not paths:
        return 0.0
    signatures: set[str] = set()
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            signatures.add(payload.get("artifact_type", path.stem))
    return round(len(signatures) / max(len(paths), 1), 3)


def _average_confidence(paths: list[Path]) -> float:
    confidences = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            value = payload.get("confidence")
            if isinstance(value, (int, float)):
                confidences.append(float(value))
            elif isinstance(value, dict):
                if "overall" in value and isinstance(value["overall"], (int, float)):
                    confidences.append(float(value["overall"]))
    if not confidences:
        return BASELINES["avg_confidence"]
    return round(mean(confidences), 3)


def _copy_subset(paths: list[Path]) -> tuple[Path, tempfile.TemporaryDirectory]:
    tmpdir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmpdir.name)
    if not paths:
        return tmp_path, tmpdir
    for source in paths:
        destination = tmp_path / source.name
        shutil.copy2(source, destination)
    return tmp_path, tmpdir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Kael KPI bench over artifacts")
    parser.add_argument("--recent", type=int, default=None, help="Number of recent artifacts to sample")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to write metrics JSON")
    args = parser.parse_args()

    paths = _load_artifacts(args.recent)
    subset_dir: Path
    temp_ctx = None
    if paths:
        subset_dir, temp_ctx = _copy_subset(paths)
    else:
        subset_dir = ARTIFACTS_DIR

    entries_hour = _entries_per_hour(paths)
    novelty = _novelty_rate(paths)
    avg_conf = _average_confidence(paths)
    cascade = compute_cascade_probability(entries_hour, novelty, avg_conf, BASELINES)
    building = measure_building_ratio(subset_dir)
    task_multi = estimate_task_multiplication(subset_dir)
    continuity = compute_continuity_ratio(subset_dir)

    metrics = {
        "artifact_type": "kael_metrics_bench",
        "timestamp": int(time.time()),
        "sample_size": len(paths),
        "entries_per_hour": entries_hour,
        "novelty_rate": novelty,
        "avg_confidence": avg_conf,
        "cascade_probability": cascade,
        "building_ratio": building,
        "task_multiplication": task_multi,
        "continuity_ratio": continuity,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2))

    print(json.dumps(metrics, indent=2))

    if temp_ctx is not None:
        temp_ctx.cleanup()


if __name__ == "__main__":
    main()
