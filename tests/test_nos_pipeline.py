import json

import pytest

yaml = pytest.importorskip("yaml")

from tools import nos_pipeline


def _stub_swarm(*, dry_run: bool = False):
    return {
        "run_id": "TEST",
        "gated": False,
        "gate_metrics": {
            "avg_regression_pass_rate": 0.91,
            "avg_continuity_ratio": 0.93,
            "avg_building_ratio": 0.62,
            "avg_queue_depth": 6.4,
            "avg_nos_score": 0.12,
        },
        "summary": {
            "gate_metrics": {
                "avg_regression_pass_rate": 0.91,
                "avg_continuity_ratio": 0.93,
                "avg_building_ratio": 0.62,
                "avg_queue_depth": 6.4,
                "avg_nos_score": 0.12,
            }
        },
    }


def test_pipeline_creates_config_and_artifacts(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "artifacts").mkdir(parents=True)
    (root / "runtime").mkdir()
    (root / "docs").mkdir()
    data_dir = root / "data" / "evo"
    data_dir.mkdir(parents=True)
    (data_dir / "evo_rates.csv").write_text("mutation_rate,selection_gradient\n0.4,0.3\n", encoding="utf-8")
    (data_dir / "pop_dyn.json").write_text(
        json.dumps([
            {"birth_rate": 0.7, "death_rate": 0.5, "carrying_capacity": 1000}
        ]),
        encoding="utf-8",
    )
    monkeypatch.setattr(nos_pipeline, "ROOT", root)
    monkeypatch.setattr(nos_pipeline, "run_swarm", _stub_swarm)

    pipeline = nos_pipeline.NosRealDataPipeline(root, dry_run=False)
    summary = pipeline.run()

    assert summary.gated is False
    assert summary.delta_nos >= 0.12

    config_path = root / "runtime" / "nos_sources.yaml"
    assert config_path.exists()
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert any(src["id"] == "evo_rates_01" for src in cfg["sources"])

    calibration_artifact = root / "artifacts" / "nos_calibration.json"
    assert calibration_artifact.exists()
    calibration = json.loads(calibration_artifact.read_text(encoding="utf-8"))
    assert calibration["weights"]["energy_efficiency"] > 0

    nos_doc = root / "docs" / "NATURAL_OPTIMISATION_SIGNATURE.md"
    assert "digest:" in nos_doc.read_text(encoding="utf-8")

    ledger_artifact = root / "artifacts" / "ledger_entry_nos_realdata.json"
    ledger = json.loads(ledger_artifact.read_text(encoding="utf-8"))
    assert ledger["delta_nos"] >= 0.12

    query_text = (root / "runtime" / "user_query.txt").read_text(encoding="utf-8")
    assert "memetic local-refactor" in query_text
