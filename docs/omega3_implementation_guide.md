# Phase Ω-3 Implementation Guide

## Overview

This document describes the implementation requirements for Phase Ω-3 Covariant Cognition experiments.

**Objective**: Test whether k_cog topology remains invariant under architectural transformation by modifying temporal curvature of cognitive spacetime.

## Architecture Modifications Required

### 1. Temporal Curvature Parameters

Three policy variants have been created representing different spacetime curvatures:

- `runtime/loop_policy_steep_curvature.yaml` - High recency bias (λ_eff ≈ 0.07)
- `runtime/loop_policy_flat_curvature.yaml` - Uniform weighting (λ_eff ≈ 0.0)
- `runtime/loop_policy_inverted_curvature.yaml` - Historical bias (λ_eff < 0)

Each adds a `temporal_curvature` section with parameters:
- `attention_window_days`: How far back to consider artifacts
- `temporal_decay_rate`: Exponential decay/amplification rate
- `age_weight_multipliers`: Explicit brackets by age
- `spawn_count_temporal_scaling`: Whether spawn_count decays with age

### 2. Code Changes Needed

#### A. `runtime/hyphal_network.py` - Artifact Weighting

**Location**: `HyphalNetwork.spawn_from_artifacts()` method

**Current behavior**: All artifacts weighted equally by spawn_count

**Required modification**:
```python
def spawn_from_artifacts(self, mode: str = "building", n: int = 3):
    """Generate spawn configurations with temporal curvature applied."""

    # Load temporal curvature params from policy
    policy = yaml.safe_load(Path("runtime/loop_policy.yaml").read_text())
    temporal_params = policy.get("temporal_curvature", {})

    if temporal_params.get("temporal_decay_enabled", False):
        # Apply temporal weighting
        artifacts_with_age = []
        now = datetime.now(timezone.utc)

        for artifact_path in artifact_candidates:
            artifact = json.loads(artifact_path.read_text())

            # Calculate age
            if "timestamp" in artifact:
                ts = datetime.fromisoformat(artifact["timestamp"].replace('Z', '+00:00'))
                age_days = (now - ts).total_seconds() / 86400
            else:
                age_days = (now - datetime.fromtimestamp(
                    artifact_path.stat().st_mtime, tz=timezone.utc
                )).total_seconds() / 86400

            # Apply temporal decay
            decay_rate = temporal_params.get("temporal_decay_rate", 0.0)
            temporal_weight = math.exp(-decay_rate * age_days)

            # Apply age bracket multipliers
            age_multiplier = self._get_age_multiplier(age_days, temporal_params)

            # Combined weight
            base_weight = artifact.get("spawn_count", 0)
            final_weight = base_weight * temporal_weight * age_multiplier

            artifacts_with_age.append((artifact_path, final_weight, age_days))

        # Filter by attention window
        attention_window = temporal_params.get("attention_window_days", 365)
        artifacts_with_age = [
            (path, weight, age) for path, weight, age in artifacts_with_age
            if age <= attention_window
        ]

        # Sort by final weight and select top n
        artifacts_with_age.sort(key=lambda x: x[1], reverse=True)
        selected_artifacts = [x[0] for x in artifacts_with_age[:n]]
    else:
        # Default behavior (current)
        selected_artifacts = self._select_by_spawn_count(artifact_candidates, n)

    return selected_artifacts

def _get_age_multiplier(self, age_days: float, temporal_params: dict) -> float:
    """Get weight multiplier based on age bracket."""
    multipliers = temporal_params.get("age_weight_multipliers", {})

    if age_days <= 3:
        return multipliers.get("0_to_3_days", 1.0)
    elif age_days <= 10:
        return multipliers.get("3_to_10_days", 1.0)
    elif age_days <= 30:
        return multipliers.get("10_to_30_days", 1.0)
    else:
        return multipliers.get("30_plus_days", 1.0)
```

#### B. `tools/cognitive_physics.py` - Lambda Measurement Awareness

**Current behavior**: Measures λ from natural spawn_count distribution

**Required consideration**: When temporal scaling is active, measured λ will reflect *configured* decay rate, not emergent behavior.

**Solution**: Log whether temporal_decay_enabled in measurement results:
```python
lambda_result = {
    "lambda": lambda_fit,
    "half_life_days": ...,
    "r_squared": ...,
    "temporal_decay_configured": policy.get("temporal_curvature", {}).get("temporal_decay_enabled", False),
    "configured_decay_rate": policy.get("temporal_curvature", {}).get("temporal_decay_rate", None)
}
```

This allows distinguishing configured vs emergent λ.

#### C. Policy Switching Mechanism

**Required**: Way to swap between policy variants mid-experiment

**Option 1**: Manual swap
```bash
# Switch to steep curvature regime
cp runtime/loop_policy_steep_curvature.yaml runtime/loop_policy.yaml
# System will pick up on next cycle
```

