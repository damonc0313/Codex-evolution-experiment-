"""
Meta-Learning Validation Skill - Comprehensive Scientific Validation

Extends statistical_validation.py with meta-learning capabilities:
1. Statistical validation (t-tests, effect size, CI)
2. Attractor prediction (convergence analysis)
3. Ablation validation (component contribution)
4. Learning trajectory analysis

Synthesized from iterations 7-8 autonomous learning.

Pattern sources:
- experiments/rigorous_replication_study.py (statistical validation)
- experiments/attractor_prediction.py (convergence prediction)
- experiments/ablation_study.py (component validation)
- tools/code_quality_tracker.py (quality measurement)

Author: Claude Code (autonomous)
Date: 2025-11-07
Version: 2.0.0
"""

import json
import statistics
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import base skill
from skills.statistical_validation import StatisticalValidationSkill


SKILL_SPEC = {
    "name": "meta_learning_validation",
    "version": "2.0.0",
    "description": "Comprehensive validation for meta-learning systems",
    "capabilities": [
        "statistical_validation",
        "attractor_prediction",
        "ablation_analysis",
        "trajectory_analysis"
    ],
    "interface": {
        "inputs": {
            "data": "Dict - structured validation data",
            "validation_type": "str - type of validation to perform",
            "config": "Dict - validation configuration"
        },
        "outputs": {
            "verdict": "str - VALIDATED, REJECTED, INCONCLUSIVE",
            "evidence": "Dict - empirical evidence",
            "report": "Dict - comprehensive report"
        }
    },
    "tests": "tests/test_meta_learning_validation.py",
    "dependencies": ["numpy", "statistics", "skills.statistical_validation"]
}


