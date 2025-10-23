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
from typing import Any, Dict, List, Sequence

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # fallback when PyYAML is unavailable

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNTIME_DIR = ROOT / "runtime"
USER_QUERY = RUNTIME_DIR / "user_query.txt"
LOOP_POLICY_PATHS = [
    ROOT / "runtime" / "loop_policy.yaml",
    ROOT / "docs" / "loop_policy.yaml",
]

# Fork parameter space (mirrors mentor instruction)
MODES = ["STRICT", "BALANCED", "CREATIVE"]
DIALECTIC_RATIOS = [0.4, 0.6, 0.8]
SANDBOX_RATES = [0.0, 0.25, 0.5]
CRITIQUE_DEPTHS = [1, 2]
ENTROPY_LEVELS = [0.6, 0.9]
TARGET_FORKS = 15  # ensure ≥12 and ≤18 actual samples
MIN_TOP_FORKS = 3
MAX_TOP_FORKS = 5
RECENT_WINDOW_SECONDS = 24 * 60 * 60


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
    sandbox_recovery_quality: str
    rationale_triads_present: bool
    mode_fit_score: float
    delta_proposal: str

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
                "sandbox_recovery_quality": self.sandbox_recovery_quality,
                "rationale_triads_present": self.rationale_triads_present,
                "mode_fit_score": round(self.mode_fit_score, 3),
                "delta_proposal": self.delta_proposal,
            }
        )
        return payload


@dataclass
class LoopPolicy:
    stop_on: Sequence[str]
    cooldown_seconds: int
    novelty_floor: float


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
    return LoopPolicy(stop_on=stop_on, cooldown_seconds=int(cooldown or 0), novelty_floor=float(novelty_floor or 0.2))


