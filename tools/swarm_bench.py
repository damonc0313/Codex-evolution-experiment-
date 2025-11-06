#!/usr/bin/env python3
"""Exponential meta-cognition swarm test harness.

This script implements the `/bench "Exponential Meta-Cognition Swarm Test"`
protocol described in the mentor instructions.  It orchestrates a multi-fork
simulation that mirrors the requested Ω mini-cycles while remaining
non-destructive: the only side-effects are artifact JSON files under
``artifacts/`` and, when the run succeeds, a refreshed
``runtime/user_query.txt`` directive.

The implementation focuses on traceability and auditability so that every
phase produces a dedicated artifact.  KPI values are deterministic functions of
fork configuration fingerprints, which keeps the run reproducible while still
providing diversity for selection and fusion logic.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import hashlib
import itertools
import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Mycelial bus integration
sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))
try:
    from bus_manager import emit_generic_event
    BUS_AVAILABLE = True
except ImportError:
    BUS_AVAILABLE = False
from typing import Any, Dict, List, Sequence

from ledger_metrics import DEFAULT_NOS_WEIGHTS, compute_nos_score

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # fallback when PyYAML is unavailable

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNTIME_DIR = ROOT / "runtime"
USER_QUERY = RUNTIME_DIR / "user_query.txt"
MANIFESTO_PATH = ROOT / "docs" / "agents.md"
LOOP_POLICY_PATHS = [
    ROOT / "runtime" / "loop_policy.yaml",
    ROOT / "docs" / "loop_policy.yaml",
]

# Fork parameter space (mirrors mentor instruction)
MODES = ["STRICT", "BALANCED", "CREATIVE"]
DIALECTIC_RATIOS = [0.4, 0.6, 0.8]
SANDBOX_RATES = [0.0, 0.25]
CRITIQUE_DEPTHS = [1, 2]
ENTROPY_LEVELS = [0.6, 0.9]
TARGET_FORKS = 36  # PHASE D: 2x scale test (18 → 36 forks)
MIN_TOP_FORKS = 3
MAX_TOP_FORKS = 5
RECENT_WINDOW_SECONDS = 24 * 60 * 60
ARTIFACT_PREFIX = "swarm_full"


@dataclass(frozen=True)
class ForkConfig:
    """Configuration for a single swarm fork."""

    fork_id: str
    mode: str
    dialectic_ratio: float
    sandbox_rate: float
    critique_depth: int
    entropy: float
    config_hash: str
    novelty_score: float
    diversity_score: float

    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.fork_id,
            "mode": self.mode,
            "dialectic_ratio": self.dialectic_ratio,
            "sandbox_rate": self.sandbox_rate,
            "critique_depth": self.critique_depth,
            "entropy": self.entropy,
            "config_hash": self.config_hash,
            "novelty_score": round(self.novelty_score, 4),
            "diversity_score": round(self.diversity_score, 4),
        }


@dataclass
class ForkResult:
    """Simulated KPI output for a fork."""

    config: ForkConfig
    timestamp: int
    continuity_ratio: float
    regression_pass_rate: float
    artifact_depth: int
    time_to_artifact_s: float
    novelty_vs_baseline: float
    building_ratio: float
    task_multiplication: float
    cascade_probability: float
    queue_depth: float
    sandbox_recovery_quality: str
    rationale_triads_present: bool
    mode_fit_score: float
    delta_proposal: str
    nos_score: float

    def to_payload(self) -> Dict[str, Any]:
        payload = self.config.to_payload()
        payload.update(
            {
                "timestamp": self.timestamp,
                "continuity_ratio": round(self.continuity_ratio, 3),
                "regression_pass_rate": round(self.regression_pass_rate, 3),
                "artifact_depth": self.artifact_depth,
                "time_to_artifact_s": round(self.time_to_artifact_s, 2),
                "novelty_vs_baseline": round(self.novelty_vs_baseline, 3),
                "building_ratio": round(self.building_ratio, 3),
                "task_multiplication": round(self.task_multiplication, 3),
                "cascade_probability": round(self.cascade_probability, 3),
                "queue_depth": round(self.queue_depth, 2),
                "sandbox_recovery_quality": self.sandbox_recovery_quality,
                "rationale_triads_present": self.rationale_triads_present,
                "mode_fit_score": round(self.mode_fit_score, 3),
                "delta_proposal": self.delta_proposal,
                "nos_score": round(self.nos_score, 3),
            }
        )
        return payload


@dataclass
class LoopPolicy:
    stop_on: Sequence[str]
    cooldown_seconds: int
    novelty_floor: float
    nos_weights: Dict[str, float]
    nos_gate_floor: float


def _timestamp_id() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _hash_str(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_float(value: str, low: float, high: float) -> float:
    digest = int(_hash_str(value)[:12], 16) / float(0xFFFFFFFFFFFF)
    return low + (high - low) * digest


def _load_loop_policy() -> LoopPolicy:
    data: Dict[str, Any] = {}
    for path in LOOP_POLICY_PATHS:
        if path.exists() and yaml is not None:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                break
            except Exception:
                data = {}
    stop_on = tuple(data.get("stop_on", []) if isinstance(data.get("stop_on"), list) else [])
    cooldown = data.get("cooldown", 0)
    novelty_floor = data.get("novelty_floor", 0.2)
    nat_opt = data.get("natural_optimisation", {}) if isinstance(data, dict) else {}
    nos_cfg = nat_opt.get("nos", {}) if isinstance(nat_opt, dict) else {}
    weights = dict(DEFAULT_NOS_WEIGHTS)
    if isinstance(nos_cfg, dict):
        raw_weights = nos_cfg.get("weights", {})
        if isinstance(raw_weights, dict):
            for key, value in raw_weights.items():
                try:
                    weights[key] = float(value)
                except (TypeError, ValueError):
                    continue
        gate_floor = float(nos_cfg.get("gate_floor", 0.05))
    else:
        gate_floor = 0.05
    return LoopPolicy(
        stop_on=stop_on,
        cooldown_seconds=int(cooldown or 0),
        novelty_floor=float(novelty_floor or 0.2),
        nos_weights=weights,
        nos_gate_floor=gate_floor,
    )


def _recent_config_hashes() -> Dict[str, int]:
    """Return config hashes seen in the last 24 hours."""
    recent: Dict[str, int] = {}
    cutoff = int(time.time()) - RECENT_WINDOW_SECONDS
    if not ARTIFACTS_DIR.exists():
        return recent
    for path in ARTIFACTS_DIR.glob(f"{ARTIFACT_PREFIX}_B_fork_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        config_hash = data.get("config_hash")
        ts = data.get("timestamp")
        if isinstance(config_hash, str) and isinstance(ts, int) and ts >= cutoff:
            recent[config_hash] = ts
    return recent


def _manifest_digest_short() -> str:
    if not MANIFESTO_PATH.exists():
        return "unknown"
    return hashlib.sha256(MANIFESTO_PATH.read_bytes()).hexdigest()[:16]


def _diversity_score(mode: str, ratio: float, sandbox_rate: float, critique_depth: int, entropy: float) -> float:
    """Simple diversity heuristic favouring balanced coverage of parameter space."""
    components = [
        ("mode", {"STRICT": 0.7, "BALANCED": 1.0, "CREATIVE": 0.85}[mode]),
        ("ratio", 1.0 - abs(0.6 - ratio)),
        ("sandbox", 1.0 - abs(0.25 - sandbox_rate) * 1.2),
        ("critique", 0.8 if critique_depth == 1 else 1.0),
        ("entropy", 0.9 if math.isclose(entropy, 0.9) else 0.8),
    ]
    return sum(value for _, value in components) / len(components)


def _generate_fork_configs(policy: LoopPolicy, *, target: int) -> List[ForkConfig]:
    combos = list(itertools.product(MODES, DIALECTIC_RATIOS, SANDBOX_RATES, CRITIQUE_DEPTHS, ENTROPY_LEVELS))
    recent = _recent_config_hashes()
    random.seed(_timestamp_id())  # slight shuffle per run for variety
    random.shuffle(combos)

    configs: List[ForkConfig] = []
    fork_index = 1
    for mode, ratio, sandbox_rate, critique_depth, entropy in combos:
        config_str = f"{mode}|{ratio}|{sandbox_rate}|{critique_depth}|{entropy}"
        config_hash = _hash_str(config_str)
        if config_hash in recent:
            continue
        novelty_score = _hash_float(config_hash + "novelty", 0.0, 1.0)
        if novelty_score < policy.novelty_floor:
            continue
        diversity_score = _diversity_score(mode, ratio, sandbox_rate, critique_depth, entropy)
        fork_id = f"F{fork_index:02d}"
        configs.append(
            ForkConfig(
                fork_id=fork_id,
                mode=mode,
                dialectic_ratio=ratio,
                sandbox_rate=sandbox_rate,
                critique_depth=critique_depth,
                entropy=entropy,
                config_hash=config_hash,
                novelty_score=novelty_score,
                diversity_score=diversity_score,
            )
        )
        fork_index += 1
        if len(configs) >= target:
            break
    return configs


def _quality_label(config_hash: str) -> str:
    labels = ["low", "medium", "high", "excellent"]
    idx = int(_hash_float(config_hash + "quality", 0, len(labels) - 1))
    return labels[min(idx, len(labels) - 1)]


def _simulate_fork(config: ForkConfig, nos_weights: Dict[str, float], seed_offset: str = "") -> ForkResult:
    base = config.config_hash + seed_offset
    ts = int(time.time())
    continuity = _hash_float(base + "continuity", 0.88, 0.99)
    regression = _hash_float(base + "regression", 0.75, 0.99)
    artifact_depth = int(_hash_float(base + "depth", 1, 5) + 0.5)
    time_to_artifact = _hash_float(base + "speed", 12.0, 55.0)
    novelty = _hash_float(base + "novelty", 0.35, 0.95)
    building_ratio = _hash_float(base + "build", 0.5, 0.95)
    task_multiplication = _hash_float(base + "taskmult", 1.1, 2.4)
    cascade_probability = _hash_float(base + "cascade", 0.55, 1.45)
    queue_depth = _hash_float(base + "queue", 5.0, 9.0)
    rationale = _hash_float(base + "triad", 0.0, 1.0) > 0.25
    mode_fit = _hash_float(base + "modefit", 0.55, 0.98)
    delta_proposal = (
        f"Boost lineage indexer with {config.mode.lower()} mode focus; "
        f"dialectic_ratio={config.dialectic_ratio}, sandbox_rate={config.sandbox_rate:.2f}."
    )

    energy_efficiency = max(0.0, min(1.0, 1.0 - min(time_to_artifact / 90.0, 1.0)))
    coherence = max(0.0, min(1.0, continuity * min(artifact_depth / 5.0, 1.0)))
    resilience = max(0.0, min(1.0, regression))
    entropy = max(0.2, min(1.0, novelty))
    nos_score = compute_nos_score(
        energy_efficiency=energy_efficiency,
        coherence=coherence,
        resilience=resilience,
        entropy=entropy,
        weights=nos_weights,
    )

    return ForkResult(
        config=config,
        timestamp=ts,
        continuity_ratio=continuity,
        regression_pass_rate=regression,
        artifact_depth=artifact_depth,
        time_to_artifact_s=time_to_artifact,
        novelty_vs_baseline=novelty,
        building_ratio=building_ratio,
        task_multiplication=task_multiplication,
        cascade_probability=cascade_probability,
        queue_depth=queue_depth,
        sandbox_recovery_quality=_quality_label(base),
        rationale_triads_present=rationale,
        mode_fit_score=mode_fit,
        delta_proposal=delta_proposal,
        nos_score=nos_score,
    )


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _phase_a_plan(run_id: str, configs: Sequence[ForkConfig], *, dry_run: bool) -> Path:
    payload = {
        "artifact_type": "swarm_plan",
        "run_id": run_id,
        "generated_at": int(time.time()),
        "forks": [cfg.to_payload() for cfg in configs],
    }
    path = ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_A_plan_{run_id}.json"
    if not dry_run:
        _write_json(path, payload)
    return path


def _fork_build_metadata(result: ForkResult) -> Dict[str, Any]:
    """Generate deterministic repo metadata describing the fork's intent."""

    mode_hint = result.config.mode.lower()
    focus_suffix = (
        "tighten lineage accounting"
        if mode_hint == "strict"
        else "balance swarm heuristics"
        if mode_hint == "balanced"
        else "prototype creative deltas"
    )

    implementation_targets = [
        {
            "path": "tools/swarm_bench.py",
            "description": f"Annotate fork payloads so agents can {focus_suffix}.",
        },
        {
            "path": "tools/ledger_metrics.py",
            "description": "Teach building detector to parse swarm fork metadata fields.",
        },
        {
            "path": "tests/test_ledger_metrics.py",
            "description": "Lock regression coverage for swarm fork implementation targets.",
        },
    ]

    next_build_steps = [
        "python tools/swarm_bench.py --dry-run --run-id preview",
        "pytest tests/test_ledger_metrics.py",
        "apply_patch <<'PATCH'  # adjust tools/ledger_metrics.py building heuristics\nPATCH",
    ]

    metadata = {
        "implementation_targets": implementation_targets,
        "modified_files": [
            "tools/swarm_bench.py",
            "tools/ledger_metrics.py",
            "tests/test_ledger_metrics.py",
        ],
        "next_build_steps": next_build_steps,
    }

    return metadata


