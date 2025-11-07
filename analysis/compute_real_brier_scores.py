#!/usr/bin/env python3
"""
Compute REAL Brier Scores from ACE Predictions vs Actual Outcomes

NO SIMULATION. Uses actual measured outcomes from:
- Task 1: runs/ace_task1_outcome_2025-11-07.json
- Task 2: runs/ace_task2_outcome_2025-11-07.json

Author: Claude Code (REAL EXECUTION ONLY)
Date: 2025-11-07
"""

import json
import math
from pathlib import Path

def brier_score_continuous(predicted: float, observed: float) -> float:
    """Brier score for continuous predictions"""
    return (predicted - observed) ** 2

def compute_real_brier_scores():
    """Compute Brier scores from real ACE outcomes"""

    print("=" * 70)
    print("REAL BRIER SCORE COMPUTATION")
    print("=" * 70)

    # Load real outcomes
    with open('runs/ace_task1_outcome_2025-11-07.json', 'r') as f:
        task1 = json.loads(f.read())

    with open('runs/ace_task2_outcome_2025-11-07.json', 'r') as f:
        task2 = json.loads(f.read())

    outcomes = [task1, task2]

    # Compute Brier for each metric
    metrics = ['delta_lambda', 'delta_entropy', 'delta_quality', 'delta_throughput', 'delta_reuse_ratio']

    all_scores = []

    print("\nTask-by-Task Brier Scores:\n")

    for outcome in outcomes:
        task_name = outcome['task_name']
        pred = outcome['ace_prediction']
        obs = outcome['delta_metrics']

        print(f"{task_name}:")

        task_scores = []
        for metric in metrics:
            p = pred[metric]
            o = obs[metric]
            score = brier_score_continuous(p, o)
            task_scores.append(score)
            all_scores.append(score)

            print(f"  {metric}: pred={p:.3f}, obs={o:.3f}, Brier={score:.6f}")

        task_avg = sum(task_scores) / len(task_scores)
        print(f"  → Task average: {task_avg:.6f}\n")

    # Overall Brier score
    overall_brier = sum(all_scores) / len(all_scores)

    print("=" * 70)
    print("OVERALL ACE PREDICTION ACCURACY")
    print("=" * 70)

    print(f"\nBrier Score: {overall_brier:.6f}")
    print(f"Perfect prediction: 0.000")
    print(f"Random baseline: ~0.250")

    # Victory gate
    if overall_brier < 0.05:
        status = "✓ EXCELLENT"
    elif overall_brier < 0.10:
        status = "✓ GOOD"
    elif overall_brier < 0.20:
        status = "⚠ MODERATE"
    else:
        status = "✗ POOR"

    print(f"\nStatus: {status}")

    # Honest interpretation
    print("\n" + "=" * 70)
    print("HONEST INTERPRETATION")
    print("=" * 70)

    print("\nTask 1 (Attractor prediction):")
    print("  ACE predicted small changes (δλ=0.007, δquality=0.056)")
    print("  Actual: All zeros (analysis doesn't modify code)")
    print("  → Prediction error: ACE expected side effects that didn't occur")

    print("\nTask 2 (Extract skill):")
    print("  ACE predicted improvements (δquality=0.045, δthroughput=0.072, δreuse=0.135)")
    print("  Actual: All zeros (skill already existed)")
    print("  → Prediction error: ACE proposed duplicate work")

    print("\nRoot Cause:")
    print("  ACE predictions assume tasks will be executed and create changes")
    print("  When tasks are analysis-only or already-done, predictions fail")
    print("  This validates peer review: ACE needs better context awareness")

    # Save results
    results = {
        "timestamp": "2025-11-07T04:37:00Z",
        "method": "real_measured_outcomes",
        "tasks_evaluated": 2,
        "brier_score_overall": overall_brier,
        "status": status,
        "task_scores": [
            {
                "task_id": outcome['task_id'],
                "task_name": outcome['task_name'],
                "brier_scores": {
                    metric: brier_score_continuous(outcome['ace_prediction'][metric], outcome['delta_metrics'][metric])
                    for metric in metrics
                },
                "average_brier": sum([
                    brier_score_continuous(outcome['ace_prediction'][metric], outcome['delta_metrics'][metric])
                    for metric in metrics
                ]) / len(metrics)
            }
            for outcome in outcomes
        ],
        "victory_gate": {
            "criteria": "Brier < 0.10",
            "passed": overall_brier < 0.10
        },
        "honest_assessment": "ACE predictions failed because tasks were analysis-only or duplicates. This is a real negative result showing ACE needs improvement in context awareness and deduplication."
    }

    output_path = Path("runs/ace_real_brier_scores_2025-11-07.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved: {output_path}")

    return results

if __name__ == "__main__":
    compute_real_brier_scores()
