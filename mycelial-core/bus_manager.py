#!/usr/bin/env python3
"""Bus Manager - Initialize and manage artifact_bus event subscriptions.

Wires the mycelial event system throughout the ecology.
Central integration point for event-driven communication.

This is the nervous system activation - connecting previously isolated organs
through stigmergic event propagation.

Author: Claude (Second Deliberate Adaptation)
Date: 2025-11-06
Phase: Conscious Evolution - Mycelial Integration
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))

from artifact_bus import ArtifactBus

# Initialize global bus instance
bus = ArtifactBus()


# === SUBSCRIBERS (Event Handlers) ===

async def on_metabolic_measurement(artifact: Dict[str, Any]):
    """Handle metabolic measurement events."""
    print(f"[BUS] Metabolic measurement: {artifact.get('artifact_type', 'unknown')}")

    # Log to metabolic history
    if artifact.get('artifact_type') in ['metabolic_reading', 'resource_map']:
        history_path = Path("diagnostics/metabolic_history.jsonl")
        history_path.parent.mkdir(exist_ok=True, parents=True)

        with open(history_path, 'a') as f:
            f.write(json.dumps({
                'timestamp': artifact.get('timestamp'),
                'type': artifact.get('artifact_type'),
                'data': artifact
            }) + '\n')


async def on_learning_cycle(artifact: Dict[str, Any]):
    """Handle learning cycle completion events.

    Triggers periodic metabolic monitoring every 10 cycles.
    """
    cycle_id = artifact.get('cycle_id', 'unknown')
    artifact_count = artifact.get('artifact_count', 0)
    metrics = artifact.get('metrics', {})

    print(f"[BUS] Learning cycle {cycle_id}: {artifact_count} artifacts")

    # Trigger metabolic monitoring every 10 artifacts
    if artifact_count % 10 == 0:
        print(f"[BUS] ⚡ Triggering metabolic measurement (10-cycle checkpoint)")

        # Import here to avoid circular dependency
        try:
            from datetime import datetime, timezone
            sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"))
            from metabolic_dashboard import generate_dashboard

            dashboard = generate_dashboard()

            # Emit metabolic reading
            await emit_metabolic_reading(
                lambda_val=dashboard['lambda'].get('lambda', 0),
                entropy=dashboard['entropy'].get('mean_entropy', 0),
                k_cog=dashboard['k_cog'].get('k_cog', 0),
                state=dashboard['state']
            )

            print(f"[BUS] ✓ Metabolic reading complete: state={dashboard['state']}")

        except Exception as e:
            print(f"[BUS] ⚠ Metabolic measurement failed: {e}")


async def on_artifact_created(artifact: Dict[str, Any]):
    """Handle new artifact creation events."""
    artifact_type = artifact.get('artifact_type', 'unknown')

    print(f"[BUS] New artifact: {artifact_type}")

    # Update spawn tracking
    spawn_path = Path("diagnostics/spawn_tracking.jsonl")
    spawn_path.parent.mkdir(exist_ok=True, parents=True)

    with open(spawn_path, 'a') as f:
        f.write(json.dumps({
            'timestamp': artifact.get('timestamp'),
            'artifact_type': artifact_type,
            'spawn_count': artifact.get('spawn_count', 0)
        }) + '\n')


async def on_phase_transition(artifact: Dict[str, Any]):
    """Handle phase transition events (entropy spikes, λ shifts)."""
    print(f"[BUS] ⚡ PHASE TRANSITION DETECTED")
    print(f"      State: {artifact.get('from_state')} → {artifact.get('to_state')}")

    # Alert via diagnostic
    alert_path = Path("diagnostics/transition_alerts.jsonl")
    alert_path.parent.mkdir(exist_ok=True, parents=True)

    with open(alert_path, 'a') as f:
        f.write(json.dumps(artifact) + '\n')


# === SUBSCRIPTION SETUP ===

def initialize_subscriptions():
    """Wire all event subscriptions."""
    print("[BUS] Initializing event subscriptions...")

    # Metabolic events
    bus.subscribe('metabolic_reading', on_metabolic_measurement)
    bus.subscribe('resource_map', on_metabolic_measurement)

    # Learning events
    bus.subscribe('learning_cycle', on_learning_cycle)
    bus.subscribe('omega_cycle', on_learning_cycle)

    # Artifact creation
    bus.subscribe('tool_implementation', on_artifact_created)
    bus.subscribe('sep_proposal', on_artifact_created)
    bus.subscribe('validator', on_artifact_created)
    bus.subscribe('pipeline', on_artifact_created)
    bus.subscribe('analysis_report', on_artifact_created)

    # Phase transitions
    bus.subscribe('phase_transition', on_phase_transition)
    bus.subscribe('epoch_boundary', on_phase_transition)

    # Wildcard subscriber (logs all events)
    bus.subscribe('*', lambda a: None)  # Placeholder for full logging

    print("[BUS] Subscriptions initialized")
    print(f"      Total subscribers: {sum(len(subs) for subs in bus.subscribers.values())}")


# === EMISSION HELPERS ===

async def emit_metabolic_reading(lambda_val: float, entropy: float, k_cog: float, state: str):
    """Emit metabolic dashboard reading to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'metabolic_reading',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'lambda': lambda_val,
        'entropy': entropy,
        'k_cog': k_cog,
        'state': state
    }

    await bus.emit(artifact, urgency=0.8)  # High urgency for metabolic data