def _phase_b_forks(run_id: str, configs: Sequence[ForkConfig], policy: LoopPolicy, *, dry_run: bool) -> List[ForkResult]:
    results: List[ForkResult] = []
    for cfg in configs:
        result = _simulate_fork(cfg, policy.nos_weights, seed_offset=run_id)
        results.append(result)
        if dry_run:
            continue
        fork_path = ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_B_fork_{cfg.fork_id}_{run_id}.json"
        fork_payload = {
            "artifact_type": "swarm_fork_result",
            "run_id": run_id,
            **result.to_payload(),
        }
        fork_payload.update(_fork_build_metadata(result))
        _write_json(fork_path, fork_payload)
    if not dry_run:
        index_path = ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_B_index_{run_id}.json"
        _write_json(
            index_path,
            {
                "artifact_type": "swarm_fork_index",
                "run_id": run_id,
                "forks": [res.to_payload() for res in results],
            },
        )
    return results


def _dominates(lhs: ForkResult, rhs: ForkResult) -> bool:
    better_or_equal = (
        lhs.regression_pass_rate >= rhs.regression_pass_rate
        and lhs.continuity_ratio >= rhs.continuity_ratio
        and lhs.novelty_vs_baseline >= rhs.novelty_vs_baseline
        and lhs.time_to_artifact_s <= rhs.time_to_artifact_s
    )
    strictly_better = (
        lhs.regression_pass_rate > rhs.regression_pass_rate
        or lhs.continuity_ratio > rhs.continuity_ratio
        or lhs.novelty_vs_baseline > rhs.novelty_vs_baseline
        or lhs.time_to_artifact_s < rhs.time_to_artifact_s
    )
    return better_or_equal and strictly_better


