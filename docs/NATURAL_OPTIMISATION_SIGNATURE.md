---
artifact_type: heuristic_spec
title: Natural Optimisation Signature
digest: 92cda50229323c46
sources:
  - runtime/nos_sources.yaml
  - tools/nos_data_sources.py
  - tools/nos_calibration.py
---

# Natural Optimisation Signature

The Natural Optimisation Signature (NOS) blends Kael KPIs with principles
drawn from real-world evolutionary systems.  Each component is sourced
from ingestible datasets and normalised before weights are applied.

## Components
- **Energy efficiency** → mutation rate / selection gradient proxies.
- **Coherence** → fitness landscape peaks reinforcing lineage structure.
- **Resilience** → population dynamic stability and carrying capacity.
- **Entropy** → exploration diversity derived from landscape ruggedness.

## Current Weights
- **energy_efficiency**: 0.250
- **coherence**: 0.250
- **resilience**: 0.250
- **entropy**: 0.250

## Latest Primitives
- **energy_efficiency**: 0.000
- **coherence**: 0.000
- **resilience**: 0.000
- **entropy**: 0.000

## Formula
```text
nos_score = ((w_e × energy_efficiency) × (w_c × coherence) × (w_r × resilience)) / (w_h × entropy)
```

## Operational Guidance
1. Persist `runtime/nos_sources.yaml` alongside dataset digests.
2. When new datasets land, re-run the ingestion + calibration helper.
3. Promote validator soft checks to hard failures once telemetry stabilises.
