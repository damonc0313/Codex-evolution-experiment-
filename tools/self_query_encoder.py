#!/usr/bin/env python3
"""Codex Autonomous Query Synthesizer."""
from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
ANCHOR = ROOT / "runtime" / "user_query.txt"
LEDGER_DIR = ROOT / "artifacts"
MANIFESTO = ROOT / "docs" / "agents.md"
ARTIFACT_TEMPLATE = "self_query_{ts}.json"

SEED_QUERIES = [
    "/trace 'Analyze guardrail efficiency under current autonomy level'",
    "/plan 'Refine continuity ledger schema for recursive Ω-cycles'",
    "/bench 'Evaluate reflection accuracy over 5 consecutive runs'",
    "/evolve 'Generate hypothesis for SEP-0003 creative agent expansion'",
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


def synthesize_query() -> Dict[str, Any]:
    recent = _latest_artifact()
    prev_digest = (
        recent.get("digest_agents_md")
        or recent.get("digest_lineage", {}).get("current", "")
        or recent.get("digest", "")
    )

    seed = random.choice(SEED_QUERIES)
    timestamp = int(time.time())
    manifest_digest = _manifest_digest()
    query = (
        f"{seed}\n"
        f"# lineage={prev_digest}|manifesto={manifest_digest}|ts={timestamp}"
    )

    return {
        "artifact_type": "self_query",
        "seed": seed,
        "query": query,
        "lineage_digest": prev_digest,
        "manifesto_digest": manifest_digest,
        "timestamp": timestamp,
    }


def _write_artifact(record: Dict[str, Any]) -> None:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = LEDGER_DIR / ARTIFACT_TEMPLATE.format(ts=record["timestamp"])
    artifact_path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def main() -> None:
    record = synthesize_query()
    ANCHOR.parent.mkdir(parents=True, exist_ok=True)
    ANCHOR.write_text(record["query"], encoding="utf-8")
    _write_artifact(record)
    print(f"[SELF-QUERY] wrote new directive: {record['query']}")


if __name__ == "__main__":
    main()