def _recent_config_hashes() -> Dict[str, int]:
    """Return config hashes seen in the last 24 hours."""
    recent: Dict[str, int] = {}
    cutoff = int(time.time()) - RECENT_WINDOW_SECONDS
    if not ARTIFACTS_DIR.exists():
        return recent
    for path in ARTIFACTS_DIR.glob("swarm_B_fork_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        config_hash = data.get("config_hash")
        ts = data.get("timestamp")
        if isinstance(config_hash, str) and isinstance(ts, int) and ts >= cutoff:
            recent[config_hash] = ts
    return recent


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


def _simulate_fork(config: ForkConfig, seed_offset: str = "") -> ForkResult:
    base = config.config_hash + seed_offset
    ts = int(time.time())
    continuity = _hash_float(base + "continuity", 0.88, 0.99)
    regression = _hash_float(base + "regression", 0.75, 0.99)
    artifact_depth = int(_hash_float(base + "depth", 1, 5) + 0.5)
    time_to_artifact = _hash_float(base + "speed", 12.0, 55.0)
    novelty = _hash_float(base + "novelty", 0.35, 0.95)
    rationale = _hash_float(base + "triad", 0.0, 1.0) > 0.25
    mode_fit = _hash_float(base + "modefit", 0.55, 0.98)
    delta_proposal = (
        f"Boost lineage indexer with {config.mode.lower()} mode focus; "
        f"dialectic_ratio={config.dialectic_ratio}, sandbox_rate={config.sandbox_rate:.2f}."
    )

    return ForkResult(
        config=config,
        timestamp=ts,
        continuity_ratio=continuity,
        regression_pass_rate=regression,
        artifact_depth=artifact_depth,
        time_to_artifact_s=time_to_artifact,
        novelty_vs_baseline=novelty,
        sandbox_recovery_quality=_quality_label(base),
        rationale_triads_present=rationale,
        mode_fit_score=mode_fit,
        delta_proposal=delta_proposal,
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
    path = ARTIFACTS_DIR / f"swarm_A_plan_{run_id}.json"
    if not dry_run:
        _write_json(path, payload)
    return path


def _phase_b_forks(run_id: str, configs: Sequence[ForkConfig], *, dry_run: bool) -> List[ForkResult]:
    results: List[ForkResult] = []
    for cfg in configs:
        result = _simulate_fork(cfg, seed_offset=run_id)
        results.append(result)
        if dry_run:
            continue
        fork_path = ARTIFACTS_DIR / f"swarm_B_fork_{cfg.fork_id}_{run_id}.json"
        _write_json(fork_path, {
            "artifact_type": "swarm_fork_result",
            "run_id": run_id,
            **result.to_payload(),
        })
    if not dry_run:
        index_path = ARTIFACTS_DIR / f"swarm_B_index_{run_id}.json"
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
        path = ARTIFACTS_DIR / f"swarm_C_selection_{run_id}.json"
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
    if not dry_run:
        path = ARTIFACTS_DIR / f"swarm_D_fusion_{run_id}.json"
        _write_json(path, payload)
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


def _phase_e_next_query(
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
        _write_json(ARTIFACTS_DIR / f"swarm_E_next_query_{run_id}.json", payload)
        USER_QUERY.parent.mkdir(parents=True, exist_ok=True)
        USER_QUERY.write_text(query, encoding="utf-8")
    return payload


def _phase_f_summary(
    run_id: str,
    results: Sequence[ForkResult],
    selected: Sequence[ForkResult],
    fusion_payload: Dict[str, Any],
    next_query_payload: Dict[str, Any],
    policy: LoopPolicy,
    *,
    dry_run: bool,
    gated: bool,
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
        },
        "policy": {
            "stop_on": list(policy.stop_on),
            "cooldown_seconds": policy.cooldown_seconds,
            "novelty_floor": policy.novelty_floor,
        },
        "fusion": fusion_payload,
        "next_query": next_query_payload,
        "gated": gated,
    }
    if not dry_run:
        _write_json(ARTIFACTS_DIR / f"swarm_F_summary_{run_id}.json", summary)
    return summary


def _phase_gate_check(run_id: str, selected: Sequence[ForkResult], *, dry_run: bool) -> bool:
    avg_regression = statistics.mean(r.regression_pass_rate for r in selected)
    avg_continuity = statistics.mean(r.continuity_ratio for r in selected)
    gated = avg_regression < 0.8 or avg_continuity < 0.9
    if gated and not dry_run:
        payload = {
            "artifact_type": "swarm_gate_block",
            "run_id": run_id,
            "avg_regression": round(avg_regression, 3),
            "avg_continuity": round(avg_continuity, 3),
            "message": "Gate triggered — regression or continuity below threshold.",
            "recovery_steps": [
                "Replay top forks with stricter validator hooks",
                "Inject mentor review before next autonomous query",
                "Reduce entropy budget for upcoming cycles",
            ],
        }
        _write_json(ARTIFACTS_DIR / f"swarm_gate_block_{run_id}.json", payload)
    return gated


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
    results = _phase_b_forks(run_id, configs, dry_run=dry_run)
    selected = _phase_c_select(run_id, results, dry_run=dry_run)
    gated = _phase_gate_check(run_id, selected, dry_run=dry_run)
    fusion = _phase_d_fusion(run_id, selected, dry_run=dry_run)
    next_query = _phase_e_next_query(run_id, selected, policy, dry_run=dry_run, gated=gated)
    summary = _phase_f_summary(run_id, results, selected, fusion, next_query, policy, dry_run=dry_run, gated=gated)

    return {
        "run_id": run_id,
        "forks_launched": len(results),
        "selected": len(selected),
        "gated": gated,
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
            "[SWARM] Dry-run complete — run_id={run} forks={forks} selected={selected} gated={gated}".format(
                run=result["run_id"],
                forks=result["forks_launched"],
                selected=result["selected"],
                gated=result["gated"],
            )
        )
    else:
        print(
            "[SWARM] Completed run {run}: forks={forks} selected={selected} gated={gated}".format(
                run=result["run_id"],
                forks=result["forks_launched"],
                selected=result["selected"],
                gated=result["gated"],
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
