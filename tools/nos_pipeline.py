#!/usr/bin/env python3
"""Orchestrate the NOS real-data ingestion and calibration pipeline.

This script implements the multi-phase routine described in the
"NOS — Real-World Data Ingestion & Calibration" command.  It is designed to be
idempotent and auditable: each phase emits artifacts under ``artifacts/`` and
critical files are snapshotted so a gate failure can roll back changes.

The pipeline can also run in ``--dry-run`` mode which performs planning and
reporting without mutating the working tree.  This is useful for unit tests and
local rehearsals.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:  # PyYAML is optional until dependencies are bootstrapped
    import yaml  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - dependency hint
    print("ERROR: PyYAML is required. Install dependencies via `pip install -r requirements.txt`.", file=sys.stderr)
    raise SystemExit(1) from exc

from ledger_metrics import DEFAULT_NOS_WEIGHTS
from nos_calibration import DEFAULT_WEIGHTS, calibrate_weights, prepare_samples
from nos_data_sources import load_config, summarise_sources, extract_primitives
from swarm_bench import run_swarm

# ---------------------------------------------------------------------------
# Constants and helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNTIME_DIR = ROOT / "runtime"
DOCS_DIR = ROOT / "docs"

DEFAULT_SOURCES = [
    {
        "kind": "evolution_rates",
        "id": "evo_rates_01",
        "path": "data/evo/evo_rates.csv",
        "fields": {
            "mutation_rate": "float",
            "selection_gradient": "float",
            "generation_time": "float",
        },
    },
    {
        "kind": "population_dynamics",
        "id": "pop_dyn_01",
        "path": "data/evo/pop_dyn.json",
        "fields": {
            "birth_rate": "float",
            "death_rate": "float",
            "carrying_capacity": "float",
        },
    },
    {
        "kind": "fitness_landscapes",
        "id": "fit_land_01",
        "path": "data/evo/fitness_land.parquet",
        "fields": {
            "ruggedness": "float",
            "peaks": "int",
            "neutrality": "float",
        },
    },
]

NOS_DOC = DOCS_DIR / "NATURAL_OPTIMISATION_SIGNATURE.md"
REFLECTION_DOC = DOCS_DIR / "REFLECTION_swarm_nature_synthesis.md"

def _timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")


def _stamp_digest(path: Path) -> str:
    """Stamp canonical digest into a markdown file."""

    if not path.exists():
        return ""
    raw = path.read_text(encoding="utf-8")
    neutral_lines: List[str] = []
    for line in raw.splitlines():
        if line.lstrip().startswith("digest:"):
            neutral_lines.append(line.split("digest:", 1)[0] + "digest: ")
        else:
            neutral_lines.append(line)
    digest = __import__("hashlib").sha256("\n".join(neutral_lines).encode("utf-8")).hexdigest()[:16]
    stamped_lines: List[str] = []
    for line in raw.splitlines():
        if line.lstrip().startswith("digest:"):
            prefix = line.split("digest:", 1)[0]
            stamped_lines.append(prefix + f"digest: {digest}")
        else:
            stamped_lines.append(line)
    newline = "\n" if raw.endswith("\n") else ""
    path.write_text("\n".join(stamped_lines) + newline, encoding="utf-8")
    return digest


def _round_weights(weights: Dict[str, float]) -> Dict[str, float]:
    return {key: round(float(value), 3) for key, value in weights.items()}


@dataclass
class PipelineSummary:
    primitives: Dict[str, float]
    weights: Dict[str, float]
    gate_metrics: Dict[str, Any] = field(default_factory=dict)
    delta_nos: float = 0.0
    run_id: Optional[str] = None
    gated: bool = False


class NosRealDataPipeline:
    """Encapsulates the NOS ingestion pipeline so it can be unit tested."""

    def __init__(self, root: Path, *, dry_run: bool = False):
        self.root = root
        self.dry_run = dry_run
        self.artifacts_dir = root / "artifacts"
        self.runtime_dir = root / "runtime"
        self.docs_dir = root / "docs"
        self.config_path = self.runtime_dir / "nos_sources.yaml"
        self.policy_path = self.runtime_dir / "loop_policy.yaml"
        self.user_query_path = self.runtime_dir / "user_query.txt"
        self.loop_state_path = self.runtime_dir / "loop_state.json"
        self.backups: Dict[Path, Optional[str]] = {}

    # ------------------------------------------------------------------
    # backup helpers
    # ------------------------------------------------------------------
    def _snapshot(self, path: Path) -> None:
        if path in self.backups:
            return
        if path.exists():
            self.backups[path] = path.read_text(encoding="utf-8")
        else:
            self.backups[path] = None

    def _rollback(self, reason: str) -> None:
        for path, content in self.backups.items():
            if content is None:
                if path.exists():
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        payload = {
            "artifact_type": "nos_counterfactual",
            "generated_at": _timestamp(),
            "reason": reason,
            "recovery_steps": [
                "Install or verify evolutionary datasets",
                "Lower mutation factor temporarily and rerun calibration",
                "Review swarm gate metrics before re-enabling autonomous loop",
            ],
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_counterfactual.json", payload)

    # ------------------------------------------------------------------
    # phases
    # ------------------------------------------------------------------
    def phase_sources(self) -> List[Any]:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        data: Dict[str, Any]
        if self.config_path.exists():
            try:
                data = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
            except Exception:
                data = {}
        else:
            data = {}
        data.setdefault("schema_version", 1)
        sources = data.setdefault("sources", [])
        ids = {entry.get("id") for entry in sources if isinstance(entry, dict)}
        for entry in DEFAULT_SOURCES:
            if entry["id"] not in ids:
                sources.append(entry.copy())
        sources = [entry for entry in sources if isinstance(entry, dict)]
        data["sources"] = sources
        if not self.dry_run:
            self._snapshot(self.config_path)
            self.config_path.write_text(
                yaml.safe_dump(data, sort_keys=False),
                encoding="utf-8",
            )
        specs = load_config(self.config_path, root=self.root)
        summaries = summarise_sources(specs)
        index_payload = {
            "artifact_type": "nos_sources_index",
            "generated_at": _timestamp(),
            "sources": [summary.to_payload() for summary in summaries],
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_sources_index.json", index_payload)
        return summaries

    def phase_ingest(self, summaries: Iterable[Any]) -> Dict[str, Any]:
        payload = {
            "artifact_type": "nos_ingest_report",
            "generated_at": _timestamp(),
            "sources": [summary.to_payload() for summary in summaries],
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_ingest_report.json", payload)
        return payload

    def phase_features(self, summaries: Iterable[Any]) -> Dict[str, float]:
        primitives = extract_primitives(summaries)
        payload = {
            "artifact_type": "nos_features",
            "generated_at": _timestamp(),
            "primitives": primitives,
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_features.json", payload)
        return primitives

    def phase_calibration(self, primitives: Dict[str, float]) -> Dict[str, float]:
        samples = prepare_samples(primitives)
        if samples:
            weights = calibrate_weights(samples)
            method = "calibrated"
        else:
            weights = DEFAULT_WEIGHTS.copy()
            method = "defaults"
        payload = {
            "artifact_type": "nos_calibration",
            "generated_at": _timestamp(),
            "method": method,
            "weights": _round_weights(weights),
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_calibration.json", payload)
        return weights

    def _merge_policy(self, weights: Dict[str, float]) -> Dict[str, Any]:
        if self.policy_path.exists():
            try:
                policy = yaml.safe_load(self.policy_path.read_text(encoding="utf-8")) or {}
            except Exception:
                policy = {}
        else:
            policy = {}
        natural = policy.setdefault("natural_optimisation", {})
        natural["enabled"] = True
        natural.setdefault("mutation_factor", 0.2)
        natural.setdefault("swarm_branching", 3)
        natural.setdefault("multi_optima_bias", True)
        natural.setdefault("anneal_on_plateau", True)
        nos_cfg = natural.setdefault("nos", {})
        nos_cfg["sources_config"] = "runtime/nos_sources.yaml"
        nos_cfg["weights"] = _round_weights({**DEFAULT_NOS_WEIGHTS, **weights})
        nos_cfg.setdefault("gate_floor", 0.05)
        targets = policy.setdefault("continuous_operation_targets", {})
        targets.setdefault("task_queue_min", 6)
        targets.setdefault("building_ratio_min", 0.55)
        targets.setdefault("task_multiplication_min", 1.6)
        stop_on = list(policy.get("stop_on", []))
        for token in ["ci_fail", "digest_mismatch", "continuity_low", "regressions_spike"]:
            if token not in stop_on:
                stop_on.append(token)
        policy["stop_on"] = stop_on
        policy.setdefault("cooldown_seconds", 8)
        policy.setdefault("novelty_floor", 0.35)
        if not self.dry_run:
            self._snapshot(self.policy_path)
            self.policy_path.write_text(
                yaml.safe_dump(policy, sort_keys=False),
                encoding="utf-8",
            )
            artifact = {
                "artifact_type": "policy_merge_nos",
                "generated_at": _timestamp(),
                "weights": _round_weights(weights),
            }
            _write_json(self.artifacts_dir / "policy_merge_nos.json", artifact)
        return policy

    def _load_baseline_nos(self) -> float:
        if not self.loop_state_path.exists():
            return 0.0
        try:
            data = json.loads(self.loop_state_path.read_text(encoding="utf-8"))
        except Exception:
            return 0.0
        summary = data.get("summary", {})
        gate = summary.get("gate_metrics", {})
        value = gate.get("avg_nos_score")
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def phase_swarm(self, policy: Dict[str, Any], weights: Dict[str, float]) -> PipelineSummary:
        if self.dry_run:
            return PipelineSummary(primitives={}, weights=weights, gate_metrics={}, delta_nos=0.0)
        self._snapshot(self.user_query_path)
        self._snapshot(self.loop_state_path)
        result = run_swarm(dry_run=False)
        gate_metrics = result.get("gate_metrics", {})
        avg_nos = float(gate_metrics.get("avg_nos_score", 0.0))
        baseline = self._load_baseline_nos()
        delta = avg_nos - baseline if baseline else avg_nos
        gated = bool(result.get("gated"))
        if delta < 0.05:
            gated = True
            gate_metrics["delta_nos_score"] = delta
        summary = PipelineSummary(
            primitives={},
            weights=weights,
            gate_metrics=gate_metrics,
            delta_nos=round(delta, 3),
            run_id=result.get("run_id"),
            gated=gated,
        )
        summary.primitives = {}
        summary.gate_metrics = gate_metrics
        return summary

    def _render_docs(
        self,
        primitives: Dict[str, float],
        weights: Dict[str, float],
        gate_metrics: Dict[str, Any],
    ) -> None:
        if self.dry_run:
            return
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        nos_lines = [
            "---",
            "artifact_type: heuristic_spec",
            "title: Natural Optimisation Signature",
            "digest: TEMP",
            "sources:",
            "  - runtime/nos_sources.yaml",
            "  - artifacts/nos_calibration.json",
            "---",
            "",
            "# Natural Optimisation Signature (NOS)",
            "",
            "The NOS blends Kael KPIs with real-world evolutionary datasets.",
            "",
            "## Weights",
        ]
        for key in ("energy_efficiency", "coherence", "resilience", "entropy"):
            nos_lines.append(f"- **{key}**: {weights.get(key, DEFAULT_NOS_WEIGHTS[key]):.3f}")
        nos_lines.append("")
        nos_lines.append("## Primitives")
        if primitives:
            for key, value in primitives.items():
                nos_lines.append(f"- **{key}**: {value:.3f}")
        else:
            nos_lines.append("- No primitives extracted; defaults remain active.")
        NOS_DOC.write_text("\n".join(nos_lines) + "\n", encoding="utf-8")
        digest = _stamp_digest(NOS_DOC)

        reflection_lines = [
            "# Swarm ↔ Nature Reflection",
            "",
            f"- Generated: {_timestamp()}",
            f"- NOS digest: {digest}",
            "",
            "## Gate Metrics",
        ]
        if gate_metrics:
            for key, value in sorted(gate_metrics.items()):
                if isinstance(value, float):
                    reflection_lines.append(f"- **{key}**: {value:.3f}")
                else:
                    reflection_lines.append(f"- **{key}**: {value}")
        else:
            reflection_lines.append("- No swarm metrics available; run skipped.")
        REFLECTION_DOC.write_text("\n".join(reflection_lines) + "\n", encoding="utf-8")
        _stamp_digest(REFLECTION_DOC)

    def _update_telemetry(self, run_id: Optional[str], gate_metrics: Dict[str, Any], weights: Dict[str, float]) -> None:
        if self.dry_run:
            return
        telemetry_path = self.artifacts_dir / "swarm_gate_telemetry.json"
        payload = {
            "runs": [],
            "last_run_id": run_id,
            "generated_at": _timestamp(),
        }
        if telemetry_path.exists():
            try:
                payload = json.loads(telemetry_path.read_text(encoding="utf-8"))
            except Exception:
                payload = {"runs": []}
        payload.setdefault("runs", [])
        payload["runs"].append(
            {
                "run_id": run_id,
                "gate_metrics": gate_metrics,
                "weights": _round_weights(weights),
                "timestamp": _timestamp(),
            }
        )
        payload["last_run_id"] = run_id
        if not self.dry_run:
            _write_json(telemetry_path, payload)

    def _ledger_entry(self, summary: PipelineSummary) -> None:
        if self.dry_run:
            return
        nos_score = float(summary.gate_metrics.get("avg_nos_score", 0.0))
        cascade = float(summary.gate_metrics.get("avg_cascade_probability", 0.0)) if "avg_cascade_probability" in summary.gate_metrics else None
        payload = {
            "artifact_type": "ledger_entry_nos_realdata",
            "generated_at": _timestamp(),
            "run_id": summary.run_id,
            "kpis": {
                "avg_regression_pass_rate": summary.gate_metrics.get("avg_regression_pass_rate"),
                "avg_continuity_ratio": summary.gate_metrics.get("avg_continuity_ratio"),
                "avg_building_ratio": summary.gate_metrics.get("avg_building_ratio"),
                "avg_queue_depth": summary.gate_metrics.get("avg_queue_depth"),
                "avg_nos_score": summary.gate_metrics.get("avg_nos_score"),
                "avg_cascade_probability": cascade,
            },
            "delta_nos": summary.delta_nos,
        }
        _write_json(self.artifacts_dir / "ledger_entry_nos_realdata.json", payload)

    def _write_next_query(self) -> None:
        if self.dry_run:
            return
        query = (
            "/evolve 'Implement memetic local-refactor pass tuned by NOS weights; "
            "re-run swarm with branching=3 and mutation_factor auto-tuned on plateau'"
        )
        self._snapshot(self.user_query_path)
        self.user_query_path.parent.mkdir(parents=True, exist_ok=True)
        self.user_query_path.write_text(query + "\n", encoding="utf-8")

    def run(self) -> PipelineSummary:
        summaries = self.phase_sources()
        self.phase_ingest(summaries)
        primitives = self.phase_features(summaries)
        weights = self.phase_calibration(primitives)
        policy = self._merge_policy(weights)
        summary = self.phase_swarm(policy, weights)
        if summary.gated:
            if not self.dry_run:
                self._rollback("Swarm gates blocked NOS promotion")
            return summary
        self._render_docs(primitives, {**DEFAULT_NOS_WEIGHTS, **weights}, summary.gate_metrics)
        self._update_telemetry(summary.run_id, summary.gate_metrics, weights)
        self._ledger_entry(summary)
        self._write_next_query()
        overall = {
            "artifact_type": "nos_pipeline_summary",
            "generated_at": _timestamp(),
            "run_id": summary.run_id,
            "delta_nos": summary.delta_nos,
            "gated": summary.gated,
            "weights": _round_weights({**DEFAULT_NOS_WEIGHTS, **weights}),
        }
        if not self.dry_run:
            _write_json(self.artifacts_dir / "nos_pipeline_summary.json", overall)
        return summary


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NOS real-data ingestion pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Plan the pipeline without writing outputs")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    pipeline = NosRealDataPipeline(ROOT, dry_run=args.dry_run)
    summary = pipeline.run()
    if summary.gated:
        print("[NOS] Gate triggered — see artifacts/nos_counterfactual.json for recovery plan")
        return 1 if not args.dry_run else 0
    print(
        "[NOS] Calibration complete — run={run} Δnos={delta:.3f}".format(
            run=summary.run_id or "dry-run",
            delta=summary.delta_nos,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
