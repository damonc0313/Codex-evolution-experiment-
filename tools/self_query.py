#!/usr/bin/env python3
"""Autonomous self-query generator with Kael policy awareness."""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

from tools.ledger_metrics import (
    compute_cascade_probability,
    compute_continuity_ratio,
    estimate_task_multiplication,
    measure_building_ratio,
)

ROOT = Path(__file__).resolve().parent.parent
USER_QUERY = ROOT / "runtime" / "user_query.txt"
POLICY_PATH = ROOT / "runtime" / "loop_policy.yaml"
STATE_PATH = ROOT / "runtime" / "loop_state.json"
ARTIFACTS_DIR = ROOT / "artifacts"
MANIFESTO = ROOT / "docs" / "agents.md"

DEFAULT_BASELINES = {
    "entries_per_hour": 1.0,
    "novelty_rate": 1.0,
    "avg_confidence": 1.0,
}


@dataclass
class Policy:
    novelty_floor: float = 0.25
    task_queue_min: float = 4
    building_ratio_min: float = 0.5
    task_multiplication_min: float = 1.2


def _load_policy() -> Policy:
    if not POLICY_PATH.exists():
        return Policy()
    data = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8")) or {}
    targets = data.get("continuous_operation_targets", {}) if isinstance(data, dict) else {}
    return Policy(
        novelty_floor=float(data.get("novelty_floor", 0.25) or 0.25),
        task_queue_min=float(targets.get("task_queue_min", 4)),
        building_ratio_min=float(targets.get("building_ratio_min", 0.5)),
        task_multiplication_min=float(targets.get("task_multiplication_min", 1.2)),
    )


def _manifest_digest() -> str:
    if not MANIFESTO.exists():
        return "00000000"
    import hashlib

    return hashlib.sha256(MANIFESTO.read_bytes()).hexdigest()[:8]


def _collect_artifacts() -> List[Path]:
    if not ARTIFACTS_DIR.exists():
        return []
    return sorted(ARTIFACTS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def _latest_artifact() -> Dict[str, object]:
    for path in _collect_artifacts():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _entries_per_hour(artifacts: List[Path]) -> float:
    if len(artifacts) < 2:
        return 0.0
    newest = artifacts[0].stat().st_mtime
    oldest = artifacts[min(len(artifacts) - 1, 20)].stat().st_mtime
    span_hours = max((newest - oldest) / 3600.0, 1 / 3600.0)
    return round(min(len(artifacts), 20) / span_hours, 3)


def _novelty_rate(artifacts: List[Path]) -> float:
    if not artifacts:
        return 0.0
    seen_titles: set[str] = set()
    novelty_hits = 0
    for path in artifacts[:20]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            title = str(payload.get("title") or payload.get("artifact_type") or path.name)
            if title not in seen_titles:
                novelty_hits += 1
            seen_titles.add(title)
    return round(novelty_hits / min(len(artifacts), 20), 3)


def _average_confidence(artifacts: List[Path]) -> float:
    if not artifacts:
        return 0.0
    confidences: List[float] = []
    for path in artifacts[:20]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            value = payload.get("confidence") or payload.get("kpis", {}).get("confidence")
            if isinstance(value, (int, float)):
                confidences.append(float(value))
    if not confidences:
        return 0.0
    return round(sum(confidences) / len(confidences), 3)


def _read_previous_query() -> str:
    if not USER_QUERY.exists():
        return ""
    return USER_QUERY.read_text(encoding="utf-8")


def _novelty_distance(candidate: str, previous: str) -> float:
    if not previous:
        return 1.0
    prev_tokens = set(previous.lower().split())
    cand_tokens = set(candidate.lower().split())
    if not cand_tokens:
        return 0.0
    overlap = len(prev_tokens & cand_tokens)
    return 1.0 - (overlap / len(cand_tokens))


def _build_candidates(policy: Policy, metrics: Dict[str, float]) -> List[str]:
    base = [
        "/trace 'Audit continuous operation KPIs and recommend gating adjustments'",
        "/bench 'Stress-test cascade probability estimators across last 5 runs'",
        "/plan 'Raise building ratio via targeted lineage schema upgrades'",
        "/evolve 'Prototype distributed task queue balancer with lineage hooks'",
    ]
    if metrics["building_ratio"] < policy.building_ratio_min:
        base.append(
            "/plan 'Launch building sprint to lift building_ratio above target; include artifact linkage report'"
        )
    if metrics["task_multiplication"] < policy.task_multiplication_min:
        base.append(
            "/bench 'Diagnose task multiplication bottlenecks and propose parallelization experiments'"
        )
    if metrics["continuity_ratio"] < 0.9:
        base.append(
            "/trace 'Map lineage gaps and design remediation checklist for continuity blocks'"
        )
    return base


def synthesize_query() -> Dict[str, object]:
    policy = _load_policy()
    artifacts = _collect_artifacts()
    entries_rate = _entries_per_hour(artifacts)
    novelty_rate = _novelty_rate(artifacts)
    avg_conf = _average_confidence(artifacts)
    cascade_probability = compute_cascade_probability(
        entries_rate, novelty_rate, avg_conf, DEFAULT_BASELINES
    )
    building_ratio = measure_building_ratio()
    task_multiplication = estimate_task_multiplication()
    continuity_ratio = compute_continuity_ratio()

    metrics = {
        "entries_per_hour": entries_rate,
        "novelty_rate": novelty_rate,
        "avg_confidence": avg_conf,
        "cascade_probability": cascade_probability,
        "building_ratio": building_ratio,
        "task_multiplication": task_multiplication,
        "continuity_ratio": continuity_ratio,
    }

    candidates = _build_candidates(policy, metrics)
    previous_query = _read_previous_query()
    random.shuffle(candidates)
    chosen = None
    for candidate in candidates:
        if _novelty_distance(candidate, previous_query) >= policy.novelty_floor:
            chosen = candidate
            break
    if chosen is None:
        chosen = random.choice(candidates)

    timestamp = int(time.time())
    manifest_digest = _manifest_digest()
    query = (
        f"{chosen}\n"
        f"# lineage={_latest_artifact().get('digest_lineage', {}).get('current', '')}"
        f"|manifesto={manifest_digest}|cascade={cascade_probability}|ts={timestamp}"
    )

    record = {
        "artifact_type": "self_query",
        "query": query,
        "timestamp": timestamp,
        "manifesto_digest": manifest_digest,
        "metrics": metrics,
        "policy": {
            "novelty_floor": policy.novelty_floor,
            "targets": {
                "building_ratio_min": policy.building_ratio_min,
                "task_queue_min": policy.task_queue_min,
                "task_multiplication_min": policy.task_multiplication_min,
            },
        },
    }
    if STATE_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            state = {}
        record["loop_state_snapshot"] = state
    return record


def write_query(record: Dict[str, object]) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    USER_QUERY.parent.mkdir(parents=True, exist_ok=True)
    USER_QUERY.write_text(record["query"], encoding="utf-8")
    artifact_path = ARTIFACTS_DIR / f"self_query_{record['timestamp']}.json"
    artifact_path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def main() -> None:
    record = synthesize_query()
    write_query(record)
    print(f"[SELF-QUERY] wrote new directive: {record['query']}")


if __name__ == "__main__":
    main()
