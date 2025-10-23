"""Unit tests for ledger metrics helpers."""

from __future__ import annotations

import json
from pathlib import Path

from tools.ledger_metrics import measure_building_ratio


def _write_artifact(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_measure_building_ratio_recognises_design_artifacts(tmp_path: Path) -> None:
    """Artifacts describing implementation plans should count as building work."""

    _write_artifact(
        tmp_path / "artifact_build_design.json",
        {
            "artifact_type": "design_spec",
            "summary": "Design the queue balancer module",
            "files": ["docs/queue_balancer_spec.md"],
        },
    )
    _write_artifact(
        tmp_path / "artifact_build_validator.json",
        {
            "artifact_type": "report",
            "observation": "Implement validator upgrades for schema migration",
            "tags": ["validator", "plan"],
        },
    )
    _write_artifact(
        tmp_path / "artifact_analysis.json",
        {
            "artifact_type": "reflection",
            "observation": "Analyzed outcomes from prior cycle",
        },
    )

    ratio = measure_building_ratio(tmp_path)

    assert ratio == 0.667