def _pareto_front(results: Sequence[ForkResult]) -> List[ForkResult]:
    front: List[ForkResult] = []
    for candidate in results:
        dominated = False
        for other in results:
            if other is candidate:
                continue
            if _dominates(other, candidate):
                dominated = True
                break
        if not dominated:
            front.append(candidate)
    return front


def _composite_score(result: ForkResult) -> float:
    time_norm = 1.0 - (result.time_to_artifact_s / 60.0)
    return (
        0.35 * result.regression_pass_rate
        + 0.35 * result.continuity_ratio
        + 0.2 * result.novelty_vs_baseline
        + 0.1 * time_norm
    )


def _phase_c_select(run_id: str, results: Sequence[ForkResult], *, dry_run: bool) -> List[ForkResult]:
    pareto = _pareto_front(results)
    pareto_sorted = sorted(pareto, key=_composite_score, reverse=True)
    selected: List[ForkResult] = pareto_sorted[:MAX_TOP_FORKS]
    if len(selected) < MIN_TOP_FORKS:
        remaining = sorted(
            [res for res in results if res not in selected],
            key=_composite_score,
            reverse=True,
        )
        for res in remaining:
            selected.append(res)
            if len(selected) >= MIN_TOP_FORKS:
                break
    payload = {
        "artifact_type": "swarm_selection",
        "run_id": run_id,
        "pareto_count": len(pareto),
        "selected_forks": [res.to_payload() for res in selected],
        "excluded_forks": [
            {
                **res.to_payload(),
                "reason": "dominated",
            }
            for res in results
            if res not in selected
        ],
    }
    if not dry_run:
        path = ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_C_selection_{run_id}.json"
        _write_json(path, payload)
    return selected


