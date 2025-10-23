#!/usr/bin/env python3
"""Unit tests for NOS calibration utilities."""
from __future__ import annotations
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / 'tools'))


import math

from nos_calibration import DEFAULT_WEIGHTS, NosSample, calibrate_weights, prepare_samples


def test_prepare_samples_returns_single_sample():
    primitives = {"energy_efficiency": 0.5, "coherence": 0.25, "resilience": 0.75, "entropy": 0.6}
    samples = prepare_samples(primitives)
    assert len(samples) == 1
    sample = samples[0]
    assert math.isclose(sample.energy_efficiency, 0.5)
    assert math.isclose(sample.coherence, 0.25)
    assert math.isclose(sample.resilience, 0.75)
    assert math.isclose(sample.entropy, 0.6)


def test_calibrate_weights_defaults_when_no_samples():
    weights = calibrate_weights([])
    assert weights == DEFAULT_WEIGHTS


def test_calibrate_weights_normalises_values():
    samples = [
        NosSample(energy_efficiency=0.9, coherence=0.3, resilience=0.2, entropy=0.5),
        NosSample(energy_efficiency=0.6, coherence=0.4, resilience=0.4, entropy=0.5),
    ]
    weights = calibrate_weights(samples)
    total = sum(weights.values())
    assert math.isclose(total, 1.0, rel_tol=1e-3)
    assert weights["energy_efficiency"] > weights["coherence"] >= 0.05
    assert weights["entropy"] >= 0.05

