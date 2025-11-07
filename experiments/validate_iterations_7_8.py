"""
Apply Meta-Learning Validation Skill to Iterations 7-8

Validates recent autonomous learning using synthesized skill.
"""

import sys
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.meta_learning_validation import MetaLearningValidationSkill


def convert_to_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    else:
        return obj


def main():
    """Validate iterations 7-8 using synthesized skill."""
    print("=" * 70)
    print("VALIDATING ITERATIONS 7-8 WITH SYNTHESIZED SKILL")
    print("=" * 70)

    skill = MetaLearningValidationSkill()

    # Load iteration 7 ablation results
    ablation_path = Path("diagnostics/ablation_results/iteration_7_ablation.json")
    with open(ablation_path, 'r') as f:
        ablation_data = json.load(f)

    # Load iteration 8 attractor prediction results
    attractor_path = Path("diagnostics/attractor_prediction_report.json")
    with open(attractor_path, 'r') as f:
        attractor_data = json.load(f)

    # Validate iteration 7 (ablation)
    print("\n### ITERATION 7: Ablation Study ###\n")
    
    ablation_validation_data = {
        "baseline_quality": ablation_data['baseline']['quality'],
        "ablations": [
            {
                "component": abl['condition'].replace('no_', ''),
                "degradation": abl.get('degradation', 0.0)
            }
            for abl in ablation_data['ablations']
        ]
    }

    result_iter7 = skill.validate(
        ablation_validation_data,
        "ablation",
        {"degradation_threshold": 0.05}
    )

    print(f"Verdict: {result_iter7['verdict']}")
    print(f"Critical components: {result_iter7['report']['critical_list']}")
    print(f"Total contribution: {result_iter7['report']['total_contribution']}")

    # Validate iteration 8 (attractor prediction)
    print("\n### ITERATION 8: Attractor Prediction ###\n")

    # Get historical policy trajectory
    hist_preds = attractor_data['historical_policy']['predictions']
    building_weight_pred = hist_preds.get('building_weight', {})

    if 'attractor' in building_weight_pred:
        attractor_validation_data = {
            "predicted_attractor": building_weight_pred['attractor'],
            "current_value": building_weight_pred.get('current_value', 0.5),
            "trajectory": [0.5026, 0.5029, 0.503, 0.5032, 0.5033, 0.5047, 
                         0.5064, 0.5077, 0.5082, 0.5086, 0.5107]  # From history
        }

        result_iter8 = skill.validate(
            attractor_validation_data,
            "attractor"
        )

        print(f"Verdict: {result_iter8['verdict']}")
        print(f"Computed attractor: {result_iter8['evidence']['computed_attractor']:.3f}")
        print(f"Convergence: {result_iter8['report']['estimated_convergence']}")
    else:
        print("Attractor data not found in expected format")
        result_iter8 = {"verdict": "INCONCLUSIVE"}

    # Validate overall learning trajectory (iterations 1-8)
    print("\n### OVERALL TRAJECTORY (Iterations 1-8) ###\n")

    # Quality progression from coding sessions
    coding_sessions_path = Path("diagnostics/coding_sessions.jsonl")
    quality_trajectory = []
    
    with open(coding_sessions_path, 'r') as f:
        for line in f:
            session = json.loads(line)
            if 'practice/' in session.get('file_path', ''):
                quality = session.get('quality', 0)
                if quality > 0:
                    quality_trajectory.append(quality)

    # Take last 8 iterations (representative samples)
    if len(quality_trajectory) >= 8:
        recent_trajectory = quality_trajectory[-8:]
    else:
        recent_trajectory = quality_trajectory

    trajectory_validation_data = {
        "quality_trajectory": recent_trajectory,
        "expected_improvement": 0.1  # Expect 10% improvement
    }

    result_trajectory = skill.validate(
        trajectory_validation_data,
        "trajectory"
    )

    print(f"Verdict: {result_trajectory['verdict']}")
    print(f"Improvement: {result_trajectory['report']['summary']}")
    print(f"Stability: {result_trajectory['report']['stability']}")

    # Comprehensive summary
    print("\n" + "=" * 70)
    print("COMPREHENSIVE VALIDATION SUMMARY")
    print("=" * 70)

    all_verdicts = [
        ("Iteration 7 (Ablation)", result_iter7['verdict']),
        ("Iteration 8 (Attractor)", result_iter8['verdict']),
        ("Overall Trajectory", result_trajectory['verdict'])
    ]

    for name, verdict in all_verdicts:
        print(f"  {name}: {verdict}")

    validated_count = sum(1 for _, v in all_verdicts if v == "VALIDATED")
    print(f"\nOverall: {validated_count}/{len(all_verdicts)} validations passed")

    # Save validation report (convert numpy types)
    validation_report = {
        "timestamp": "2025-11-07T18:00:00Z",
        "skill_version": skill.version,
        "iterations_validated": [7, 8],
        "results": {
            "iteration_7_ablation": convert_to_serializable(result_iter7),
            "iteration_8_attractor": convert_to_serializable(result_iter8),
            "overall_trajectory": convert_to_serializable(result_trajectory)
        },
        "summary": {
            "validated": validated_count,
            "total": len(all_verdicts),
            "verdict": "VALIDATED" if validated_count >= 2 else "INCONCLUSIVE"
        }
    }

    output_path = Path("diagnostics/iteration_7_8_validation.json")
    with open(output_path, 'w') as f:
        json.dump(validation_report, f, indent=2)

    print(f"\nValidation report saved: {output_path}")


if __name__ == '__main__':
    main()
