#!/usr/bin/env python3
"""Ledger Utilities - Artifact Writing with Lineage Integration

Wires LineageWeaver into artifact persistence layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from tools.lineage_weaver import LineageWeaver

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
LEDGER_PATH = ROOT / "continuity_ledger.jsonl"


def write_artifact(
    artifact: Dict[str, Any],
    out_path: Path,
    parents: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Write artifact with lineage metadata to file and ledger.

    Args:
        artifact: Artifact data to write
        out_path: Path to save artifact JSON
        parents: List of parent artifacts (for lineage tracking)
    """
    # Wire lineage tracking
    lw = LineageWeaver(out_path.parent)
    artifact = lw.weave(artifact, parents or [])

    # Write artifact file
    out_path.write_text(json.dumps(artifact, indent=2), encoding='utf-8')

    # Append to continuity ledger with parent links
    entry = {
        "artifact_id": artifact.get("lineage", {}).get("artifact_hash", artifact.get("id", "unknown")),
        "parent_hashes": artifact.get("lineage", {}).get("parent_hashes", artifact.get("parent_hash", [])),
        "timestamp": artifact.get("lineage", {}).get("timestamp", artifact.get("timestamp", datetime.utcnow().isoformat() + 'Z')),
        "artifact_type": artifact.get("artifact_type", "unknown"),
        "depth": artifact.get("depth", 0)
    }
    append_ledger(entry)


def append_ledger(entry: Dict[str, Any]) -> None:
    """Append entry to continuity ledger (JSONL format).

    Args:
        entry: Entry to append to ledger
    """
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


__all__ = ['write_artifact', 'append_ledger']