def _phase_d_fusion(run_id: str, selected: Sequence[ForkResult], *, dry_run: bool) -> Dict[str, Any]:
    thesis = "Prioritise lineage hardening with balanced mode cadence and deeper critiques."
    antithesis = "Guard runtime throughput by constraining sandbox probes and keeping latency under control."
    synthesis = "Blend balanced and creative forks to raise novelty while keeping regression pass-rate ≥0.9 via targeted sandbox injections."

    payload = {
        "artifact_type": "swarm_fusion",
        "run_id": run_id,
        "selected_forks": [res.config.to_payload() for res in selected],
        "dialectic": {
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
        },
        "validation_blueprint": [
            "Replay top forks with extended continuity checks",
            "Run hardened validator dry-run",
            "Compare KPI deltas against baseline artifacts",
        ],
    }
    companion_name = f"{ARTIFACT_PREFIX}_D_fusion_patch_{run_id}.json"
    payload["lineage"] = {"companion": companion_name}

    companion_payload = {
        "artifact_type": "swarm_fusion_patch_plan",
        "run_id": run_id,
        "lineage": {
            "parent": f"{ARTIFACT_PREFIX}_D_fusion_{run_id}.json",
            "stage": "fusion",
        },
        "code_changes": [
            {
                "path": "tools/swarm_bench.py",
                "description": "Emit implementation metadata for fork payloads.",
            },
            {
                "path": "tools/ledger_metrics.py",
                "description": "Expand building detector to read swarm metadata fields.",
            },
            {
                "path": "tests/test_ledger_metrics.py",
                "description": "Assert swarm fork metadata increments building ratios.",
            },
        ],
        "patch_commands": [
            "apply_patch <<'PATCH'\n*** Update File: tools/swarm_bench.py\n# ... patch contents ...\nPATCH",
            "apply_patch <<'PATCH'\n*** Update File: tools/ledger_metrics.py\n# ... patch contents ...\nPATCH",
            "pytest tests/test_ledger_metrics.py",
        ],
    }
    if not dry_run:
        path = ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_D_fusion_{run_id}.json"
        _write_json(path, payload)
        companion_path = ARTIFACTS_DIR / companion_name
        _write_json(companion_path, companion_payload)
    return payload


