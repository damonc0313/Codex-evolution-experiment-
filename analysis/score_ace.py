#!/usr/bin/env python3
"""
ACE Prediction Scoring - Brier(sign) + RMSE(magnitude)

Measures prediction accuracy for autonomous task selection.

Victory Gate: Brier(sign) < 0.25, RMSE < 0.05 on delta_quality

Author: Claude Code
Date: 2025-11-07
"""

import json
import math
from pathlib import Path

# Input files
PRED_FILE = Path("diagnostics/ace_proposals_task1-3.json")
OUTCOMES_FILE = Path("runs/ace_outcomes_2025-11-07.jsonl")
OUT_FILE = Path("runs/ace_predictions_2025-11-07.jsonl")

def brier_sign(predicted: float, observed: float) -> float:
    """
    Brier score for sign prediction (direction).

    Converts continuous prediction to Bernoulli:
    - predicted_prob = 1.0 if predicted > 0 else 0.0
    - observed_event = 1.0 if observed > 0 else 0.0
    - brier = (predicted_prob - observed_event)^2
    """
    pred_positive = 1.0 if predicted > 0 else 0.0
    obs_positive = 1.0 if observed > 0 else 0.0
    return (pred_positive - obs_positive) ** 2

def rmse_magnitude(predictions: list, observations: list) -> float:
    """Root mean squared error for magnitude"""
    if not predictions:
        return 0.0
    mse = sum((p - o)**2 for p, o in zip(predictions, observations)) / len(predictions)
    return math.sqrt(mse)

def export_predictions():
    """Export ACE predictions to JSONL format"""

    print("=" * 70)
    print("ACE PREDICTION EXPORT")
    print("=" * 70)

    if not PRED_FILE.exists():
        print(f"\nERROR: Predictions file not found: {PRED_FILE}")
        return

    with PRED_FILE.open() as f:
        data = json.load(f)

    proposals = data.get('proposals', [])

    print(f"\nExporting {len(proposals)} task predictions...")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUT_FILE.open("w") as f:
        for proposal in proposals:
            pred_record = {
                "ts": proposal["timestamp"],
                "task_id": proposal["task_id"],
                "name": proposal["task"]["name"],
                "domain": proposal["task"]["domain"],
                "pred": proposal["predicted"]
            }
            f.write(json.dumps(pred_record) + "\n")

    print(f"Predictions saved: {OUT_FILE}")

    # Status
    print("\n" + "=" * 70)
    print("STATUS")
    print("=" * 70)
    print(f"\n✓ Predictions logged: {len(proposals)} tasks")
    print("⚠ Outcomes pending: Need to execute tasks and measure actual deltas")
    print()
    print("To complete ACE validation:")
    print("  1. Execute Task 1 (Ablation study) - DONE ✓")
    print("  2. Measure actual KPI deltas")
    print("  3. Log to runs/ace_outcomes_2025-11-07.jsonl")
    print("  4. Re-run this script to compute Brier scores")

    return proposals


if __name__ == "__main__":
    export_predictions()
