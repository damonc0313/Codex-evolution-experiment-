"""Simple additive BiasCorrector used in Gap 1.5 calibration checks.

The method assumes a stable, directionally consistent calibration bias
between predicted probabilities and empirical outcomes. It estimates a
single scalar bias on a calibration set and subtracts it from future
predictions, clipping to the probability simplex.
"""
from __future__ import annotations

from typing import Iterable, List


class BiasCorrector:
    """Estimate and remove a constant calibration bias.

    This implementation mirrors the Gap 1.5 assumption of a directionally
    stable bias: predicted probabilities deviate from true frequencies by a
    roughly constant additive term. The corrector estimates that offset on
    a calibration set and subtracts it from subsequent predictions.
    """

    def __init__(self, clip_eps: float = 1e-6) -> None:
        self.clip_eps = clip_eps
        self.bias: float | None = None

    def fit(self, predicted: Iterable[float], labels: Iterable[int]) -> float:
        """Estimate the bias as mean(predicted - observed_labels).

        Args:
            predicted: Model confidence scores in [0, 1].
            labels: Binary outcomes (0 or 1).

        Returns:
            The estimated bias term.
        """

        predicted_list = list(predicted)
        labels_list = list(labels)
        if len(predicted_list) != len(labels_list):
            raise ValueError("Predicted and label lengths must match")

        self.bias = sum(p - y for p, y in zip(predicted_list, labels_list)) / len(
            predicted_list
        )
        return self.bias

    def correct(self, predicted: Iterable[float]) -> List[float]:
        """Apply the learned bias correction.

        Raises:
            ValueError: if fit has not been called yet.
        """

        if self.bias is None:
            raise ValueError("BiasCorrector.fit must be called before correct")

        corrected: List[float] = []
        for p in predicted:
            adjusted = p - self.bias
            bounded = min(max(adjusted, self.clip_eps), 1.0 - self.clip_eps)
            corrected.append(bounded)
        return corrected
