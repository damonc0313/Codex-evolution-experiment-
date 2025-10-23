#!/usr/bin/env python3
"""Codex Autonomous Query Synthesizer.

Enhanced with build-first heuristic from Kael's empirical discoveries.
Biases query generation toward concrete artifact creation when building_ratio
or cascade_probability falls below thresholds.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
ANCHOR = ROOT / "runtime" / "user_query.txt"
LEDGER_DIR = ROOT / "artifacts"
MANIFESTO = ROOT / "docs" / "agents.md"
LOOP_POLICY = ROOT / "runtime" / "loop_policy.yaml"
CONTINUITY_LEDGER = ROOT / "continuity_ledger.jsonl"
ARTIFACT_TEMPLATE = "self_query_{ts}.json"

# BUILDING-FOCUSED QUERIES (weight: 0.60)
# Concrete artifact creation - higher confidence (0.90-0.95)
BUILDING_QUERIES = [
    "/plan 'Design distributed task-queue balancer with retry logic'",
    "/spec 'Multi-agent coordination protocol for parallel validation'",
    "/build 'Implement cascade probability tracker with real-time monitoring'",
    "/plan 'Refine continuity ledger schema for recursive Ω-cycles'",
    "/implement 'Auto-recovery handler for continuity_low condition'",
    "/create 'Swarm validation harness for building_ratio optimization'",
    "/build 'Metrics dashboard for continuous operation KPIs'",
    "/plan 'Task decomposition engine with novelty scoring'",
]

# ANALYSIS-FOCUSED QUERIES (weight: 0.25)
# Abstract analysis - lower confidence (0.70-0.75)
ANALYSIS_QUERIES = [
    "/trace 'Analyze guardrail efficiency under current autonomy level'",
    "/analyze 'Building ratio patterns across last 20 cycles'",
    "/reflect 'Cascade probability trends and inflection points'",
    "/critique 'Current loop policy effectiveness'",
    "/review 'Task multiplication anomalies in recent swarm runs'",
]

# HYBRID QUERIES (weight: 0.15)
# Mixed building + analysis
HYBRID_QUERIES = [
    "/bench 'Evaluate reflection accuracy over 5 consecutive runs'",
    "/evolve 'Generate hypothesis for SEP-0003 creative agent expansion'",
    "/fractal 'Multi-scale analysis of continuous operation mechanics'",
    "/bench 'Swarm diversity vs convergence trade-off exploration'",
]


def _latest_artifact() -> Dict[str, Any]:
    if not LEDGER_DIR.exists():
        return {}
    try:
        files = sorted(
            LEDGER_DIR.glob("*.json"),
            key=lambda candidate: candidate.stat().st_mtime,
            reverse=True,
        )
    except FileNotFoundError:
        return {}
    for entry in files:
        try:
            return json.loads(entry.read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _manifest_digest() -> str:
    if not MANIFESTO.exists():
        return "00000000"
    return hashlib.sha256(MANIFESTO.read_bytes()).hexdigest()[:8]


def _load_loop_policy() -> Dict[str, Any]:
    """Load loop policy with continuous operation targets."""
    if not LOOP_POLICY.exists() or yaml is None:
        return {}

    try:
        return yaml.safe_load(LOOP_POLICY.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _load_latest_metrics() -> Optional[Dict[str, Any]]:
    """Load most recent continuous operation metrics."""
    metrics_file = LEDGER_DIR / "continuous_operation_metrics.json"
    if not metrics_file.exists():
        return None

    try:
        return json.loads(metrics_file.read_text(encoding="utf-8"))
    except Exception:
        return None


def _compute_query_weights(policy: Dict[str, Any], metrics: Optional[Dict[str, Any]]) -> Dict[str, float]:
    """Compute dynamic query weights based on current metrics.

    Implements build-first heuristic:
    - If building_ratio < threshold: boost building weight to 0.75
    - If cascade_probability < threshold: boost building weight to 0.70
    - If queue_depth < threshold: boost multi-step building queries
    """
    # Default weights from policy
    default_weights = {
        "building": 0.60,
        "analysis": 0.25,
        "hybrid": 0.15
    }

    policy_weights = policy.get("self_query_weights", {})
    if policy_weights:
        default_weights["building"] = policy_weights.get("building_commands", {}).get("weight", 0.60)
        default_weights["analysis"] = policy_weights.get("analysis_commands", {}).get("weight", 0.25)
        default_weights["hybrid"] = policy_weights.get("hybrid_commands", {}).get("weight", 0.15)

    # If no metrics available, use defaults
    if not metrics or "metrics" not in metrics:
        return default_weights

    # Extract current metric values
    current_metrics = metrics["metrics"]
    building_ratio = current_metrics.get("building_ratio", 0.5)
    cascade_prob = current_metrics.get("cascade_probability", 2.0)
    queue_depth = current_metrics.get("queue_depth", 5)

    # Get thresholds
    targets = policy.get("continuous_operation_targets", {})
    building_min = targets.get("building_ratio_min", 0.55)
    cascade_min = targets.get("cascade_probability_min", 2.0)
    queue_min = targets.get("task_queue_min", 6)

    # Dynamic weight adjustment
    weights = default_weights.copy()

    # Boost building if metrics below threshold
    if building_ratio < building_min:
        weights["building"] = 0.75
        weights["analysis"] = 0.15
        weights["hybrid"] = 0.10

    if cascade_prob < cascade_min:
        weights["building"] = max(weights["building"], 0.70)
        weights["analysis"] = 0.20
        weights["hybrid"] = 0.10

    if queue_depth < queue_min:
        # Prefer multi-step building tasks
        weights["building"] = max(weights["building"], 0.65)
        weights["hybrid"] = 0.20  # Hybrid often creates compound tasks
        weights["analysis"] = 0.15

    # Normalize to sum to 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: v/total for k, v in weights.items()}

    return weights


def _weighted_choice(queries_by_type: Dict[str, List[str]], weights: Dict[str, float]) -> tuple[str, str]:
    """Select query using weighted random choice.

    Returns: (query_type, query_string)
    """
    types = list(weights.keys())
    type_weights = [weights[t] for t in types]

    # Weighted random selection
    selected_type = random.choices(types, weights=type_weights, k=1)[0]
    selected_query = random.choice(queries_by_type[selected_type])

    return selected_type, selected_query


def synthesize_query() -> Dict[str, Any]:
    """Synthesize autonomous query with build-first bias.

    Uses continuous operation metrics to dynamically adjust query selection
    toward building (concrete artifacts) when metrics fall below thresholds.
    """
    recent = _latest_artifact()
    prev_digest = (
        recent.get("digest_agents_md")
        or recent.get("digest_lineage", {}).get("current", "")
        or recent.get("digest", "")
    )

    # Load policy and metrics
    policy = _load_loop_policy()
    metrics = _load_latest_metrics()

    # Compute dynamic weights
    weights = _compute_query_weights(policy, metrics)

    # Select query based on weights
    queries_by_type = {
        "building": BUILDING_QUERIES,
        "analysis": ANALYSIS_QUERIES,
        "hybrid": HYBRID_QUERIES
    }

    query_type, seed = _weighted_choice(queries_by_type, weights)

    timestamp = int(time.time())
    manifest_digest = _manifest_digest()

    # Include metrics context in query metadata
    metrics_context = ""
    if metrics and "metrics" in metrics:
        m = metrics["metrics"]
        metrics_context = (
            f"building_ratio={m.get('building_ratio', 0):.2f}|"
            f"cascade_prob={m.get('cascade_probability', 0):.2f}|"
            f"queue={m.get('queue_depth', 0)}"
        )

    query = (
        f"{seed}\n"
        f"# lineage={prev_digest}|manifesto={manifest_digest}|ts={timestamp}\n"
        f"# type={query_type}|weights=B{weights['building']:.2f}_A{weights['analysis']:.2f}_H{weights['hybrid']:.2f}"
    )

    if metrics_context:
        query += f"|{metrics_context}"

    return {
        "artifact_type": "self_query",
        "seed": seed,
        "query": query,
        "query_type": query_type,
        "weights_applied": weights,
        "lineage_digest": prev_digest,
        "manifesto_digest": manifest_digest,
        "timestamp": timestamp,
        "metrics_snapshot": metrics.get("metrics", {}) if metrics else {}
    }


def _write_artifact(record: Dict[str, Any]) -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = LEDGER_DIR / ARTIFACT_TEMPLATE.format(ts=record["timestamp"])
    artifact_path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def main() -> None:
    generate_query()


if __name__ == "__main__":
    main()
