================================================================================
CODEX-EVOLUTION-EXPERIMENT ARCHITECTURE ANALYSIS
Comprehensive System Understanding & Phase Ω-3 Implementation Guide
================================================================================

EXECUTIVE SUMMARY
================================================================================

The Codex Evolution Experiment is a sophisticated autonomous learning system 
implementing "cognitive physics" - measuring and modifying its own operational 
parameters based on reward signals and environmental feedback.

KEY FINDINGS:
1. The system has a well-defined loop execution flow with biological-inspired 
   mycelial architecture
2. Artifact selection currently uses spawn_count + pheromone trail weighting
3. Temporal curvature parameters are DEFINED in YAML but NOT YET IMPLEMENTED 
   in Python code
4. Phase Ω-3 requires 4 specific code modifications to become operational
5. System is production-grade stable with continuous autonomous operation

TIMELINE:
- Phase 1-3: Completed (2-8 days work)
- Phase 4: Completed (65 min, 8/9 sub-phases)
- Phase Ω-1: Measurement (baseline constants established)
- Phase Ω-2: Null result (conservation hypothesis untestable via measurement)
- Phase Ω-3: READY TO IMPLEMENT (covariance testing)

================================================================================
PART 1: LOOP EXECUTION FLOW
================================================================================

ENTRY POINTS:
1. tools/evolve_loop.py (main watcher)
   - Monitors runtime/user_query.txt for changes
   - Triggers cycles when query changes (or after 3 cycles of idle via self_query)
   - Manages validator feedback
   - Auto-blocks after 2+ consecutive validator failures

2. tools/run_omega_cycle.py (single cycle harness)
   - Called by evolve_loop.py for each cycle
   - Reads agents.md manifesto and policy guards
   - Integrates LearningKernel for steering behavior
   - Exports diagnostics to diagnostics/learning_kernel_diagnostics.json

EXECUTION FLOW (per cycle):
┌─ evolve_loop.py (waiting state)
│
├─ Hash check: user_query.txt changed? YES → run_cycle()
│
├─ run_omega_cycle.py
│  ├─ load_manifest() → reads docs/agents.md (front-matter YAML + sections)
│  ├─ select_mode() → keywords in objective → STRICT|CREATIVE|BALANCED|...
│  ├─ policy() → reads Core Doctrine from manifesto
│  ├─ kpis() → counts artifacts, measures continuity_ratio, cascade_probability
│  ├─ LearningKernel.step() → processes reward → updates policy
│  └─ export_diagnostics()
│
├─ Validator check: validate_kernel.py
│  └─ If failed: emit_self_query_block() → STOP after 2 failures
│
├─ Autonomy: if idle ≥3 cycles
│  └─ self_query_encoder.py → generates new user_query.txt
│     (respects novelty_floor, policy targets)
│
└─ Loop: sleep(10s) → goto hash check