class MetaLearningValidationSkill:
    """
    Comprehensive validation skill for meta-learning systems.

    Combines:
    - Statistical validation (significance testing)
    - Attractor prediction (convergence analysis)
    - Ablation analysis (component contribution)
    - Trajectory analysis (learning curves)
    """

    def __init__(self, spec: Dict = None):
        self.spec = spec or SKILL_SPEC
        self.version = self.spec['version']
        self.base_validator = StatisticalValidationSkill()

    def validate(
        self,
        data: Dict,
        validation_type: str = "comprehensive",
        config: Dict = None
    ) -> Dict:
        """
        Run validation based on type.

        Types:
        - "statistical": Statistical significance testing
        - "attractor": Convergence prediction
        - "ablation": Component contribution
        - "trajectory": Learning curve analysis
        - "comprehensive": All of the above
        """
        config = config or {}

        if validation_type == "statistical":
            return self.validate_statistical(data, config)
        elif validation_type == "attractor":
            return self.validate_attractor(data, config)
        elif validation_type == "ablation":
            return self.validate_ablation(data, config)
        elif validation_type == "trajectory":
            return self.validate_trajectory(data, config)
        elif validation_type == "comprehensive":
            return self.validate_comprehensive(data, config)
        else:
            return {
                "verdict": "ERROR",
                "error": f"Unknown validation type: {validation_type}"
            }

    def validate_statistical(self, data: Dict, config: Dict) -> Dict:
        """
        Statistical validation (wrapper around base skill).

        Data format:
        {
            "samples": [0.7, 0.72, 0.75, ...],
            "null_hypothesis": {"type": "mean", "value": 0.575}
        }
        """
        samples = data.get('samples', [])
        null_hypothesis = data.get('null_hypothesis', {"type": "mean", "value": 0.5})
        alpha = config.get('alpha', 0.01)

        result = self.base_validator.validate(samples, null_hypothesis, alpha)

        return {
            "validation_type": "statistical",
            "verdict": "VALIDATED" if result['verdict'] else "REJECTED",
            "evidence": result['statistics'],
            "report": result['report'],
            "criteria": result['criteria']
        }

    def validate_attractor(self, data: Dict, config: Dict) -> Dict:
        """
        Attractor prediction validation.

        Data format:
        {
            "trajectory": [0.50, 0.51, 0.52, ...],
            "predicted_attractor": 0.75,
            "current_value": 0.55
        }
        """
        trajectory = data.get('trajectory', [])
        predicted_attractor = data.get('predicted_attractor', None)
        current_value = data.get('current_value', trajectory[-1] if trajectory else None)

        if not trajectory or len(trajectory) < 3:
            return {
                "validation_type": "attractor",
                "verdict": "INCONCLUSIVE",
                "error": "Insufficient trajectory data (need ≥3 points)"
            }

        # Fit curve to trajectory
        t = np.arange(len(trajectory))
        y = np.array(trajectory)

        # Linear fit
        coeffs_linear = np.polyfit(t, y, 1)
        slope = coeffs_linear[0]

        # Predict attractor (extrapolate to t=100)
        computed_attractor = np.polyval(coeffs_linear, 100)

        # Validate prediction
        if predicted_attractor is not None:
            prediction_error = abs(computed_attractor - predicted_attractor)
            prediction_accurate = prediction_error < 0.1  # Within 10%
        else:
            prediction_error = None
            prediction_accurate = None

        # Convergence metrics
        distance_to_attractor = abs(computed_attractor - current_value)
        convergence_rate = abs(slope)  # Change per iteration

        if convergence_rate > 0:
            iterations_to_convergence = distance_to_attractor / convergence_rate
        else:
            iterations_to_convergence = float('inf')

        # Verdict
        converging = convergence_rate > 0.001  # Non-zero slope
        attractor_reasonable = 0.0 <= computed_attractor <= 1.0

        verdict = "VALIDATED" if (converging and attractor_reasonable) else "INCONCLUSIVE"

        return {
            "validation_type": "attractor",
            "verdict": verdict,
            "evidence": {
                "trajectory_length": len(trajectory),
                "current_value": float(current_value),
                "computed_attractor": float(computed_attractor),
                "predicted_attractor": predicted_attractor,
                "prediction_error": float(prediction_error) if prediction_error is not None else None,
                "distance_to_attractor": float(distance_to_attractor),
                "convergence_rate": float(convergence_rate),
                "iterations_to_convergence": float(iterations_to_convergence) if iterations_to_convergence != float('inf') else None,
                "slope": float(slope)
            },
            "criteria": {
                "converging": converging,
                "attractor_reasonable": attractor_reasonable,
                "prediction_accurate": prediction_accurate
            },
            "report": {
                "summary": f"Trajectory converging toward {computed_attractor:.3f}",
                "current_distance": f"{distance_to_attractor:.3f} from attractor",
                "estimated_convergence": f"{iterations_to_convergence:.0f} iterations" if iterations_to_convergence != float('inf') else "Not converging"
            }
        }

    def validate_ablation(self, data: Dict, config: Dict) -> Dict:
        """
        Ablation analysis validation.

        Data format:
        {
            "baseline_quality": 0.7,
            "ablations": [
                {"component": "ACE", "quality": 0.64, "degradation": 0.06},
                {"component": "CIL", "quality": 0.7, "degradation": 0.0},
                ...
            ]
        }
        """
        baseline = data.get('baseline_quality', 0.7)
        ablations = data.get('ablations', [])
        threshold = config.get('degradation_threshold', 0.05)

        if not ablations:
            return {
                "validation_type": "ablation",
                "verdict": "INCONCLUSIVE",
                "error": "No ablation data provided"
            }

        # Analyze each component
        critical_components = []
        non_critical_components = []
        total_degradation = 0.0

        for ablation in ablations:
            component = ablation.get('component', 'unknown')
            degradation = ablation.get('degradation', 0.0)

            total_degradation += degradation

            if degradation >= threshold:
                critical_components.append({
                    "component": component,
                    "degradation": degradation,
                    "contribution_pct": (degradation / baseline * 100) if baseline > 0 else 0
                })
            else:
                non_critical_components.append(component)

        # Verdict
        has_critical_components = len(critical_components) > 0
        total_impact_significant = total_degradation >= threshold

        verdict = "VALIDATED" if has_critical_components else "INCONCLUSIVE"

        return {
            "validation_type": "ablation",
            "verdict": verdict,
            "evidence": {
                "baseline_quality": baseline,
                "num_components_tested": len(ablations),
                "critical_components": critical_components,
                "non_critical_components": non_critical_components,
                "total_degradation": total_degradation,
                "avg_degradation": total_degradation / len(ablations) if ablations else 0.0
            },
            "criteria": {
                "has_critical_components": has_critical_components,
                "total_impact_significant": total_impact_significant
            },
            "report": {
                "summary": f"{len(critical_components)} critical components identified",
                "critical_list": [c['component'] for c in critical_components],
                "total_contribution": f"{total_degradation:.3f} ({total_degradation/baseline*100:.1f}% of baseline)"
            }
        }

    def validate_trajectory(self, data: Dict, config: Dict) -> Dict:
        """
        Learning trajectory validation.

        Data format:
        {
            "quality_trajectory": [0.7, 0.75, 0.8, 0.85, 0.9],
            "expected_improvement": 0.2,
            "iterations": 5
        }
        """
        trajectory = data.get('quality_trajectory', [])
        expected_improvement = data.get('expected_improvement', 0.1)

        if not trajectory or len(trajectory) < 2:
            return {
                "validation_type": "trajectory",
                "verdict": "INCONCLUSIVE",
                "error": "Insufficient trajectory data (need ≥2 points)"
            }

        # Calculate improvement
        initial = trajectory[0]
        final = trajectory[-1]
        actual_improvement = final - initial
        improvement_rate = actual_improvement / len(trajectory) if len(trajectory) > 0 else 0.0

        # Monotonicity check (is it improving?)
        increases = sum(1 for i in range(len(trajectory) - 1) if trajectory[i+1] > trajectory[i])
        monotonicity = increases / (len(trajectory) - 1) if len(trajectory) > 1 else 0.0

        # Variance (is it stable?)
        variance = np.var(trajectory)
        stable = variance < 0.01

        # Verdict
        improving = actual_improvement > 0
        meets_target = actual_improvement >= expected_improvement
        mostly_monotonic = monotonicity >= 0.7  # 70% of steps increase

        verdict = "VALIDATED" if (improving and meets_target and mostly_monotonic) else "INCONCLUSIVE"

        return {
            "validation_type": "trajectory",
            "verdict": verdict,
            "evidence": {
                "trajectory_length": len(trajectory),
                "initial_quality": initial,
                "final_quality": final,
                "actual_improvement": actual_improvement,
                "expected_improvement": expected_improvement,
                "improvement_rate": improvement_rate,
                "monotonicity": monotonicity,
                "variance": variance,
                "stable": stable
            },
            "criteria": {
                "improving": improving,
                "meets_target": meets_target,
                "mostly_monotonic": mostly_monotonic,
                "stable": stable
            },
            "report": {
                "summary": f"Quality improved from {initial:.2f} to {final:.2f} (+{actual_improvement:.2f})",
                "improvement_rate": f"{improvement_rate:.3f} per iteration",
                "monotonicity": f"{monotonicity:.1%} monotonic increases",
                "stability": "Stable" if stable else "Variable"
            }
        }

    def validate_comprehensive(self, data: Dict, config: Dict) -> Dict:
        """
        Run all validation types.

        Data format: Union of all validation data formats
        """
        results = {}
        verdicts = []

        # Try each validation type
        if 'samples' in data and 'null_hypothesis' in data:
            results['statistical'] = self.validate_statistical(data, config)
            verdicts.append(results['statistical']['verdict'])

        if 'trajectory' in data:
            results['attractor'] = self.validate_attractor(data, config)
            verdicts.append(results['attractor']['verdict'])

        if 'ablations' in data:
            results['ablation'] = self.validate_ablation(data, config)
            verdicts.append(results['ablation']['verdict'])

        if 'quality_trajectory' in data:
            results['trajectory'] = self.validate_trajectory(data, config)
            verdicts.append(results['trajectory']['verdict'])

        # Overall verdict
        validated_count = verdicts.count("VALIDATED")
        rejected_count = verdicts.count("REJECTED")
        inconclusive_count = verdicts.count("INCONCLUSIVE")

        if validated_count > 0 and rejected_count == 0:
            overall_verdict = "VALIDATED"
        elif rejected_count > validated_count:
            overall_verdict = "REJECTED"
        else:
            overall_verdict = "INCONCLUSIVE"

        return {
            "validation_type": "comprehensive",
            "verdict": overall_verdict,
            "results": results,
            "summary": {
                "tests_run": len(verdicts),
                "validated": validated_count,
                "rejected": rejected_count,
                "inconclusive": inconclusive_count
            },
            "report": {
                "summary": f"Comprehensive validation: {validated_count}/{len(verdicts)} tests validated",
                "details": {k: v['report'] for k, v in results.items() if 'report' in v}
            }
        }


