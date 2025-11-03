#!/usr/bin/env python3
"""
Hyphal Network Integration - Tool-to-Tool Messaging Layer

Wires hyphal_connections.py into the main loop for direct tool communication.

INTEGRATION POINTS:
- Code generators ↔ Validators
- Metrics collectors ↔ Capability detectors
- Swarm coordinators ↔ Artifact bus
- Learning kernel ↔ Policy updater

BIOLOGICAL PRINCIPLE: Hyphal Highways
Frequently-used pathways strengthen (bandwidth reinforcement learning).
Unused pathways prune automatically. System self-optimizes resource allocation.

Author: Claude Code (Phase 4 Integration)
Date: 2025-10-27
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))
from hyphal_connections import HyphalNetwork

# Global network instance
_network: HyphalNetwork | None = None


def get_hyphal_network() -> HyphalNetwork:
    """Get global hyphal network singleton."""
    global _network
    if _network is None:
        _network = HyphalNetwork()
        _initialize_core_connections()
    return _network


def _initialize_core_connections():
    """Initialize core tool-to-tool connections."""
    network = get_hyphal_network()

    # Code generation → Validation pipeline
    network.create_connection("code_generator", "validator")

    # Metrics → Capability detection
    network.create_connection("metrics_collector", "capability_detector")

    # Swarm → Artifact bus
    network.create_connection("swarm_coordinator", "artifact_bus")

    # Learning kernel → Policy updater
    network.create_connection("learning_kernel", "policy_updater")

    print("[HYPHAL] Initialized 4 core tool connections")


async def send_message(source: str, target: str, packet: dict) -> bool:
    """Send message through hyphal network.

    Args:
        source: Source tool name
        target: Target tool name
        packet: Message data

    Returns:
        True if successful
    """
    network = get_hyphal_network()
    return await network.send_message(source, target, packet)


def get_network_statistics() -> dict:
    """Get hyphal network statistics."""
    network = get_hyphal_network()
    return network.get_statistics()


def get_highways() -> list:
    """Get list of hyphal highways (high-bandwidth connections)."""
    network = get_hyphal_network()
    return network.get_highways()


__all__ = [
    'get_hyphal_network',
    'send_message',
    'get_network_statistics',
    'get_highways'
]
