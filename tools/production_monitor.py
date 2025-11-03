#!/usr/bin/env python3
"""Production monitoring system for continuous KPI tracking."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.ledger_metrics import (
    compute_continuity_ratio,
    estimate_task_multiplication,
    measure_building_ratio,
)

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
TELEMETRY_DIR = ROOT / "telemetry"
TELEMETRY_DIR.mkdir(exist_ok=True)


class ProductionMonitor:
    """Real-time production monitoring system."""

    def __init__(self):
        self.thresholds = {
            "building_ratio_min": 0.45,
            "continuity_ratio_min": 0.70,
            "task_multiplication_min": 1.0,
            "task_multiplication_max": 6.0,
        }
        self.alert_history = []
        self.metrics_history = []

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "building_ratio": measure_building_ratio(),
            "continuity_ratio": compute_continuity_ratio(),
            "task_multiplication": estimate_task_multiplication(),
            "total_artifacts": len(list(ARTIFACTS_DIR.glob("*.json"))),
        }

    def check_thresholds(self, metrics: Dict[str, Any]) -> list:
        """Check metrics against thresholds."""
        alerts = []

        if metrics["building_ratio"] < self.thresholds["building_ratio_min"]:
            alerts.append({
                "severity": "WARNING",
                "metric": "building_ratio",
                "value": metrics["building_ratio"],
                "threshold": self.thresholds["building_ratio_min"],
            })

        if metrics["continuity_ratio"] < self.thresholds["continuity_ratio_min"]:
            alerts.append({
                "severity": "CRITICAL",
                "metric": "continuity_ratio",
                "value": metrics["continuity_ratio"],
                "threshold": self.thresholds["continuity_ratio_min"],
            })

        return alerts

    def _compute_health_score(self, metrics: Dict[str, Any]) -> float:
        """Compute system health score."""
        scores = []
        br = metrics["building_ratio"]
        scores.append(min(br / 0.55, 1.0))
        cr = metrics["continuity_ratio"]
        scores.append(min(cr / 0.9, 1.0))
        tm = metrics["task_multiplication"]
        if 1.5 <= tm <= 2.5:
            scores.append(1.0)
        elif tm < 1.5:
            scores.append(tm / 1.5)
        else:
            scores.append(max(0.0, 1.0 - (tm - 2.5) / 3.5))
        return sum(scores) / len(scores)

    def generate_snapshot(self) -> Dict[str, Any]:
        """Generate monitoring snapshot."""
        metrics = self.collect_metrics()
        alerts = self.check_thresholds(metrics)
        health_score = self._compute_health_score(metrics)

        return {
            "timestamp": metrics["timestamp"],
            "metrics": metrics,
            "alerts": alerts,
            "health_score": health_score,
            "status": "HEALTHY" if health_score >= 0.8 else "DEGRADED" if health_score >= 0.6 else "CRITICAL"
        }


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Production monitoring")
    parser.add_argument("--snapshot", action="store_true", help="Single snapshot")
    args = parser.parse_args()

    monitor = ProductionMonitor()
    snapshot = monitor.generate_snapshot()
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
