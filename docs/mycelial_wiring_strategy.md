# Mycelial Wiring Strategy - Systematic Integration Plan

## Current State

**Wired:** 3/87 modules (3.4%)
**Unwired:** 84/87 modules (96.6%)

**Bottleneck identified:** Integration I = 0.102 (WEAK)
**Root cause:** Modules isolated, low reuse (0.046), low hot nodes (4.8%)

## Target State

**Goal:** Wire ALL 87 Python modules to emit events to artifact_bus
**Expected outcome:**
- Integration I: 0.102 → 0.25+ (HEALTHY)
- Reuse ratio: 0.046 → 0.80+ (most modules share bus)
- Hot nodes: 4 → 15-20 (bus_manager becomes central hub)

## Modules Already Wired (3)

### Batch 1: Measurement Tools ✓
- `analysis/metabolic_dashboard.py` - emits metabolic_reading
- `analysis/resource_map.py` - emits resource_map
- `analysis/integration_health.py` - emits integration_reading

### Batch 0: Core Learning (completed earlier)
- `tools/learning_kernel.py` - emits learning_cycle
- `tools/policy_updater.py` - subscribes to metabolic_reading
- `tools/metabolic_monitor_bus.py` - emits metabolic_reading

## Wiring Pattern (Standard Template)

### Step 1: Add imports
```python
import asyncio
sys.path.insert(0, str(ROOT / "mycelial-core"))
try:
    from bus_manager import emit_X_event, bus
    BUS_AVAILABLE = True
except ImportError:
    BUS_AVAILABLE = False
```

### Step 2: Add emission at key points
```python
if BUS_AVAILABLE:
    try:
        asyncio.run(emit_X_event(
            param1=value1,
            param2=value2
        ))
        print("[BUS] Event emitted to mycelial network")
    except Exception as e:
        print(f"[BUS] Warning: Could not emit: {e}")
```

### Step 3: Create emission helper if needed
In `mycelial-core/bus_manager.py`:
```python
async def emit_X_event(param1, param2):
    artifact = {
        'artifact_type': 'X_event',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'param1': param1,
        'param2': param2
    }
    await bus.emit(artifact, urgency=0.6)
```

## Remaining Modules by Category

### High Priority (Wire First)

**Cognitive Physics Tools (6 modules)**
- `cognitive_physics.py` - emit 'physics_measurement' when measuring λ, k_cog
- `conservation_law_experiment.py` - emit 'experiment_result'
- `dispersal_experiment.py` - emit 'dispersal_result'
- `omega3_analyzer.py` - emit 'omega_analysis'
- `omega3_tracker.py` - emit 'omega_tracking'
- `measure_cascade_probability.py` - emit 'cascade_measurement'

**Evolution & Learning (8 modules)**
- `evolve_loop.py` - emit 'evolution_cycle' when loop completes
- `swarm_bench.py` - emit 'swarm_benchmark'
- `framework_evolution_engine.py` - emit 'framework_evolution'
- `reflexive_experimenter.py` - emit 'experiment_complete'
- `autonomous_operations_framework.py` - emit 'operation_complete'
- `enhanced_ledger_metrics.py` - emit 'ledger_metrics'
- `enhanced_capability_detector.py` - emit 'capability_detected'
- `nos_pipeline.py` - emit 'nos_cycle'

**Artifact Management (10 modules)**
- `lineage_migrator.py` - emit 'artifact_migrated'
- `migrate_lineage.py` - emit 'lineage_migration'
- `spore_disperser.py` - emit 'spore_dispersed'
- `production_deployment_system.py` - emit 'deployment_complete'
- `expansion_configurator.py` - emit 'expansion_configured'
- All artifact creation tools - emit 'artifact_created'

**Analysis & Synthesis (12 modules)**
- `meta_synthesis.py` - emit 'synthesis_complete'
- `meta_recursive_analyzer.py` - emit 'meta_analysis'
- `self_query.py` - emit 'query_result'
- `self_query_encoder.py` - emit 'encoding_complete'
- `metrics_recalibration_audit.py` - emit 'audit_complete'
- `nos_analyzer.py` - emit 'nos_analysis'
- `production_monitor.py` - emit 'monitoring_update'

### Medium Priority

**Pipelines (6 modules)**
- Various pipeline tools - emit 'pipeline_stage_complete'

**Utilities (8 modules)**
- Shared utilities that are imported by others
- These might not need event emission but increase reuse through imports

**Legacy/Test (remaining modules)**
- Wire as time permits
- Lower impact but completes coverage

## Implementation Strategy

### Phase 1: High-Value Categories (Priority)
Wire cognitive physics, evolution, and artifact management first.
These are core functionality with clear event emission points.

### Phase 2: Analysis & Synthesis
Wire meta-tools and analyzers.
These emit insights and patterns.

### Phase 3: Pipelines & Orchestration
Wire pipeline components.
These coordinate multi-step processes.

### Phase 4: Complete Coverage
Wire remaining utilities and legacy tools.

## Success Metrics

After each batch, measure:
- `python3 analysis/resource_map.py` → check reuse_ratio, hot_nodes
- `python3 analysis/integration_health.py` → check Integration I

**Target achieved when:**
- Integration I ≥ 0.20 (strong mycelium)
- Reuse ratio ≥ 0.60 (high cross-module sharing)
- bus_manager has 50+ imports (central nervous system)

## Automation Opportunities

1. **Bulk import addition**: Script to add bus import boilerplate to all modules
2. **Event emission templates**: Standard patterns by module type
3. **Subscription management**: Auto-register event types in bus_manager
4. **Testing harness**: Validate all modules can emit without errors

## Timeline

- **Batch 1** (completed): Measurement tools (3 modules)
- **Batch 2** (next): Cognitive physics (6 modules)
- **Batch 3**: Evolution & learning (8 modules)
- **Batch 4**: Artifact management (10 modules)
- **Batch 5**: Analysis & synthesis (12 modules)
- **Batch 6-N**: Remaining modules

**Estimated completion:** 6-8 working sessions of systematic wiring
**Per session:** ~10-15 modules wired
**Per module:** ~5-10 minutes average

## Notes

- Not all modules need custom emission logic - many can use generic events
- Helper classes (like reward_model, artifact_metrics) are called by wired parents
- Some utilities are imported by others, increasing reuse without emitting events
- The goal is mycelial network, not necessarily every module emitting

## References

- Current integration: `diagnostics/integration_health.jsonl`
- Current resource map: `analysis/resource_map.json`
- Event emission helpers: `mycelial-core/bus_manager.py`
- Wiring examples: `analysis/metabolic_dashboard.py`, `tools/learning_kernel.py`