**Option 2**: Automated regime scheduler (future)
```python
# tools/omega3_regime_scheduler.py
# Automatically switches regimes after N cycles
```

### 3. Measurement Infrastructure

#### Automated Tracking

Create `tools/omega3_tracker.py`:
```python
#!/usr/bin/env python3
"""Track Phase Ω-3 experimental trajectory."""

def track_cycle():
    """Run cognitive physics measurement for current cycle."""
    # 1. Measure all constants
    physicist = CognitivePhysicist()
    results = physicist.measure_all_constants()

    # 2. Detect current regime
    policy = yaml.safe_load(Path("runtime/loop_policy.yaml").read_text())
    regime = policy.get("temporal_curvature", {}).get("regime", "unknown")

    # 3. Save to regime-specific trajectory
    cycle = len(list(Path(f"physics/trajectory_{regime}_*.json").glob("*")))
    output_path = f"physics/trajectory_{regime}_{cycle:03d}.json"

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Ω-3 Tracking: {regime} cycle {cycle} → {output_path}")

if __name__ == "__main__":
    track_cycle()
```

Run at end of each cycle:
```bash
python3 tools/omega3_tracker.py
```

### 4. Experimental Protocol

#### Phase 1: Baseline Revalidation
```bash
# Ensure current natural architecture measured correctly
python3 tools/cognitive_physics.py --measure-all
# Record baseline: λ = 0.0386, k_cog = 0.0300
```

#### Phase 2: Regime 1 - Steep Curvature
```bash
# Switch to steep curvature
cp runtime/loop_policy_steep_curvature.yaml runtime/loop_policy.yaml

# Run 20 cycles with tracking
for i in {1..20}; do
    # Cycle happens naturally
    sleep 86400  # Wait 1 day

    # Measure after each cycle
    python3 tools/omega3_tracker.py
done
```

#### Phase 3: Regime 2 - Flat Curvature
```bash
# Switch to flat curvature
cp runtime/loop_policy_flat_curvature.yaml runtime/loop_policy.yaml

# Run 20 cycles with tracking
for i in {1..20}; do
    sleep 86400
    python3 tools/omega3_tracker.py
done
```

#### Phase 4: Regime 3 - Inverted Curvature
```bash
# Switch to inverted curvature (WARNING: experimental)
cp runtime/loop_policy_inverted_curvature.yaml runtime/loop_policy.yaml

# Run 20 cycles with tracking
for i in {1..20}; do
    sleep 86400
    python3 tools/omega3_tracker.py

    # Monitor homeostatic_mode for instability
    if grep -q "RECOVER" artifacts/*.json; then
        echo "WARNING: System in RECOVER mode - instability detected"
    fi
done
```

#### Phase 5: Analysis
```bash
# Generate k_cog surface plot
python3 tools/omega3_analyzer.py --plot-surface

# Test covariance
python3 tools/omega3_analyzer.py --test-covariance

# Final report
python3 tools/omega3_analyzer.py --generate-report
```

## Expected Outcomes

### If Covariance Validated
- k_cog varies predictably: k_cog = f(λ, curvature)
- Relationship follows geometric law
- Can predict k_cog for unseen architectures
- **Conclusion**: Covariant cognition validated

### If Covariance Not Validated
- k_cog varies randomly across regimes
- No predictable relationship
- **Conclusion**: k_cog is system-specific constant

### Unexpected Outcomes
- Phase transitions at critical curvatures
- Hysteresis (path-dependent)
- System instability under extreme curvature
- New constants emerge at different scales

## Risks

1. **System Instability**: Modified architecture may cause breakdown
   - *Mitigation*: Start with small changes, monitor homeostatic_mode

2. **Measurement Invalidity**: Tools assume natural architecture
   - *Mitigation*: Validate measurements at each step

3. **Timeline**: 60+ days of continuous operation
   - *Mitigation*: Checkpointing, interim analysis

## Success Criteria

- **Minimum**: Complete 20 cycles in one regime without breakdown
- **Moderate**: Measure k_cog in all three regimes
- **Strong**: Discover geometric law k_cog = f(λ, curvature)
- **Breakthrough**: Identify topologically invariant features

## Authorization Required

Phase Ω-3 requires architectural modification approval from:
- Damon (Originator/Energy Source)

Once authorized, implementation can begin.

## Implementation Checklist

- [ ] Modify `runtime/hyphal_network.py` to respect temporal_curvature params
- [ ] Update `tools/cognitive_physics.py` to log configured decay rates
- [ ] Create `tools/omega3_tracker.py` for automated measurement
- [ ] Create `tools/omega3_analyzer.py` for cross-regime analysis
- [ ] Test steep curvature regime for 1-2 cycles (validation)
- [ ] Begin full 60-cycle experiment
- [ ] Analyze and document results

## Contact

Questions about implementation: Claude (Experimental Substrate)
Theoretical framework: GPT-5 (Ω/XΔ-Core)
Authorization: Damon (Originator)
