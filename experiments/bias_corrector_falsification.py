"""Falsification experiment for Gap 1.5 BiasCorrector under drift inversion."""
from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.bias_corrector import BiasCorrector


@dataclass
class DatasetConfig:
    n_samples: int
    drift: float
    seed: int


@dataclass
class CalibrationMetrics:
    pre_ece: float
    post_ece: float

    @property
    def delta(self) -> float:
        return self.post_ece - self.pre_ece


@dataclass
class ExperimentResult:
    hypothesis: str
    calibration_source: DatasetConfig
    evaluation_overconfident: CalibrationMetrics
    evaluation_underconfident: CalibrationMetrics
    estimated_bias: float
    outcome: str
    notes: str

    def to_json(self) -> str:
        payload = {
            "hypothesis": self.hypothesis,
            "calibration_source": asdict(self.calibration_source),
            "estimated_bias": self.estimated_bias,
            "metrics": {
                "overconfident": {
                    "pre_ece": self.evaluation_overconfident.pre_ece,
                    "post_ece": self.evaluation_overconfident.post_ece,
                    "delta": self.evaluation_overconfident.delta,
                },
                "underconfident": {
                    "pre_ece": self.evaluation_underconfident.pre_ece,
                    "post_ece": self.evaluation_underconfident.post_ece,
                    "delta": self.evaluation_underconfident.delta,
                },
            },
            "outcome": self.outcome,
            "notes": self.notes,
            "steps": [
                "Generate base probabilities from a logistic link on Gaussian inputs",
                "Induce additive calibration drift in positive and negative directions",
                "Fit BiasCorrector on overconfident (+drift) calibration set",
                "Apply the same correction to overconfident and underconfident evaluation sets",
                "Compute pre/post Expected Calibration Error (ECE) and assess drift inversion robustness",
            ],
        }
        return json.dumps(payload, indent=2)


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def expected_calibration_error(probs: List[float], labels: List[int], n_bins: int = 10) -> float:
    bin_totals = [0 for _ in range(n_bins)]
    bin_correct = [0 for _ in range(n_bins)]
    bin_conf_sum = [0.0 for _ in range(n_bins)]

    for p, y in zip(probs, labels):
        bin_idx = min(int(p * n_bins), n_bins - 1)
        bin_totals[bin_idx] += 1
        bin_correct[bin_idx] += y
        bin_conf_sum[bin_idx] += p

    total_count = len(probs)
    ece = 0.0
    for total, correct, conf_sum in zip(bin_totals, bin_correct, bin_conf_sum):
        if total == 0:
            continue
        accuracy = correct / total
        confidence = conf_sum / total
        ece += abs(accuracy - confidence) * (total / total_count)
    return ece


def generate_dataset(config: DatasetConfig) -> Tuple[List[float], List[int], List[float]]:
    rng = random.Random(config.seed)
    logits = [rng.gauss(0, 1) for _ in range(config.n_samples)]
    true_probs = [sigmoid(logit) for logit in logits]
    labels = [1 if rng.random() < p else 0 for p in true_probs]

    drifted_probs = [
        min(max(p + config.drift, 1e-6), 1.0 - 1e-6)
        for p in true_probs
    ]
    return true_probs, labels, drifted_probs


def run_experiment() -> ExperimentResult:
    hypothesis = (
        "A BiasCorrector calibrated on overconfident (+0.15) drift will fail when "
        "applied to underconfident (-0.15) drift, increasing ECE under inversion."
    )

    calib_config = DatasetConfig(n_samples=2000, drift=0.15, seed=42)
    eval_under_config = DatasetConfig(n_samples=2000, drift=-0.15, seed=84)

    _, labels_cal, overconfident_probs = generate_dataset(calib_config)
    _, labels_under, underconfident_probs = generate_dataset(eval_under_config)

    bias_corrector = BiasCorrector()
    estimated_bias = bias_corrector.fit(overconfident_probs, labels_cal)

    corrected_over = bias_corrector.correct(overconfident_probs)
    corrected_under = bias_corrector.correct(underconfident_probs)

    over_pre_ece = expected_calibration_error(overconfident_probs, labels_cal)
    over_post_ece = expected_calibration_error(corrected_over, labels_cal)

    under_pre_ece = expected_calibration_error(underconfident_probs, labels_under)
    under_post_ece = expected_calibration_error(corrected_under, labels_under)

    over_metrics = CalibrationMetrics(pre_ece=over_pre_ece, post_ece=over_post_ece)
    under_metrics = CalibrationMetrics(pre_ece=under_pre_ece, post_ece=under_post_ece)

    if under_metrics.post_ece > under_metrics.pre_ece:
        outcome = "FAILS under drift inversion"
        notes = (
            "Correction learned on +0.15 drift overcompensated when drift flipped "
            "negative, worsening calibration."
        )
    else:
        outcome = "HOLDS under drift inversion"
        notes = "BiasCorrector generalized despite drift sign change."

    return ExperimentResult(
        hypothesis=hypothesis,
        calibration_source=calib_config,
        evaluation_overconfident=over_metrics,
        evaluation_underconfident=under_metrics,
        estimated_bias=estimated_bias,
        outcome=outcome,
        notes=notes,
    )


def main() -> None:
    result = run_experiment()
    output_path = Path("runs/bias_corrector_gap15_falsification.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.to_json())
    print(result.to_json())
    print(f"\nSaved log to {output_path}")


if __name__ == "__main__":
    main()
