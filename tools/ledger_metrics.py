#!/usr/bin/env python3
"""Helpers for computing Kael ledger metrics and NOS scores."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Sequence
import json

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"

DEFAULT_NOS_WEIGHTS = {
    "energy_efficiency": 0.35,
    "coherence": 0.30,
    "resilience": 0.25,
    "entropy": 0.10,
}


BUILDING_ARTIFACT_TOKENS = {
    "design",
    "design_spec",
    "schema",
    "spec",
    "implementation",
    "implementation_plan",
    "validator",
    "queue",
    "pipeline",
    "policy",
    "infrastructure",
    "plan",
}

BUILDING_KEYWORDS = {
    "design",
    "implement",
    "implementation",
    "build",
    "builder",
    "pipeline",
    "schema",
    "infrastructure",
    "validator",
    "queue",
    "migrate",
    "spec",
    "specification",
    "deploy",
    "rollout",
    "roll-forward",
    "blueprint",
    "plan",
    "code",
    "module",
}

BUILDING_FILE_EXTENSIONS = (
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    ".toml",
    ".ini",
)


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
    files = (
        list(_iter_artifacts())
        if artifacts_dir is None
        else sorted(directory.glob("*.json"))
    )
    if not files:
        return 0.0
    build_hits = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if _is_building_payload(payload):
            build_hits += 1
    return round(build_hits / len(files), 3)


def _is_building_payload(payload: object) -> bool:
    """Heuristically determine if an artifact captures build activity."""

    if not isinstance(payload, dict):
        return False

    artifact_type = str(payload.get("artifact_type") or "").lower()
    if artifact_type and _matches_token(artifact_type, BUILDING_ARTIFACT_TOKENS):
        return True

    tags = payload.get("tags")
    if isinstance(tags, Sequence) and not isinstance(tags, (str, bytes)):
        for tag in tags:
            if isinstance(tag, str) and _matches_token(tag.lower(), BUILDING_ARTIFACT_TOKENS):
                return True

    text = json.dumps(payload, sort_keys=True).lower()
    if any(keyword in text for keyword in BUILDING_KEYWORDS):
        return True

    if _contains_building_extension(payload):
        return True

    return False


def _matches_token(text: str, tokens: Iterable[str]) -> bool:
    return any(token in text for token in tokens)


def _contains_building_extension(payload: dict) -> bool:
    """Check for explicit file references that imply code or config changes."""

    candidate_fields = ("files", "paths", "artifacts", "changes", "outputs")
    for field in candidate_fields:
        value = payload.get(field)
        if _value_has_building_extension(value):
            return True
    return False


def _value_has_building_extension(value: object) -> bool:
    if isinstance(value, str):
        return value.lower().endswith(BUILDING_FILE_EXTENSIONS)
    if isinstance(value, (list, tuple, set)):
        return any(_value_has_building_extension(item) for item in value)
    if isinstance(value, dict):
        return any(_value_has_building_extension(v) for v in value.values())
    return False


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


def compute_nos_score(
    energy_efficiency: float,
    coherence: float,
    resilience: float,
    entropy: float,
    weights: Dict[str, float] | None = None,
) -> float:
    """Compute the Natural Optimisation Signature score with optional weights."""

    w = {**DEFAULT_NOS_WEIGHTS, **(weights or {})}
    entropy_component = max(float(entropy) * max(w.get("entropy", 0.1), 1e-6), 1e-6)
    energy = min(max(float(energy_efficiency), 0.0), 1.0)
    coh = min(max(float(coherence), 0.0), 1.0)
    res = min(max(float(resilience), 0.0), 1.0)
    numerator = max(w["energy_efficiency"], 1e-6) * energy
    numerator *= max(w["coherence"], 1e-6) * coh
    numerator *= max(w["resilience"], 1e-6) * res
    raw = numerator / entropy_component
    return round(raw, 3)


def map_nature_to_kpis(heuristics: Iterable[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    """Transform heuristic specs into loop policy deltas.

    Each heuristic entry should define ``mapping_to_codex_metric`` and
    ``policy_suggestion`` fields.  The function produces a dictionary keyed by
    heuristic name so callers can trace the resulting policy recommendations.
    """

    mapping: Dict[str, Dict[str, object]] = {}
    for item in heuristics:
        if not isinstance(item, dict):
            continue
        name = str(item.get("heuristic_name") or item.get("name") or "heuristic")
        mapping[name] = {
            "metrics": item.get("mapping_to_codex_metric") or item.get("mapping"),
            "policy": item.get("policy_suggestion") or item.get("policy"),
            "expected_effect": item.get("expected_effect"),
        }
    return mapping


__all__ = [
    "DEFAULT_NOS_WEIGHTS",
    "compute_cascade_probability",
    "measure_building_ratio",
    "estimate_task_multiplication",
    "compute_continuity_ratio",
    "compute_nos_score",
    "map_nature_to_kpis",
]
