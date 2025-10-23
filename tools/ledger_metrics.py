#!/usr/bin/env python3
"""Helpers for computing Kael ledger metrics and NOS scores."""
from __future__ import annotations

from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Dict, Iterable, Iterator
import json
import re


BUILDING_TYPE_HINTS = (
    "spec",
    "plan",
    "schema",
    "protocol",
    "validator",
    "pipeline",
    "manifesto",
    "loop_state",
    "policy",
    "ledger",
    "implementation",
    "architecture",
    "design",
    "queue_balancer",
    "sep",
    "upgrade",
    "patch",
)

BUILDING_KEYWORDS = (
    "build",
    "implement",
    "wire",
    "deploy",
    "migrate",
    "refactor",
    "upgrade",
    "scaffold",
    "generate",
    "create",
    "instrument",
    "hook",
    "schema",
    "protocol",
    "blueprint",
    "spec",
    "manifest",
)

BUILDING_EXTENSIONS = (
    ".py",
    ".rs",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".java",
    ".cs",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".md",
    ".rst",
)

_BUILDING_KEYWORD_PATTERNS = [re.compile(rf"\b{re.escape(keyword)}\b") for keyword in BUILDING_KEYWORDS]

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"

DEFAULT_NOS_WEIGHTS = {
    "energy_efficiency": 0.35,
    "coherence": 0.30,
    "resilience": 0.25,
    "entropy": 0.10,
}


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


def _iter_artifacts(directory: Path) -> Iterator[Path]:
    if not directory.exists():
        return iter(())
    return (path for path in sorted(directory.glob("*.json")))


def _iter_strings(value) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        try:
            yield json.dumps(value)
        except TypeError:
            yield str(value)
    elif isinstance(value, IterableABC):
        for item in value:
            yield from _iter_strings(item)


def _looks_like_code_reference(text: str) -> bool:
    lower = text.strip().lower()
    return any(lower.endswith(ext) for ext in BUILDING_EXTENSIONS)


def _split_artifact_type(value: str) -> set[str]:
    tokens = {value}
    sanitized = value.replace("-", " ").replace("_", " ").replace("/", " ")
    tokens.update(part for part in sanitized.split() if part)
    return tokens


def _is_building_payload(payload: Dict[str, object]) -> bool:
    artifact_type = str(payload.get("artifact_type", "")).lower()
    if artifact_type:
        tokens = _split_artifact_type(artifact_type)
        if any(hint in tokens for hint in BUILDING_TYPE_HINTS):
            return True

    # Inspect summary-style fields first for quick hits.
    candidate_fields = [
        "summary",
        "observation",
        "goal",
        "goals",
        "decisions",
        "notes",
        "description",
        "actions",
        "actions_taken",
        "plan",
        "analysis",
        "deltas",
        "changes",
        "diff",
        "rationale",
        "next_steps",
        "next_action",
        "evidence",
        "acceptance_criteria",
        "assumptions",
        "risk",
    ]

    text_fragments = []
    for key in candidate_fields:
        if key in payload:
            text_fragments.extend(_iter_strings(payload.get(key)))

    combined_text = "\n".join(fragment.lower() for fragment in text_fragments if isinstance(fragment, str))
    if combined_text and any(pattern.search(combined_text) for pattern in _BUILDING_KEYWORD_PATTERNS):
        return True

    # Examine generic fields when specific ones are missing.
    if not combined_text:
        combined_text = json.dumps(payload).lower()
        if any(pattern.search(combined_text) for pattern in _BUILDING_KEYWORD_PATTERNS):
            return True

    # Look for explicit file path references that usually signal implementation.
    for key in ("files", "paths", "modified_files", "touched_files", "diffs", "artifacts"):
        if key not in payload:
            continue
        for fragment in _iter_strings(payload.get(key)):
            if isinstance(fragment, str) and _looks_like_code_reference(fragment):
                return True

    return False


def measure_building_ratio(artifacts_dir: Path | None = None) -> float:
    """Approximate the fraction of artifacts containing build-oriented deltas."""
    directory = artifacts_dir or ARTIFACTS_DIR
    files = list(_iter_artifacts(directory))
    if not files:
        return 0.0
    build_hits = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict):
            if _is_building_payload(payload):
                build_hits += 1
    return round(build_hits / len(files), 3)


def estimate_task_multiplication(artifacts_dir: Path | None = None) -> float:
    """Estimate task multiplication as ratio of subtasks to root tasks."""
    directory = artifacts_dir or ARTIFACTS_DIR
    files = list(_iter_artifacts(directory))
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
    files = list(_iter_artifacts(directory))
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