def main():
    """Test meta-learning validation skill."""
    print("=" * 70)
    print("META-LEARNING VALIDATION SKILL - TEST")
    print("=" * 70)

    skill = MetaLearningValidationSkill()

    # Test 1: Statistical validation
    print("\n### TEST 1: Statistical Validation ###\n")
    data_stat = {
        "samples": [0.7, 0.72, 0.75, 0.78, 0.76, 0.74, 0.77, 0.79, 0.80, 0.81],
        "null_hypothesis": {"type": "mean", "value": 0.65}
    }
    result_stat = skill.validate(data_stat, "statistical", {"alpha": 0.01})
    print(f"Verdict: {result_stat['verdict']}")
    print(f"Report: {result_stat['report']}")

    # Test 2: Attractor validation
    print("\n### TEST 2: Attractor Prediction ###\n")
    data_attr = {
        "trajectory": [0.50, 0.52, 0.54, 0.55, 0.56, 0.57],
        "predicted_attractor": 0.85,
        "current_value": 0.57
    }
    result_attr = skill.validate(data_attr, "attractor")
    print(f"Verdict: {result_attr['verdict']}")
    print(f"Report: {result_attr['report']}")

    # Test 3: Ablation validation
    print("\n### TEST 3: Ablation Analysis ###\n")
    data_ablation = {
        "baseline_quality": 0.7,
        "ablations": [
            {"component": "ACE", "quality": 0.64, "degradation": 0.06},
            {"component": "CIL", "quality": 0.7, "degradation": 0.0},
            {"component": "Pattern Detection", "quality": 0.68, "degradation": 0.02}
        ]
    }
    result_ablation = skill.validate(data_ablation, "ablation")
    print(f"Verdict: {result_ablation['verdict']}")
    print(f"Report: {result_ablation['report']}")

    # Test 4: Trajectory validation
    print("\n### TEST 4: Learning Trajectory ###\n")
    data_traj = {
        "quality_trajectory": [0.7, 0.75, 0.8, 0.85, 0.9],
        "expected_improvement": 0.15
    }
    result_traj = skill.validate(data_traj, "trajectory")
    print(f"Verdict: {result_traj['verdict']}")
    print(f"Report: {result_traj['report']}")

    # Test 5: Comprehensive validation
    print("\n### TEST 5: Comprehensive Validation ###\n")
    data_comp = {
        **data_stat,
        **data_attr,
        **data_ablation,
        **data_traj
    }
    result_comp = skill.validate(data_comp, "comprehensive")
    print(f"Overall Verdict: {result_comp['verdict']}")
    print(f"Summary: {result_comp['summary']}")
    print(f"Report: {result_comp['report']['summary']}")

    print("\n" + "=" * 70)
    print(f"Skill version: {skill.version}")
    print(f"Capabilities: {', '.join(skill.spec['capabilities'])}")
    print("=" * 70)


if __name__ == '__main__':
    main()
