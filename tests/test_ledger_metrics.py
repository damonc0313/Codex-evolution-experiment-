"""Tests for ledger metric helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import ledger_metrics


def _write_artifact(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_measure_building_ratio_counts_manifest_artifacts(tmp_path: Path) -> None:
    """Artifacts describing concrete builds should be counted as building."""

    _write_artifact(
        tmp_path,
        "artifact_design.json",
        {
            "artifact_type": "design_spec",
            "summary": "Implement queue balancer pipeline",
            "files": ["docs/queue_balancer_spec.md"],
        },
    )
    _write_artifact(
        tmp_path,
        "artifact_analysis.json",
        {
            "artifact_type": "retrospective",
            "summary": "Analyzed telemetry trends",
        },
    )

    ratio = ledger_metrics.measure_building_ratio(tmp_path)
    assert ratio == pytest.approx(0.5)


def test_measure_building_ratio_detects_keyword_content(tmp_path: Path) -> None:
    """Implementation keywords in summary fields should count as building."""

    _write_artifact(
        tmp_path,
        "artifact_keywords.json",
        {
            "artifact_type": "continuity_block",
            "summary": "Refactor validator to wire schema hooks",
            "decisions": ["deploy new validator guard"],
        },
    )
    _write_artifact(
        tmp_path,
        "artifact_reflection.json",
        {
            "artifact_type": "reflection",
            "analysis": "reviewed swarm output",
        },
    )

    ratio = ledger_metrics.measure_building_ratio(tmp_path)
    assert ratio == pytest.approx(0.5)


def test_measure_building_ratio_handles_file_lists(tmp_path: Path) -> None:
    """Explicit file references indicate build activity even without keywords."""

    _write_artifact(
        tmp_path,
        "artifact_files.json",
        {
            "artifact_type": "runtime_update",
            "files": ["tools/self_query.py", "runtime/loop_policy.yaml"],
        },
    )

    ratio = ledger_metrics.measure_building_ratio(tmp_path)
    assert ratio == pytest.approx(1.0)


def test_is_building_payload_counts_swarm_metadata() -> None:
    """Swarm fork metadata with repo paths should count as building."""

    payload = {
        "artifact_type": "swarm_fork_result",
        "implementation_targets": [
            {
                "path": "tools/swarm_bench.py",
                "description": "Emit implementation metadata for downstream agents.",
            },
            {
                "path": "tests/test_ledger_metrics.py",
                "description": "Ensure coverage for swarm metadata signals.",
            },
        ],
        "modified_files": ["tools/ledger_metrics.py"],
        "next_build_steps": [
            "apply_patch <<'PATCH'\n*** Update File: tools/ledger_metrics.py\n# ... patch contents ...\nPATCH",
            "pytest tests/test_ledger_metrics.py",
        ],
    }

    assert ledger_metrics._is_building_payload(payload)
