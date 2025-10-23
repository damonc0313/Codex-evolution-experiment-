#!/usr/bin/env python3
"""Generate natural heuristic reflection artifacts for swarm runs."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Dict, List

from ledger_metrics import DEFAULT_NOS_WEIGHTS, compute_nos_score, map_nature_to_kpis
from nos_calibration import DEFAULT_WEIGHTS as CAL_DEFAULTS, calibrate_weights, prepare_samples
from nos_data_sources import extract_primitives, load_config, summarise_sources

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
REFLECTION_DOC = ROOT / "docs" / "REFLECTION_swarm_nature_synthesis.md"
NOS_DOC = ROOT / "docs" / "NATURAL_OPTIMISATION_SIGNATURE.md"
NOS_SOURCES_ARTIFACT = ARTIFACTS_DIR / "nos_sources_index.json"
NOS_FEATURES_ARTIFACT = ARTIFACTS_DIR / "nos_features.json"
NOS_CALIBRATION_ARTIFACT = ARTIFACTS_DIR / "nos_calibration.json"
NOS_INGEST_ARTIFACT = ARTIFACTS_DIR / "nos_ingest_report.json"
HEURISTICS_ARTIFACT = ARTIFACTS_DIR / "natural_heuristics_synthesis.json"
TELEMETRY_ARTIFACT = ARTIFACTS_DIR / "swarm_gate_telemetry.json"


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_swarm_metrics() -> Dict[str, float]:
    metrics: Dict[str, List[float]] = {}
    if not ARTIFACTS_DIR.exists():
        return {}
    for path in ARTIFACTS_DIR.glob("swarm_full_B_fork_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for key in (
            "continuity_ratio",
            "regression_pass_rate",
            "novelty_vs_baseline",
            "time_to_artifact_s",
            "building_ratio",
            "task_multiplication",
            "cascade_probability",
            "queue_depth",
            "nos_score",
        ):
            value = data.get(key)
            if isinstance(value, (int, float)):
                metrics.setdefault(key, []).append(float(value))
    return {k: statistics.mean(v) for k, v in metrics.items() if v}


def _stamp_digest(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    neutral_lines: List[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("digest:"):
            neutral_lines.append(line.split("digest:", 1)[0] + "digest: ")
        else:
            neutral_lines.append(line)
    newline = "\n" if content.endswith("\n") else ""
    digest = __import__("hashlib").sha256("\n".join(neutral_lines).encode("utf-8")).hexdigest()[:16]
    stamped_lines: List[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("digest:"):
            prefix = line.split("digest:", 1)[0]
            stamped_lines.append(prefix + f"digest: {digest}")
        else:
            stamped_lines.append(line)
    path.write_text("\n".join(stamped_lines) + newline, encoding="utf-8")
    return digest


def _render_nos_doc(weights: Dict[str, float], primitives: Dict[str, float]) -> str:
    sections = [
        "# Natural Optimisation Signature",
        "",
        "The Natural Optimisation Signature (NOS) blends Kael KPIs with principles",
        "drawn from real-world evolutionary systems.  Each component is sourced",
        "from ingestible datasets and normalised before weights are applied.",
        "",
        "## Components",
        "- **Energy efficiency** → mutation rate / selection gradient proxies.",
        "- **Coherence** → fitness landscape peaks reinforcing lineage structure.",
        "- **Resilience** → population dynamic stability and carrying capacity.",
        "- **Entropy** → exploration diversity derived from landscape ruggedness.",
        "",
        "## Current Weights",
    ]
    for key in ("energy_efficiency", "coherence", "resilience", "entropy"):
        value = weights.get(key, DEFAULT_NOS_WEIGHTS[key])
        sections.append(f"- **{key}**: {value:.3f}")
    sections.extend(
        [
            "",
            "## Latest Primitives",
        ]
    )
    if primitives:
        for key, value in primitives.items():
            sections.append(f"- **{key}**: {value:.3f}")
    else:
        sections.append("- No primitives extracted; defaults retained.")
    sections.extend(
        [
            "",
            "## Formula",
            "```text",
            "nos_score = ((w_e × energy_efficiency) × (w_c × coherence) × (w_r × resilience)) / (w_h × entropy)",
            "```",
            "",
            "## Operational Guidance",
            "1. Persist `runtime/nos_sources.yaml` alongside dataset digests.",
            "2. When new datasets land, re-run the ingestion + calibration helper.",
            "3. Promote validator soft checks to hard failures once telemetry stabilises.",
        ]
    )
    front_matter = [
        "---",
        "artifact_type: heuristic_spec",
        "title: Natural Optimisation Signature",
        "digest: TEMP",
        "sources:",
        "  - runtime/nos_sources.yaml",
        "  - tools/nos_data_sources.py",
        "  - tools/nos_calibration.py",
        "---",
        "",
    ]
    NOS_DOC.parent.mkdir(parents=True, exist_ok=True)
    NOS_DOC.write_text("\n".join(front_matter + sections) + "\n", encoding="utf-8")
    return _stamp_digest(NOS_DOC)


def _render_reflection_doc(metrics: Dict[str, float], nos_digest: str, weights: Dict[str, float]) -> None:
    sections = [
        "# Swarm ↔ Nature Reflection",
        "",
        "## Summary",
        "- Captured NOS-aware telemetry from swarm runs and evolutionary datasets.",
        "- Calibrated weights from ingestible sources and prepared audit artifacts.",
        "- Outlined next dials for loop policy integration and validator promotion.",
        "",
        "## KPI Snapshot",
    ]
    if metrics:
        for key, value in sorted(metrics.items()):
            sections.append(f"- **{key}**: {value:.3f}")
    else:
        sections.append("- No swarm fork artifacts detected; metrics deferred.")
    sections.extend(
        [
            "",
            "## NOS Overview",
            "- Digest: ``{}``".format(nos_digest),
        ]
    )
    for key in ("energy_efficiency", "coherence", "resilience", "entropy"):
        sections.append(f"- Weight {key}: {weights.get(key, CAL_DEFAULTS[key]):.3f}")
    sections.extend(
        [
            "",
            "## Next Steps",
            "1. Sync swarm gating with NOS delta thresholds (≥ +0.05).",
            "2. Run Kael KPI bench post-integration to verify trend lines.",
            "3. Draft SEP-0006 to govern dataset provenance and validator promotion.",
        ]
    )
    front_matter = [
        "---",
        "artifact_type: reflection",
        f"generated_at: {int(time.time())}",
        "title: Swarm Nature Synthesis",
        "digest: TEMP",
        "sources:",
        "  - artifacts/swarm_full_B_fork_*.json",
        "  - docs/NATURAL_OPTIMISATION_SIGNATURE.md",
        "  - tools/natural_reflection.py",
        "  - tools/nos_calibration.py",
        "---",
        "",
    ]
    REFLECTION_DOC.parent.mkdir(parents=True, exist_ok=True)
    REFLECTION_DOC.write_text("\n".join(front_matter + sections) + "\n", encoding="utf-8")
    _stamp_digest(REFLECTION_DOC)


def run(*, dry_run: bool = False) -> Dict[str, object]:
    specs = load_config()
    summaries = summarise_sources(specs)
    primitives = extract_primitives(summaries)
    samples = prepare_samples(primitives)
    weights = calibrate_weights(samples) if samples else DEFAULT_NOS_WEIGHTS

    metrics = _load_swarm_metrics()
    nos_score = compute_nos_score(
        primitives.get("energy_efficiency", 0.0),
        primitives.get("coherence", 0.0),
        primitives.get("resilience", 0.0),
        primitives.get("entropy", 1.0),
        weights=weights,
    )

    heuristics_payload = {
        "artifact_type": "natural_heuristics_synthesis",
        "heuristics": [
            {
                "heuristic_name": "memetic_local_search",
                "origin_domain": "evolutionary computation",
                "mapping_to_codex_metric": {"mutation_rate": "refactor_rate", "fitness": "build_ratio"},
                "policy_suggestion": {"mutation_factor": 0.2, "local_refactor_budget": "small"},
                "expected_effect": "Balances exploration with directed improvement",
            },
            {
                "heuristic_name": "multi_optima_branching",
                "origin_domain": "fitness landscapes",
                "mapping_to_codex_metric": {"population_size": "fork_count", "speciation": "module_variants"},
                "policy_suggestion": {"swarm_branching": 3, "novelty_floor": 0.35},
                "expected_effect": "Avoids premature convergence",
            },
            {
                "heuristic_name": "energy_minimisation",
                "origin_domain": "protein folding",
                "mapping_to_codex_metric": {"energy": "latency_budget_ms"},
                "policy_suggestion": {"complexity_budget": "tighten 5%"},
                "expected_effect": "Leaner artifacts; reduced strain",
            },
            {
                "heuristic_name": "swarm_resilience_rules",
                "origin_domain": "ant colonies",
                "mapping_to_codex_metric": {"pheromones": "artifact_signals"},
                "policy_suggestion": {"sandbox_rate": 0.25, "stagnation_probe": "on"},
                "expected_effect": "Stable exploration",
            },
            {
                "heuristic_name": "adaptive_mutation_pressure",
                "origin_domain": "evolutionary dynamics",
                "mapping_to_codex_metric": {"fitness_plateau": "flat_build_ratio"},
                "policy_suggestion": {"mutation_factor_range": [0.15, 0.35]},
                "expected_effect": "Escapes stagnation",
            },
        ],
        "nos_score": nos_score,
        "weights": weights,
    }

    if not dry_run:
        _write_json(
            NOS_SOURCES_ARTIFACT,
            {
                "artifact_type": "nos_sources_index",
                "sources": [summary.to_payload() for summary in summaries],
            },
        )
        _write_json(
            NOS_INGEST_ARTIFACT,
            {
                "artifact_type": "nos_ingest_report",
                "counts": {summary.spec.source_id: summary.row_count for summary in summaries},
            },
        )
        _write_json(NOS_FEATURES_ARTIFACT, {"artifact_type": "nos_features", "primitives": primitives})
        _write_json(
            NOS_CALIBRATION_ARTIFACT,
            {
                "artifact_type": "nos_calibration",
                "weights": weights,
                "defaults": CAL_DEFAULTS,
            },
        )
        _write_json(HEURISTICS_ARTIFACT, heuristics_payload)
        _write_json(
            TELEMETRY_ARTIFACT,
            {
                "artifact_type": "swarm_gate_telemetry",
                "metrics": metrics,
                "nos_score": nos_score,
            },
        )
    nos_digest = _render_nos_doc(weights, primitives)
    _render_reflection_doc(metrics, nos_digest, weights)
    return {
        "weights": weights,
        "metrics": metrics,
        "nos_score": nos_score,
        "policy_deltas": map_nature_to_kpis(heuristics_payload["heuristics"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Collect data without writing artifacts")
    args = parser.parse_args()
    result = run(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