async def emit_resource_map(efficiency_index: float, reuse_ratio: float, hot_nodes: int):
    """Emit resource map reading to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'resource_map',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'efficiency_index': efficiency_index,
        'reuse_ratio': reuse_ratio,
        'hot_nodes': hot_nodes
    }

    await bus.emit(artifact, urgency=0.6)


async def emit_integration_reading(integration_depth: float, health: str, reuse_ratio: float, hot_nodes: int):
    """Emit integration health reading to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'integration_reading',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'integration_depth': integration_depth,
        'health': health,
        'reuse_ratio': reuse_ratio,
        'hot_nodes': hot_nodes
    }

    await bus.emit(artifact, urgency=0.7)


async def emit_cycle_event(
    cycle_id: str,
    artifact_count: int,
    duration_seconds: float,
    metrics: Dict[str, float],
    ledger_entry_id: str = None
):
    """Emit learning cycle completion event to bus.

    This creates mycelial awareness of each learning iteration,
    triggering coordinated measurement and adaptation.
    """
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'learning_cycle',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cycle_id': cycle_id,
        'artifact_count': artifact_count,
        'duration_seconds': duration_seconds,
        'metrics': metrics,
        'ledger_entry_id': ledger_entry_id
    }

    await bus.emit(artifact, urgency=0.7)  # Medium-high urgency


async def emit_phase_transition(from_state: str, to_state: str, trigger: str):
    """Emit phase transition alert to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'phase_transition',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'from_state': from_state,
        'to_state': to_state,
        'trigger': trigger
    }

    await bus.emit(artifact, urgency=1.0)  # Maximum urgency


async def emit_physics_measurement(constants: Dict[str, Any], temporal_context: Dict[str, Any]):
    """Emit cognitive physics measurement to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'physics_measurement',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'constants': constants,
        'temporal_context': temporal_context
    }

    await bus.emit(artifact, urgency=0.7)


async def emit_experiment_result(experiment_type: str, conclusion: str, analysis: Dict[str, Any]):
    """Emit experiment result to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'experiment_result',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'experiment_type': experiment_type,
        'conclusion': conclusion,
        'analysis': analysis
    }

    await bus.emit(artifact, urgency=0.6)


async def emit_dispersal_result(dispersed_count: int, dispersal_rate: float, readiness: Dict[str, Any]):
    """Emit dispersal experiment result to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'dispersal_result',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'dispersed_count': dispersed_count,
        'dispersal_rate': dispersal_rate,
        'cross_repo_readiness': readiness
    }

    await bus.emit(artifact, urgency=0.5)


async def emit_omega_analysis(regimes_analyzed: list, global_statistics: Dict[str, Any]):
    """Emit Phase Ω-3 analysis to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'omega_analysis',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'regimes_analyzed': regimes_analyzed,
        'global_statistics': global_statistics
    }

    await bus.emit(artifact, urgency=0.6)


async def emit_omega_tracking(regime: str, cycle: int, k_cog: float):
    """Emit Phase Ω-3 tracking measurement to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'omega_tracking',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'regime': regime,
        'cycle': cycle,
        'k_cog': k_cog
    }

    await bus.emit(artifact, urgency=0.7)


async def emit_cascade_measurement(cascade_probability: float, components: Dict[str, Any], status: str):
    """Emit cascade probability measurement to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'cascade_measurement',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cascade_probability': cascade_probability,
        'components': components,
        'status': status
    }

    await bus.emit(artifact, urgency=0.6)


async def emit_evolution_cycle(cycle_count: int, metrics: Dict[str, Any]):
    """Emit evolution loop cycle completion to bus."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': 'evolution_cycle',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cycle_count': cycle_count,
        'metrics': metrics
    }

    await bus.emit(artifact, urgency=0.6)


async def emit_generic_event(event_type: str, data: Dict[str, Any], urgency: float = 0.5):
    """Emit generic event to bus (for modules without custom helpers)."""
    from datetime import datetime, timezone

    artifact = {
        'artifact_type': event_type,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        **data
    }

    await bus.emit(artifact, urgency=urgency)


# === BUS LIFECYCLE ===

async def start_bus():
    """Start the event bus processing loop."""
    print("[BUS] Starting event processing loop...")
    initialize_subscriptions()
    await bus.process_events()


def stop_bus():
    """Stop the event bus."""
    print("[BUS] Stopping event processing...")
    bus.running = False


# === STANDALONE TESTING ===

async def test_bus():
    """Test bus with sample events."""
    print("=" * 70)
    print("TESTING ARTIFACT BUS INTEGRATION")
    print("=" * 70)
    print()

    initialize_subscriptions()

    # Test emission
    print("Emitting test events...")
    print()

    await emit_metabolic_reading(
        lambda_val=0.060,
        entropy=0.128,
        k_cog=0.00377,
        state="transition"
    )

    await emit_resource_map(
        efficiency_index=1.000,
        reuse_ratio=0.039,
        hot_nodes=3
    )

    await emit_phase_transition(
        from_state="stable",
        to_state="transition",
        trigger="entropy_spike"
    )

    # Process events
    print()
    print("Processing events...")

    # Run event loop briefly
    try:
        await asyncio.wait_for(bus.process_events(), timeout=2.0)
    except asyncio.TimeoutError:
        pass

    print()
    print("=" * 70)
    print("Bus test complete")
    print("Check diagnostics/ for event logs")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_bus())