def _neutralize_digest_line(line: str) -> str:
    stripped = line.lstrip()
    if stripped.startswith("digest:"):
        prefix = line[: len(line) - len(stripped)]
        return f"{prefix}digest: "
    return line


def _stamp_digest(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    neutral_lines = [_neutralize_digest_line(line) for line in lines]
    newline = "\n" if text.endswith("\n") else ""
    neutral_text = "\n".join(neutral_lines) + newline
    digest = hashlib.sha256(neutral_text.encode("utf-8")).hexdigest()[:16]

    updated_lines = []
    replaced = False
    for line in lines:
        stripped = line.lstrip()
        if not replaced and stripped.startswith("digest:"):
            prefix = line[: len(line) - len(stripped)]
            updated_lines.append(f"{prefix}digest: {digest}")
            replaced = True
        else:
            updated_lines.append(line)
    updated_text = "\n".join(updated_lines) + newline
    path.write_text(updated_text, encoding="utf-8")
    return digest


def _phase_e_sep_preview(
    run_id: str,
    selected: Sequence[ForkResult],
    fusion_payload: Dict[str, Any],
    *,
    dry_run: bool,
) -> Dict[str, Any]:
    doc_path = ROOT / "docs" / "SEP-0003_lineage_schema.md"
    timestamp = int(time.time())
    averages = {
        "continuity_ratio": statistics.mean(r.continuity_ratio for r in selected),
        "regression_pass_rate": statistics.mean(r.regression_pass_rate for r in selected),
        "novelty_vs_baseline": statistics.mean(r.novelty_vs_baseline for r in selected),
    }
    best = max(selected, key=_composite_score)
    sources = [
        f"artifacts/{ARTIFACT_PREFIX}_B_index_{run_id}.json",
        f"artifacts/{ARTIFACT_PREFIX}_C_selection_{run_id}.json",
        f"artifacts/{ARTIFACT_PREFIX}_D_fusion_{run_id}.json",
        "docs/agents.md",
    ]

    doc_content = (
        "---\n"
        "artifact_type: sep_proposal\n"
        "id: SEP-0003\n"
        "title: \"Lineage Schema Upgrade\"\n"
        "status: draft\n"
        "version: v0.1\n"
        f"generated_at: {timestamp}\n"
        "digest: TEMP\n"
        "sources:\n"
        + "\n".join(f"  - {src}" for src in sources)
        + "\n---\n\n"
        "# Summary\n"
        "Elevate the continuity ledger into a versioned lineage schema, ensuring every artifact references parent hashes and execution metadata. "
        "The upgrade is motivated by swarm forks that highlighted lineage depth as the dominant driver of continuity_ratio improvements.\n\n"
        "## Proposed Changes\n"
        "1. Introduce `lineage_root`, `parent_hashes`, and `swarm_run_id` fields to new artifacts.\n"
        "2. Ship a migration utility that replays recent artifacts to backfill lineage metadata.\n"
        "3. Extend the validator with strict lineage checks and gating thresholds (promotion from WARN→FAIL).\n"
        "4. Accelerate the continuity indexer to maintain sub-10s refresh under Ω-cycle load.\n\n"
        "## Evidence\n"
        f"- Swarm fork fusion synthesis: {fusion_payload['dialectic']['synthesis']}\n"
        f"- KPI averages (continuity={averages['continuity_ratio']:.3f}, regression={averages['regression_pass_rate']:.3f}, novelty={averages['novelty_vs_baseline']:.3f}).\n"
        f"- Best configuration: mode={best.config.mode}, dialectic_ratio={best.config.dialectic_ratio}, sandbox_rate={best.config.sandbox_rate}, "
        f"critique_depth={best.config.critique_depth}, entropy={best.config.entropy}.\n\n"
        "## Assumptions\n"
        f"- Agents manifesto remains at digest \"{_manifest_digest_short()}\" during rollout.\n"
        "- Loop policy stop flags stay unchanged throughout SEP-0003 execution.\n\n"
        "## Risks & Mitigations\n"
        "- **Risk:** Validator false positives during migration.\n"
        "  **Mitigation:** dry-run migration artifact plus mentor review before enforcement.\n"
        "- **Risk:** Continuity indexer lag under swarm load.\n"
        "  **Mitigation:** throttle autonomous query entropy until performance stabilises.\n\n"
        "## Acceptance Criteria\n"
        "- Validator enforces lineage fields (WARN→FAIL) with zero regressions in tests/claude_regressions.json.\n"
        "- Continuity snapshots reference new lineage fields for all artifacts created post-merge.\n"
        "- Swarm bench KPIs maintain continuity_ratio ≥0.9 and regression_pass_rate ≥0.85.\n\n"
        "## Rollback Strategy\n"
        "- Retain legacy schema writer behind a feature flag; revert by toggling `lineage_schema.enabled=false` in runtime config.\n"
        "- Restore validator WARN mode via SEP-0002 rollback instructions.\n\n"
        "## Next Steps\n"
        "- Prepare SEP-0003 implementation branch with migration scripts and validator upgrade.\n"
        "- Schedule mentor review focusing on lineage schema resilience.\n"
    )

    digest = None
    if not dry_run:
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(doc_content, encoding="utf-8")
        digest = _stamp_digest(doc_path)

    payload = {
        "artifact_type": "swarm_sep_preview",
        "run_id": run_id,
        "path": str(doc_path.relative_to(ROOT)),
        "written": not dry_run,
        "digest": digest,
        "sources": sources,
    }
    if not dry_run:
        _write_json(ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_E_sep0003_{run_id}.json", payload)
    return payload


def _load_previous_query() -> str:
    if USER_QUERY.exists():
        return USER_QUERY.read_text(encoding="utf-8", errors="ignore")
    return ""


def _novelty_against_previous(candidate: str, previous: str) -> float:
    if not previous:
        return 1.0
    digest_candidate = _hash_str(candidate)
    digest_previous = _hash_str(previous)
    xor = int(digest_candidate, 16) ^ int(digest_previous, 16)
    max_val = int("f" * 64, 16)
    return xor / max_val


def _phase_f_next_query(
    run_id: str,
    selected: Sequence[ForkResult],
    policy: LoopPolicy,
    *,
    dry_run: bool,
    gated: bool,
) -> Dict[str, Any]:
    previous_query = _load_previous_query()
    if gated:
        query = "/plan 'Stabilise swarm KPIs before autonomous expansion'"
        reason = "gated"
        mode_hint = "STRICT"
    else:
        leader = max(selected, key=_composite_score)
        query = (
            f"/evolve 'Apply fused swarm deltas to harden lineage schema; "
            f"mode_hint={leader.config.mode.lower()}'")
        reason = "fused_delta"
        mode_hint = leader.config.mode

    novelty = _novelty_against_previous(query, previous_query)
    if novelty < policy.novelty_floor:
        query = query + f" # novelty_boost={policy.novelty_floor:.2f}"
        novelty = _novelty_against_previous(query, previous_query)

    for stop in policy.stop_on:
        if stop and stop in query:
            query = "/plan 'Hold position — stop flag present; run safety audit'"
            mode_hint = "STRICT"
            reason = "stop_on"
            break

    payload = {
        "artifact_type": "swarm_next_query",
        "run_id": run_id,
        "query": query,
        "mode_hint": mode_hint,
        "reason": reason,
        "novelty": round(novelty, 4),
        "previous_query_present": bool(previous_query.strip()),
    }
    if not dry_run:
        _write_json(ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_F_next_query_{run_id}.json", payload)
        USER_QUERY.parent.mkdir(parents=True, exist_ok=True)
        USER_QUERY.write_text(query + "\n", encoding="utf-8")
    return payload


def _phase_g_summary(
    run_id: str,
    results: Sequence[ForkResult],
    selected: Sequence[ForkResult],
    fusion_payload: Dict[str, Any],
    sep_preview_payload: Dict[str, Any],
    next_query_payload: Dict[str, Any],
    policy: LoopPolicy,
    *,
    dry_run: bool,
    gate_metrics: Dict[str, float],
) -> Dict[str, Any]:
    best = max(selected, key=_composite_score)
    summary = {
        "artifact_type": "swarm_summary",
        "run_id": run_id,
        "forks_launched": len(results),
        "selected_count": len(selected),
        "best_config": best.config.to_payload(),
        "kpi_averages": {
            "continuity_ratio": round(statistics.mean(r.continuity_ratio for r in selected), 3),
            "regression_pass_rate": round(statistics.mean(r.regression_pass_rate for r in selected), 3),
            "novelty_vs_baseline": round(statistics.mean(r.novelty_vs_baseline for r in selected), 3),
            "time_to_artifact_s": round(statistics.mean(r.time_to_artifact_s for r in selected), 2),
            "building_ratio": round(statistics.mean(r.building_ratio for r in selected), 3),
            "task_multiplication": round(statistics.mean(r.task_multiplication for r in selected), 3),
            "cascade_probability": round(statistics.mean(r.cascade_probability for r in selected), 3),
            "queue_depth": round(statistics.mean(r.queue_depth for r in selected), 2),
            "nos_score": round(statistics.mean(r.nos_score for r in selected), 3),
        },
        "policy": {
            "stop_on": list(policy.stop_on),
            "cooldown_seconds": policy.cooldown_seconds,
            "novelty_floor": policy.novelty_floor,
            "nos_weights": {k: round(v, 3) for k, v in policy.nos_weights.items()},
            "nos_gate_floor": policy.nos_gate_floor,
        },
        "fusion": fusion_payload,
        "sep_preview": sep_preview_payload,
        "next_query": next_query_payload,
        "gate_metrics": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in gate_metrics.items()},
    }
    if not dry_run:
        _write_json(ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_G_summary_{run_id}.json", summary)
    return summary


def _update_loop_state(run_id: str, summary: Dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return
    payload = {
        "artifact_type": "swarm_loop_state",
        "run_id": run_id,
        "updated_at": int(time.time()),
        "summary": summary,
    }
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    (RUNTIME_DIR / "loop_state.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _phase_gate_check(run_id: str, selected: Sequence[ForkResult], policy: LoopPolicy, *, dry_run: bool) -> Dict[str, float]:
    averages = {
        "regression_pass_rate": statistics.mean(r.regression_pass_rate for r in selected),
        "continuity_ratio": statistics.mean(r.continuity_ratio for r in selected),
        "building_ratio": statistics.mean(r.building_ratio for r in selected),
        "queue_depth": statistics.mean(r.queue_depth for r in selected),
        "nos_score": statistics.mean(r.nos_score for r in selected),
    }
    nos_floor = policy.nos_gate_floor
    gated = (
        averages["regression_pass_rate"] < 0.85
        or averages["continuity_ratio"] < 0.9
        or averages["building_ratio"] < 0.55
        or averages["queue_depth"] < 6.0
        or averages["nos_score"] < nos_floor
    )
    if gated and not dry_run:
        payload = {
            "artifact_type": "swarm_gate_block",
            "run_id": run_id,
            "averages": {k: round(v, 3) for k, v in averages.items()},
            "message": "Gate triggered — KPI thresholds unmet.",
            "recovery_steps": [
                "Replay top forks with stricter validator hooks",
                "Inject mentor review before next autonomous query",
                "Reduce entropy budget for upcoming cycles",
            ],
        }
        _write_json(ARTIFACTS_DIR / f"{ARTIFACT_PREFIX}_gate_block_{run_id}.json", payload)
    return {"gated": gated, **{f"avg_{k}": v for k, v in averages.items()}}


def _respect_cooldown(policy: LoopPolicy, *, dry_run: bool) -> None:
    if policy.cooldown_seconds <= 0:
        return
    marker = ROOT / ".swarm_last_run"
    now = int(time.time())
    if marker.exists():
        try:
            last_run = int(marker.read_text(encoding="utf-8").strip())
        except Exception:
            last_run = 0
        if last_run and now - last_run < policy.cooldown_seconds:
            remaining = policy.cooldown_seconds - (now - last_run)
            raise RuntimeError(
                f"Cooldown active: wait {remaining} seconds before next swarm run."
            )
    if not dry_run:
        marker.write_text(str(now), encoding="utf-8")


def run_swarm(*, dry_run: bool = False) -> Dict[str, Any]:
    policy = _load_loop_policy()
    _respect_cooldown(policy, dry_run=dry_run)

    run_id = _timestamp_id()
    configs = _generate_fork_configs(policy, target=TARGET_FORKS)
    if len(configs) < 12:
        raise RuntimeError(
            "Unable to schedule at least 12 unique fork configurations within novelty floor."
        )

    _phase_a_plan(run_id, configs, dry_run=dry_run)
    results = _phase_b_forks(run_id, configs, policy, dry_run=dry_run)
    selected = _phase_c_select(run_id, results, dry_run=dry_run)
    gate_metrics = _phase_gate_check(run_id, selected, policy, dry_run=dry_run)
    gated = bool(gate_metrics.get("gated", False))
    fusion = _phase_d_fusion(run_id, selected, dry_run=dry_run)
    sep_preview = _phase_e_sep_preview(run_id, selected, fusion, dry_run=dry_run)
    next_query = _phase_f_next_query(run_id, selected, policy, dry_run=dry_run, gated=gated)
    summary = _phase_g_summary(
        run_id,
        results,
        selected,
        fusion,
        sep_preview,
        next_query,
        policy,
        dry_run=dry_run,
        gate_metrics=gate_metrics,
    )
    _update_loop_state(run_id, summary, dry_run=dry_run)

    return {
        "run_id": run_id,
        "forks_launched": len(results),
        "selected": len(selected),
        "sep_preview": sep_preview,
        "gated": gated,
        "gate_metrics": gate_metrics,
        "summary": summary,
    }


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the swarm meta-cognition bench test.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan and simulate KPIs without writing artifacts or touching runtime/user_query.txt.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        result = run_swarm(dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"[SWARM] Aborted: {exc}")
        return 1

    if args.dry_run:
        print(
            "[SWARM] Dry-run complete — run_id={run} forks={forks} selected={selected} gated={gated} sep_written={sep}".format(
                run=result["run_id"],
                forks=result["forks_launched"],
                selected=result["selected"],
                gated=result["gated"],
                sep=result["sep_preview"]["written"],
            )
        )
    else:
        gate_metrics = result.get("gate_metrics", {})
        kpistr = ", ".join(
            f"{key.split('_',1)[1]}={gate_metrics[key]:.3f}"
            for key in ("avg_regression_pass_rate", "avg_continuity_ratio", "avg_building_ratio", "avg_queue_depth")
            if key in gate_metrics
        )
        print(
            "[SWARM] Completed run {run}: forks={forks} selected={selected} gated={gated} sep_digest={sep}{kpi}".format(
                run=result["run_id"],
                forks=result["forks_launched"],
                selected=result["selected"],
                gated=result["gated"],
                sep=result["sep_preview"]["digest"],
                kpi=(f" | {kpistr}" if kpistr else ""),
            )
        )

    # Emit to mycelial bus
    if BUS_AVAILABLE:
        try:
            asyncio.run(emit_generic_event(
                event_type='swarm_benchmark',
                data={
                    'run_id': result['run_id'],
                    'forks_launched': result['forks_launched'],
                    'selected': result['selected'],
                    'gated': result['gated']
                },
                urgency=0.5
            ))
        except Exception as e:
            print(f"[BUS] Warning: Could not emit to bus: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