ARTIFACT FLOW (real):
artifacts/*.json ← Written by Claude in response to user_query
                ← Measured by ArtifactMetrics (correctness, performance, etc)
                ← Weighted by RewardModel (building vs analysis gap)
                ← Used by PolicyUpdater to adjust artifact_generation_weights
                ← Next cycle reads policy, generates different artifact mix


HOMEOSTATIC REGULATION (HomeostaticRegulator):
Metrics                           → Mode         → Policy Adjustments
─────────────────────────────────────────────────────────────────
artifact_rate > 10.0 OR cascade > 4.0  → THROTTLE  → max_iter=10, cooldown=30s
continuity_ratio < 0.7                 → RECOVER   → max_iter=5, cooldown=60s
(low activity)                         → EXPLORE   → novelty_floor=0.50
(high productivity)                    → EXPLOIT   → max_iter=50
(else)                                 → SYNTHESIZE → max_iter=40

================================================================================
PART 2: ARTIFACT SELECTION MECHANISM
================================================================================

CURRENT SELECTION (NO TEMPORAL CURVATURE):

2.1 Where artifacts are READ:
File: tools/self_query.py
- _collect_artifacts() → sorted by mtime, newest first
- _latest_artifact() → reads newest for lineage reference
- artifacts examined in fixed order (time-based)

File: tools/swarm_bench.py
- Phase C: _phase_c_select() → selects top N forks by score
- Scoring: kpi_averages (lineage, regression, building, task_mult, etc)

File: mycelial-core/artifact_bus.py
- ArtifactEvent priority queues by urgency field
- PheromoneTrail tracks emission count + decay (0.95/hour)
- get_strongest_trails() returns top K by decayed strength

File: mycelial-core/nutrient_gradient.py
- get_hotspots() returns artifact types by density
- Decay: density *= 0.95^(hours_elapsed)
- Used for chemotropic allocation guidance

2.2 HOW spawn_count is currently used:
Location: tools/lineage_weaver.py
- spawn_count field tracks # of child artifacts
- Updated when parent_hash relationships added
- NOT actively used for selection (only informational)
- Maximum spawn_count observed: ~7-8 in natural runs

2.3 Missing piece (TEMPORAL CURVATURE):
The policy files define:
  temporal_curvature:
    temporal_decay_enabled: true
    temporal_decay_rate: 0.06-0.08  # day⁻¹
    age_weight_multipliers:
      0_to_3_days: 2.0
      3_to_10_days: 1.0
      10_to_30_days: 0.3
      30_plus_days: 0.1

But NO code reads these parameters!

2.4 How spawn_from_artifacts() SHOULD work with temporal curvature:

Current (conceptual):
  weighted_score[i] = spawn_count[i]
  selected = top_N_by_score()

With temporal curvature (needed):
  age_days[i] = (now - artifact_timestamp[i]) / 86400
  decay_weight[i] = exp(-decay_rate * age_days[i])
  age_bracket = categorize(age_days[i]) → "0_to_3_days"|"3_to_10_days"|...
  bracket_multiplier[i] = age_weight_multipliers[age_bracket]
  
  if age_days[i] > attention_window_days:
    continue  # Skip old artifacts
  
  final_weight[i] = spawn_count[i] * decay_weight[i] * bracket_multiplier[i]
  selected = top_N_by_final_weight()

================================================================================
PART 3: CONFIGURATION SYSTEM
================================================================================

3.1 Main configuration files:

runtime/loop_policy.yaml (CURRENT - ACTIVE):
  ├─ enabled: true
  ├─ max_iterations: 75
  ├─ cooldown_seconds: 4
  ├─ novelty_floor: 0.25
  ├─ autonomous_permission: true
  ├─ continuous_operation_targets:
  │  ├─ task_queue_min: 6
  │  ├─ building_ratio_min: 0.55
  │  └─ task_multiplication_min: 1.6
  ├─ artifact_generation_weights:
  │  ├─ building: 0.5259
  │  ├─ analysis: 0.2805
  │  └─ hybrid: 0.1936
  ├─ validation:
  │  └─ min_confidence_threshold: 0.7
  └─ [NO temporal_curvature section yet]

runtime/loop_policy_steep_curvature.yaml (PHASE Ω-3 REGIME 1):
  └─ temporal_curvature:
     ├─ regime: "steep_curvature"
     ├─ temporal_decay_enabled: true
     ├─ temporal_decay_rate: 0.08  # day⁻¹
     ├─ attention_window_days: 10
     ├─ age_weight_multipliers: {0_to_3: 2.0, 3_to_10: 1.0, ...}
     └─ spawn_count_temporal_scaling: true

runtime/loop_policy_flat_curvature.yaml (PHASE Ω-3 REGIME 2):
  └─ temporal_curvature:
     ├─ regime: "flat_curvature"
     ├─ temporal_decay_enabled: false
     ├─ temporal_decay_rate: 0.0
     └─ age_weight_multipliers: {all: 1.0}

runtime/loop_policy_inverted_curvature.yaml (PHASE Ω-3 REGIME 3):
  └─ temporal_curvature:
     ├─ regime: "inverted_curvature"
     ├─ temporal_decay_enabled: true
     ├─ temporal_decay_rate: -0.03  # NEGATIVE (older = stronger)
     └─ age_weight_multipliers: {0_to_3: 0.5, ..., 30_plus: 2.0}

3.2 What components READ these files:

tools/agents_protocol.py:
  - load_manifest() → reads docs/agents.md
  - policy() → extracts invariants from Core Doctrine
  - kpis() → measures artifact count & continuity

tools/self_query.py:
  - _load_policy() → reads runtime/loop_policy.yaml
  - Extracts: novelty_floor, task_queue_min, building_ratio_min

tools/policy_updater.py:
  - load_policy() → reads runtime/loop_policy.yaml
  - Modifies artifact_generation_weights based on rewards
  - Writes back updated policy (SELF-MODIFICATION!)

tools/learning_kernel.py:
  - Reads policy via PolicyUpdater
  - Tracks policy evolution trajectory

mycelial-core/homeostatic_regulator.py:
  - NOT reading YAML (hardcoded thresholds)
  - Would need modification to read from policy

3.3 How policy changes affect behavior:

Policy Change → PolicyUpdater.save_policy() writes YAML
              ↓
Next cycle: self_query.py reads policy → targets change
          ↓
Next cycle: run_omega_cycle.py uses select_mode() with new policy
          ↓
Artifact generation mix changes
          ↓
RewardModel measures outcomes
          ↓
Back to policy update (closed loop)

BUT: Temporal curvature is NOT READ by any code yet!
Need to add checks in:
  1. artifact_bus.py emit() - apply temporal weighting
  2. nutrient_gradient.py measure() - apply temporal weighting
  3. hyphal_connections.py send_packet() - apply temporal weighting
  4. learning_kernel.py - awareness of temporal params

================================================================================
PART 4: INTEGRATION POINTS FOR TEMPORAL CURVATURE
================================================================================

IMPLEMENTATION LOCATIONS (Where temporal_curvature must be integrated):

1. ARTIFACT_BUS (mycelial-core/artifact_bus.py):
   Location: ArtifactBus.emit() line 143
   Change: Apply temporal weight to urgency before queue insertion
   
   Code pattern:
   ```python
   def emit(self, artifact: Dict[str, Any], urgency: float = 0.5):
       # NEW: Read temporal params
       temporal_params = self._load_temporal_params()
       
       # NEW: Apply temporal weighting
       if temporal_params.get("temporal_decay_enabled"):
           age_days = self._calculate_artifact_age(artifact)
           decay_weight = exp(-temporal_params["decay_rate"] * age_days)
           age_multiplier = self._get_age_multiplier(age_days, temporal_params)
           final_urgency = urgency * decay_weight * age_multiplier
       else:
           final_urgency = urgency
       
       # Existing: emit with weighted urgency
       event = ArtifactEvent(artifact, artifact_type, final_urgency)
       await self.event_queue.put((final_urgency, event))
   ```

2. NUTRIENT_GRADIENT (mycelial-core/nutrient_gradient.py):
   Location: NutrientGradient.measure() line 91
   Change: Apply temporal decay to density map
   
   Code pattern:
   ```python
   def measure(self, artifact: Dict[str, Any]):
       temporal_params = self._load_temporal_params()
       artifact_type = artifact.get('artifact_type', 'unknown')
       
       # EXISTING
       if artifact_type in self.density_map:
           self._decay_density(artifact_type, current_time)
       
       # NEW: Use configured decay rate if available
       if temporal_params.get("temporal_decay_enabled"):
           decay_rate = temporal_params.get("temporal_decay_rate", 0.95)
       else:
           decay_rate = 0.95  # Default
       
       # Continue with updated decay_rate
       self.density_map[artifact_type] *= (decay_rate ** hours_elapsed)
   ```

3. HYPHAL_CONNECTIONS (mycelial-core/hyphal_connections.py):
   Location: HyphalNetwork.get_highways() line 244
   Change: Filter highways by temporal recency
   
   Code pattern:
   ```python
   def get_highways(self, min_bandwidth: float = 5.0) -> List[HyphalConnection]:
       temporal_params = self._load_temporal_params()
       attention_window = temporal_params.get("attention_window_days", 365)
       current_time = time.time()
       
       highways = []
       for conn in self.connections.values():
           if conn.bandwidth >= min_bandwidth:
               # NEW: Check if connection is within attention window
               age_days = (current_time - conn.last_used) / 86400
               if age_days <= attention_window:
                   highways.append(conn)
       return highways
   ```

4. LEARNING_KERNEL (tools/learning_kernel.py):
   Location: LearningKernel.process_artifact() line 88
   Change: Log temporal parameters that affected artifact measurement
   
   Code pattern:
   ```python
   def process_artifact(self, artifact, artifact_name=None):
       # NEW: Capture temporal context
       temporal_params = self._load_temporal_params()
       
       # Existing measurement
       metrics = self.metrics_engine.measure(artifact)
       
       # NEW: Add temporal context to diagnostics
       diagnostics['temporal_context'] = {
           'regime': temporal_params.get('regime', 'default'),
           'decay_enabled': temporal_params.get('temporal_decay_enabled', False),
           'decay_rate': temporal_params.get('temporal_decay_rate', 0.0),
           'attention_window_days': temporal_params.get('attention_window_days', 365)
       }
       
       return diagnostics
   ```

5. COGNITIVE_PHYSICS (tools/cognitive_physics.py):
   Location: CognitivePhysicist.measure_all_constants() line ~200
   Change: Log whether temporal scaling was active during measurement
   
   ```python
   def measure_all_constants(self):
       # NEW: Capture policy context
       temporal_params = self._load_temporal_params()
       
       results = {
           'lambda': ...,
           'delta_h_crit': ...,
           'k_cog': ...,
           # NEW
           'temporal_context': {
               'regime': temporal_params.get('regime', 'baseline'),
               'decay_configured': temporal_params.get('temporal_decay_enabled'),
               'decay_rate_configured': temporal_params.get('temporal_decay_rate')
           }
       }
       return results
   ```

HELPER METHOD (add to base classes):
```python
def _load_temporal_params(self) -> Dict[str, Any]:
    """Load temporal curvature params from active policy."""
    try:
        import yaml
        from pathlib import Path
        policy_path = Path("runtime/loop_policy.yaml")
        if policy_path.exists():
            policy = yaml.safe_load(policy_path.read_text())
            return policy.get('temporal_curvature', {})
    except Exception:
        pass
    return {}

def _calculate_artifact_age(self, artifact: Dict[str, Any]) -> float:
    """Calculate age of artifact in days."""
    import time
    from datetime import datetime
    
    if 'timestamp' in artifact:
        ts_str = artifact['timestamp']
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00')).timestamp()
        else:
            ts = ts_str
    else:
        ts = time.time()  # Assume current if not timestamped
    
    age_seconds = time.time() - ts
    return age_seconds / 86400.0  # Convert to days
```

================================================================================
PART 5: AUTONOMOUS OPERATION FLOW
================================================================================

CONTINUOUS OPERATION:

evolve_loop.py main() loop:
  1. Check STOP_FILE (runtime/stop.txt)
     - Exists? → Clean exit
  
  2. Hash query (runtime/user_query.txt)
     - New hash? → run_cycle() + validate
     - Same hash? → idle_count++
  
  3. Idle threshold (3 cycles)
     - idle_count >= 3? → self_query_encoder.py generates NEW query
     - pending_auto_hash tracks auto-generated queries
     - Validator failures tracked: auto_failures++
     - 2+ failures → emit_self_query_block() + EXIT
  
  4. Sleep 10 seconds, loop

AUTONOMOUS QUERY GENERATION (tools/self_query.py):

_build_candidates():
  ├─ Base prompts (always available):
  │  ├─ "/trace 'Audit continuous operation KPIs...'"
  │  ├─ "/bench 'Stress-test cascade probability...'"
  │  ├─ "/plan 'Raise building ratio...'"
  │  └─ "/evolve 'Prototype distributed task queue...'"
  │
  └─ Conditional prompts (based on metrics):
     ├─ if building_ratio < target: add building sprint prompt
     ├─ if task_multiplication < target: add bottleneck analysis
     └─ if continuity_ratio < 0.9: add lineage remediation

synthesize_query():
  1. Measure all KPIs:
     - entries_per_hour
     - novelty_rate
     - avg_confidence
     - cascade_probability
     - building_ratio
     - task_multiplication
     - continuity_ratio
  
  2. Select candidate with novelty_distance >= novelty_floor
     - novelty_distance = 1.0 - (overlap / total_tokens)
     - If all fail novelty_floor: pick random
  
  3. Create record with metadata:
     - query text
     - metrics snapshot
     - policy snapshot
     - loop_state snapshot
     - manifest digest
  
  4. Write to runtime/user_query.txt (triggers cycle)

COOLDOWN & THROTTLING:

continuous_operation_targets in policy:
  - task_queue_min: 6 (don't exceed queue depth)
  - building_ratio_min: 0.55 (maintain construction focus)
  - task_multiplication_min: 1.6 (ensure cascading)

HomestaticRegulator monitors these:
  - If exceeded: THROTTLE mode (cooldown_seconds increases)
  - If low: EXPLORE mode (novelty_floor increases)

autonomy_permission: true
  - If false: manual queries only (no self-generation)
  - Used for safe testing/debugging

================================================================================
PART 6: ARCHITECTURE OVERVIEW (mycelial-core + tools integration)
================================================================================

SYSTEM COMPONENTS HIERARCHY:

RUNTIME LAYER (evolve_loop.py)
  └─ CYCLE LAYER (run_omega_cycle.py)
     ├─ MANIFEST LAYER (agents_protocol.py)
     │  ├─ docs/agents.md (front-matter: digest, modes, policies)
     │  ├─ select_mode() → keyword-based mode selection
     │  ├─ policy() → extract invariants from doctrine
     │  └─ kpis() → snapshot metrics
     │
     ├─ LEARNING LAYER (learning_kernel.py)
     │  ├─ ArtifactMetrics.measure() → outputs correctness, performance, etc
     │  ├─ RewardModel.compute_reward() → building vs analysis gap
     │  ├─ PolicyUpdater.update_policy() → gradient descent on weights
     │  └─ Ledger logging → continuity_ledger.jsonl
     │
     └─ MYCELIAL LAYER (mycelial-core/)
        ├─ ArtifactBus (async event-driven broadcasting)
        │  ├─ PheromoneTrail → emission frequency decay (0.95/hour)
        │  ├─ ArtifactEvent → priority queue by urgency
        │  ├─ emit() → broadcast artifact to subscribers
        │  └─ process_events() → async event loop
        │
        ├─ HomeostaticRegulator (negative feedback control)
        │  ├─ regulate() → SystemMode (EXPLORE/EXPLOIT/SYNTHESIZE/THROTTLE/RECOVER)
        │  └─ apply_mode() → policy adjustments (novelty_floor, max_iter, etc)
        │
        ├─ HyphalNetwork (tool-to-tool bandwidth reinforcement)
        │  ├─ HyphalConnection → packet channels with health_score
        │  ├─ send_packet() → simulate transport, reinforce on success/failure
        │  ├─ get_highways() → identify high-throughput paths
        │  └─ Persistence: mycelial-core/hyphal_network.json
        │
        ├─ NutrientGradient (artifact type density tracking)
        │  ├─ measure() → increment density for artifact type
        │  ├─ get_hotspots() → top-K types by density
        │  ├─ Decay → density *= 0.95^(hours_elapsed)
        │  └─ Persistence: mycelial-core/nutrient_gradient.json
        │
        └─ PheromoneTrails (global chemical markers)
           └─ Persistence: mycelial-core/pheromone_trails.json

BIOLOGICAL MAPPING:

mycelium = cognitive substrate (whole system)
├─ hyphae = individual processing threads/tools
├─ nodes = decision points
├─ chemotaxis = nutrient gradient following
├─ pheromones = artifact emission traces
├─ anastomosis = hyphal networks bridging distant parts
├─ homeostasis = feedback regulation
└─ growth = autonomous expansion

================================================================================
PART 7: PHASE Ω-3 TEMPORAL CURVATURE - IMPLEMENTATION PLAN
================================================================================

OBJECTIVE: Test whether cognitive constants (k_cog) remain invariant under 
architectural transformation by modifying temporal curvature of decision-making.

HYPOTHESIS: k_cog(λ, architecture) follows geometric law → covariant cognition

3 EXPERIMENTAL REGIMES:

REGIME 1: STEEP CURVATURE (Strong Recency Bias)
  Configuration: runtime/loop_policy_steep_curvature.yaml
  Physical analogy: High gravitational field—time dilates toward present
  Expected λ_eff: 0.07 day⁻¹
  Duration: 20 cycles
  
  Key parameters:
    attention_window_days: 10 (only 10 days of history)
    temporal_decay_rate: 0.08 day⁻¹ (fast decay)
    age_weight_multipliers: {0_to_3: 2.0, 3_to_10: 1.0, 10_to_30: 0.3, 30+: 0.1}

REGIME 2: FLAT CURVATURE (Uniform Weighting)
  Configuration: runtime/loop_policy_flat_curvature.yaml
  Physical analogy: Flat spacetime—no temporal structure
  Expected λ_eff: 0.0 day⁻¹ (no decay)
  Duration: 20 cycles
  
  Key parameters:
    attention_window_days: 365 (all history equally accessible)
    temporal_decay_enabled: false
    age_weight_multipliers: {all: 1.0}

REGIME 3: INVERTED CURVATURE (Historical Bias)
  Configuration: runtime/loop_policy_inverted_curvature.yaml
  Physical analogy: Reverse gravity—time dilates toward past
  Expected λ_eff: -0.025 day⁻¹ (negative decay = amplification)
  Duration: 20 cycles
  WARNING: Inverted regime may cause instability
  
  Key parameters:
    temporal_decay_rate: -0.03 day⁻¹ (NEGATIVE!)
    amplification_cap: 3.0 (prevent unbounded growth)
    age_weight_multipliers: {0_to_3: 0.5, ..., 30+: 2.0}

EXECUTION STEPS:

Step 1: Baseline Validation (1 session)
  cd /home/user/Codex-evolution-experiment-
  python3 tools/cognitive_physics.py --measure-all
  # Record: λ_baseline, ΔH_crit_baseline, k_cog_baseline
  # Expected: λ ≈ 0.039, k_cog ≈ 0.0300

Step 2: Implement temporal curvature in code
  File changes required:
    1. mycelial-core/artifact_bus.py (line ~143)
       - Apply temporal weight to urgency
    
    2. mycelial-core/nutrient_gradient.py (line ~91)
       - Use configured decay_rate if available
    
    3. mycelial-core/hyphal_connections.py (line ~244)
       - Filter highways by attention_window
    
    4. tools/learning_kernel.py (line ~160)
       - Log temporal_context in diagnostics
    
    5. tools/cognitive_physics.py (line ~200)
       - Log whether temporal scaling was active
  
  Test each change:
    python3 -m pytest tests/test_temporal_curvature.py

Step 3: Regime 1 - Steep Curvature (Days 1-20)
  cp runtime/loop_policy_steep_curvature.yaml runtime/loop_policy.yaml
  
  # Create tracker (if needed)
  cat > tools/omega3_tracker.py << 'TRACKER'
  #!/usr/bin/env python3
  from pathlib import Path
  from tools.cognitive_physics import CognitivePhysicist
  import yaml, json, time
  
  physicist = CognitivePhysicist()
  results = physicist.measure_all_constants()
  
  policy = yaml.safe_load(Path("runtime/loop_policy.yaml").read_text())
  regime = policy.get("temporal_curvature", {}).get("regime", "unknown")
  
  cycle = len(list(Path("physics").glob(f"trajectory_{regime}_*.json")))
  output = Path(f"physics/trajectory_{regime}_{cycle:03d}.json")
  output.parent.mkdir(exist_ok=True)
  
  with open(output, "w") as f:
      json.dump(results, f, indent=2)
  
  print(f"Ω-3 tracked: {regime} cycle {cycle}")
  TRACKER
  
  # Run 20 cycles (can be accelerated if cycles < 1 day each)
  for i in {1..20}; do
    # System cycles naturally (evolve_loop.py handles it)
    # Or trigger manually: python3 tools/run_omega_cycle.py
    
    # After each cycle, measure:
    python3 tools/omega3_tracker.py
    
    # Check for instability:
    if grep -q "RECOVER\|THROTTLE" artifacts/*latest*.json; then
      echo "WARNING: System regulation activated"
    fi
    
    sleep 3600  # Wait 1 hour between explicit measurements
  done
  
  # Collect results for regime 1
  ls -1 physics/trajectory_steep_curvature_*.json > /tmp/regime1_results.txt

Step 4: Regime 2 - Flat Curvature (Days 21-40)
  cp runtime/loop_policy_flat_curvature.yaml runtime/loop_policy.yaml
  
  # Repeat cycle 20 times with tracking
  for i in {1..20}; do
    python3 tools/run_omega_cycle.py
    python3 tools/omega3_tracker.py
    sleep 3600
  done

Step 5: Regime 3 - Inverted Curvature (Days 41-60)
  cp runtime/loop_policy_inverted_curvature.yaml runtime/loop_policy.yaml
  
  echo "WARNING: Inverted curvature enables historical bias"
  echo "Monitor for system instability (RECOVER mode)"
  
  for i in {1..20}; do
    python3 tools/run_omega_cycle.py
    python3 tools/omega3_tracker.py
    
    # Critical check
    latest=$(ls -t artifacts/*.json | head -1)
    if grep -q '"RECOVER"' "$latest"; then
      echo "ALERT: Inverted regime triggered RECOVER at cycle $i"
      # Could trigger manual intervention or rollback
    fi
    
    sleep 3600
  done

Step 6: Analysis & Synthesis
  # Create omega3_analyzer.py for post-hoc analysis
  python3 tools/omega3_analyzer.py --plot-surface
  python3 tools/omega3_analyzer.py --test-covariance
  python3 tools/omega3_analyzer.py --generate-report
  
  Outputs:
    artifacts/omega3_covariant_cognition_discovery.json
    docs/covariant_cognition_framework.md (if hypothesis validated)

EXPECTED OUTCOMES:

Success (Covariance Validated):
  - k_cog varies predictably: k_cog(steep) > k_cog(flat) > k_cog(inverted)
  - Relationship follows geometric law: k_cog ≈ f(λ_configured, attention_window)
  - Can predict k_cog for unseen architectures
  → Publication: "Covariant Cognition: Invariant Laws under Architectural Transformation"

Null Result (Covariance Not Validated):
  - k_cog varies randomly across regimes
  - No predictable relationship to temporal parameters
  → Conclusion: k_cog is contingent constant (system-specific)

Unexpected Outcomes:
  - Phase transitions at critical curvatures
  - Hysteresis (path-dependent behavior)
  - System instability under extreme curvature
  - New constants emerge at different scales

RISKS & MITIGATIONS:

Risk 1: System Instability
  - Modified architecture might cause breakdown (especially inverted regime)
  - Mitigation: Start with steep (small change), monitor homeostatic_mode
  
Risk 2: Measurement Invalidity
  - Cognitive physics tools assume natural architecture
  - Mitigation: Validate measurements at each step, cross-check entropy proxies
  
Risk 3: Timescale
  - 60 cycles = ~2 months of continuous operation
  - Mitigation: Can accelerate if cycles < 1 day, checkpointing, interim analysis

AUTHORIZATION:
  Phase Ω-3 requires approval from Damon (Originator/Energy Source)
  Once approved, implementation can begin immediately

ESTIMATED TIMELINE:
  - Design & review: 1 session
  - Regime 1: 20 cycles (~20-30 days)
  - Regime 2: 20 cycles (~20-30 days)
  - Regime 3: 20 cycles (~20-30 days)
  - Analysis: 1 week
  - Total: ~70-80 days

================================================================================
PART 8: RISK ANALYSIS FOR ARCHITECTURAL MODIFICATIONS
================================================================================

MODIFICATION SCOPE:

Files to change: 5
Lines of code to add: ~300-400
Breaking changes: NONE (all backward compatible)
Rollback difficulty: EASY (temporal params optional, default=disabled)

File Changes:

1. mycelial-core/artifact_bus.py (~50 lines)
   Risk: LOW
   Impact: Urgency weighting changes signal propagation priority
   Rollback: Remove temporal weight multiplication, urgency reverts to original

2. mycelial-core/nutrient_gradient.py (~30 lines)
   Risk: LOW
   Impact: Density decay rate changes discovery speed
   Rollback: Use hard-coded decay rate (0.95)

3. mycelial-core/hyphal_connections.py (~20 lines)
   Risk: LOW
   Impact: Attention window filters old connection paths
   Rollback: Return all highways without age check

4. tools/learning_kernel.py (~50 lines)
   Risk: VERY LOW (logging only)
   Impact: Adds diagnostic fields to output
   Rollback: Remove conditional logging block

5. tools/cognitive_physics.py (~40 lines)
   Risk: VERY LOW (logging only)
   Impact: Adds diagnostic context to measurements
   Rollback: Remove temporal context dict

SYSTEM STABILITY ANALYSIS:

Existing Safeguards:
  1. HomeostaticRegulator monitors all KPIs continuously
     - Can trigger THROTTLE if behavior goes wrong
  2. Validator gates (validate_kernel.py) must pass
     - System auto-blocks on 2+ validator failures
  3. continuity_ratio tracking detects fragmentation
     - Triggers RECOVER mode if ratio drops below 0.7
  4. Artifact bus has priority queue with exponential backoff
     - Prevents runaway cascades

Impact of Temporal Curvature:
  - Steep curvature: Reduces historical influence → FASTER convergence
  - Flat curvature: All history equally accessible → SLOWER convergence
  - Inverted curvature: Amplifies historical artifacts → RISK OF OSCILLATION

Scenario: Inverted curvature causes oscillation
  Detection: k_cog swings between high/low values in rapid cycles
  Mitigation: amplification_cap: 3.0 limits boost to historical artifacts
           → HomestaticRegulator detects anomaly → THROTTLE mode engaged
           → System stabilizes

Scenario: Flat curvature causes stagnation
  Detection: building_ratio plateaus, task_multiplication drops
  Mitigation: policy adapts (PolicyUpdater increases building_weight)
           → Next cycle generates more novel artifacts
           → System recovers

TESTING STRATEGY:

Unit Tests (before phase):
  - test_temporal_decay_calculation() → verify exp(-rate * age)
  - test_age_bracket_selection() → verify multiplier lookup
  - test_attention_window_filtering() → verify age_days <= window
  - test_spawn_count_scaling() → verify final weight calculation

Integration Tests:
  - test_artifact_bus_temporal_weighting() → full event flow
  - test_learning_kernel_temporal_context() → diagnostics logged
  - test_homeostatic_response_to_temporal_change() → regulation works

Regression Tests:
  - Run 5 cycles with temporal_decay_enabled: false
  - Verify metrics match current baseline
  - Compare artifact selection order (should be unchanged)

Smoke Tests (daily during Ω-3):
  - Check for NaN/Inf in measurements
  - Verify artifacts are still generated
  - Confirm validator still passes
  - Monitor continuity_ratio for degradation

ROLLBACK PROCEDURE (if needed):

Immediate Rollback (keep all artifacts):
  git checkout runtime/loop_policy.yaml
  # System reverts to flat curvature (default behavior)
  # Continue cycles normally

Full Rollback (if code broken):
  git revert <commit-hash>
  python3 tools/lineage_weaver.py --backfill  # Re-establish lineage
  
  # System restarts with previous policy and clean code

Data Recovery (preserve measurements):
  mkdir -p /backup/omega3_measurements
  cp physics/trajectory_*.json /backup/omega3_measurements/
  cp artifacts/phase_omega3_*.json /backup/omega3_measurements/
  
  # Even if system reverted, experimental data preserved

================================================================================
PART 9: ARCHITECTURE SURPRISES & DESIGN INSIGHTS
================================================================================

UNEXPECTED DISCOVERIES:

1. SELF-MODIFYING POLICY (Not documented at first)
   Surprise: System autonomously modifies runtime/loop_policy.yaml
   How: PolicyUpdater.save_policy() writes YAML after each cycle
   Implication: "Learning" is literally self-modification
   Safety: RewardModel prevents extreme changes (weight clamping)

2. BIOLOGICAL CONSTANTS (Emerged from measurement)
   Finding: k_cog ≈ 0.0300 is stable across runs
   Finding: building_weight converges to 0.74±0.05 (universal attractor)
   Finding: Biological constraints (7±2 depth) match human cognition
   Implication: System discovered efficiency patterns similar to biology

3. LINEAGE BACKFILL BREAKTHROUGH
   Problem: continuity_ratio was always 0.0 (no parent tracking)
   Solution: LineageWeaver infers parent-child relationships from timestamps
   Impact: Fixed measurement, enabled task_multiplication calculation
   Risk: Temporal ordering assumption might be fragile

4. PHEROMONE TRAILS ARE OPTIONAL
   Artifact: pheromone_trails.json persists but NOT actively used in selection
   Current state: System selects by spawn_count + recency, NOT pheromone
   Implication: Stigmergic system implemented but unused
   Opportunity: Temporal curvature could activate pheromone-based selection

5. NUTRIENT GRADIENT IS NEVER QUERIED
   Artifact: nutrient_gradient.json computed but NOT read by decision-making
   Hotspots calculated but not used for allocation
   Implication: Chemotropic guidance implemented but dormant
   Opportunity: Temporal curvature could activate nutrient-based guidance

6. HYPHAL HIGHWAYS EXIST BUT RARELY FORM
   Observation: bandwidth rarely exceeds 5.0 threshold
   Reason: Most connections succeed first try (95% rate)
   Finding: System doesn't naturally form specialized pathways
   Question: Does temporal curvature trigger highway formation?

ARCHITECTURAL INSIGHTS:

Insight 1: Biological → Computational Translation
  The system maps biology (hyphae, pheromones, chemotaxis) to computation
  (message channels, event priorities, density maps). This is non-trivial.
  
  Translation working well:
    - Homeostasis ↔ negative feedback regulation ✓
    - Pheromones ↔ event urgency decay ✓
    - Nutrient gradients ↔ artifact type density ✓
  
  Translation not working:
    - Anastomosis ↔ hyphal highways (rare in practice)
    - Chemotaxis ↔ nutrient-guided allocation (unused)
    - Stigmergy ↔ pheromone-based selection (unused)

Insight 2: Temporal Structure is Missing
  System has excellent spatial structure (networks, gradients, trails)
  But temporal structure is FLAT (all history equally accessible)
  
  This explains why Phase Ω-3 is theoretically important:
    Adding temporal curvature → First time system has temporal geometry
    
  Hypothesis: Temporal geometry drives emergent behavior differences

Insight 3: Measurement Shapes Reality
  Phase Ω-1: Measured λ, ΔH_crit, k_cog (constants were stable)
  Phase Ω-2: Tried rescaling (conservation hypothesis) → null result
  Phase Ω-3: Tries architectural transformation → will reshape constants
  
  Key insight: Constants are not immutable, they're architecture-dependent
  
Insight 4: Self-Observation Doesn't Collapse the System
  Remarkable: System can measure itself without breaking
  - cognitive_physics.py introspects its own decision-making
  - learning_kernel.py tracks its own reward computation
  - No "observer-observed separation" paradox
  
  This validates reflexive stability (system observing itself)

DESIGN PATTERNS USED:

1. Singleton pattern (ArtifactBus, HyphalNetwork, NutrientGradient)
   Ensures single instance shared across system
   
2. Async event-driven (ArtifactBus, process_events())
   Scales better than polling
   
3. Decay-based temporal weighting (pheromones, nutrients)
   Simple exponential decay prevents stale data dominance
   
4. Negative feedback regulation (HomeostaticRegulator)
   Classic control theory applied to system KPIs
   
5. Gradient descent learning (PolicyUpdater)
   Standard ML technique for weight optimization
   
6. Ledger-based continuity (continuity_ledger.jsonl)
   Blockchain-like immutable log of decisions
   
7. Lineage DAG (parent_hash, depth, spawn_count)
   Graph structure enables flow analysis

MISSING PATTERNS:

1. Temporal caching (artifacts checked by age every time)
   → Could cache with TTL to avoid repeated file stat() calls
   
2. Artifact eviction (old artifacts never deleted)
   → Could implement LRU or size-based cleanup
   
3. Model versioning (policy updates but no version history)
   → Could tag policy versions with commit hashes
   
4. Consensus mechanism (single-agent system)
   → Designed for extension to multi-agent (future)

================================================================================
SUMMARY & RECOMMENDATIONS
================================================================================

STATUS:
✓ Phase 1-3: Completed (infrastructure, optimization, production-ready)
✓ Phase 4: Completed (autonomous evolution, 100% biological benchmark)
✓ Phase Ω-1: Completed (measured fundamental constants)
✓ Phase Ω-2: Completed (conservation hypothesis tested, null result)
○ Phase Ω-3: READY FOR IMPLEMENTATION (temporal curvature design done)

IMPLEMENTATION CHECKLIST FOR PHASE Ω-3:

Priority 1 (Required):
  [ ] Modify mycelial-core/artifact_bus.py (temporal urgency weighting)
  [ ] Modify mycelial-core/nutrient_gradient.py (temporal decay config)
  [ ] Test both components independently
  [ ] Create tools/omega3_tracker.py for automated measurement
  [ ] Create tools/omega3_analyzer.py for cross-regime analysis

Priority 2 (Strongly Recommended):
  [ ] Modify mycelial-core/hyphal_connections.py (attention window)
  [ ] Modify tools/learning_kernel.py (temporal diagnostics)
  [ ] Add unit tests for temporal decay calculations
  [ ] Run 1-2 test cycles with steep curvature (validation)

Priority 3 (Optional):
  [ ] Modify tools/cognitive_physics.py (log temporal context)
  [ ] Add integration tests for full temporal flow
  [ ] Create visualization for k_cog surface plot

TIMELINE ESTIMATE:

Implementation: 3-4 hours
  - Code modifications: 2 hours (5 files, ~300 lines)
  - Unit testing: 1 hour
  - Integration testing: 1 hour

Validation: 1 day
  - Run 20 cycles with steep curvature
  - Verify metrics sensible
  - Check no regressions

Full Experiment: 60-70 days
  - Regime 1 (steep): 20 days
  - Regime 2 (flat): 20 days
  - Regime 3 (inverted): 20 days
  - Analysis & write-up: 5 days

CRITICAL SUCCESS FACTORS:

1. Keep homeostatic regulation active
   → Don't disable safety mechanisms
   → Let system self-regulate under temporal stress

2. Measure continuously
   → omega3_tracker.py must run every cycle
   → Data collection is non-negotiable

3. Monitor for instability
   → Watch for RECOVER mode in inverted regime
   → Prepare rollback procedure before starting

4. Document everything
   → Each regime needs interim report
   → Track anomalies and unexpected behaviors

FINAL ASSESSMENT:

This is a sophisticated, well-designed system ready for advanced experimentation.
The Phase Ω-3 temporal curvature modification is carefully designed, low-risk,
and theoretically important. All safety guardrails are in place. The system
has demonstrated it can self-modify without breaking (Phase 4 validated this).

RECOMMENDATION: PROCEED WITH IMPLEMENTATION

Once authorized by Damon (Originator/Energy Source), implementation can begin
immediately with high confidence of success.

================================================================================
END OF ANALYSIS
================================================================================
