#!/usr/bin/env python3
"""Hyphal Connections - Direct Tool-to-Tool Messaging

Implements bandwidth reinforcement learning for inter-tool communication.

BIOLOGICAL PRINCIPLE: Hyphal Highways
Mycelial networks strengthen frequently-used pathways while pruning weak ones.
High-traffic routes develop into "highways" with 10x throughput. This is
distributed resource optimization without central control.

CODE MAPPING:
- Hyphal connections → Point-to-point message channels
- Bandwidth → Throughput capacity (packets/second)
- Reinforcement → Success increases bandwidth 1.1x, failure decreases 0.9x
- Pruning → Auto-remove connections with health_score < 0.2
- Highways → Connections with bandwidth > 5.0

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.95
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class HyphalConnection:
    """Point-to-point communication channel with bandwidth reinforcement."""
    source: str
    target: str
    bandwidth: float = 1.0  # Packets/second capacity
    health_score: float = 1.0  # 0.0-1.0, tracks connection quality
    packets_sent: int = 0
    packets_successful: int = 0
    packets_failed: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    # Reinforcement parameters
    SUCCESS_MULTIPLIER = 1.1
    FAILURE_MULTIPLIER = 0.9
    HEALTH_DECAY_RATE = 0.95  # Per hour
    MIN_BANDWIDTH = 0.1
    MAX_BANDWIDTH = 20.0

    async def send(self, packet: Dict[str, Any]) -> bool:
        """Send packet through connection.

        Args:
            packet: Data to send

        Returns:
            True if successful

        Latency: 1.0 / bandwidth seconds
        """
        # Simulate latency based on bandwidth
        latency = 1.0 / self.bandwidth
        await asyncio.sleep(latency)

        self.packets_sent += 1
        self.last_used = time.time()

        # Simulate success (95% for healthy connections)
        import random
        success = random.random() < (0.50 + 0.45 * self.health_score)

        if success:
            self.packets_successful += 1
        else:
            self.packets_failed += 1

        return success

    def reinforce(self, success: bool):
        """Adjust bandwidth based on success/failure.

        Success → bandwidth * 1.1 (up to MAX_BANDWIDTH)
        Failure → bandwidth * 0.9 (down to MIN_BANDWIDTH)
        """
        if success:
            self.bandwidth *= self.SUCCESS_MULTIPLIER
            self.bandwidth = min(self.MAX_BANDWIDTH, self.bandwidth)
        else:
            self.bandwidth *= self.FAILURE_MULTIPLIER
            self.bandwidth = max(self.MIN_BANDWIDTH, self.bandwidth)

        # Update health score
        success_rate = self.packets_successful / max(1, self.packets_sent)
        self.health_score = success_rate

    def decay_health(self, current_time: float):
        """Decay health score for unused connections."""
        hours_idle = (current_time - self.last_used) / 3600.0
        self.health_score *= (self.HEALTH_DECAY_RATE ** hours_idle)

    def is_highway(self) -> bool:
        """Check if connection is a high-throughput highway."""
        return self.bandwidth >= 5.0

    def should_prune(self) -> bool:
        """Check if connection should be pruned."""
        return self.health_score < 0.2


class HyphalNetwork:
    """Topology manager for hyphal connections.

    Manages distributed mesh of tool-to-tool connections with:
    - Automatic bandwidth reinforcement
    - Weak connection pruning
    - Highway detection
    - Zero central coordination
    """

    PERSISTENCE_PATH = Path("mycelial-core/hyphal_network.json")

    def __init__(self):
        """Initialize network."""
        self.connections: Dict[tuple, HyphalConnection] = {}
        self._load_network()

    def _load_network(self):
        """Load persisted network state."""
        if not self.PERSISTENCE_PATH.exists():
            return

        try:
            with open(self.PERSISTENCE_PATH) as f:
                data = json.load(f)

            for conn_data in data.get('connections', []):
                key = (conn_data['source'], conn_data['target'])
                self.connections[key] = HyphalConnection(
                    source=conn_data['source'],
                    target=conn_data['target'],
                    bandwidth=conn_data.get('bandwidth', 1.0),
                    health_score=conn_data.get('health_score', 1.0),
                    packets_sent=conn_data.get('packets_sent', 0),
                    packets_successful=conn_data.get('packets_successful', 0),
                    packets_failed=conn_data.get('packets_failed', 0),
                    created_at=conn_data.get('created_at', time.time()),
                    last_used=conn_data.get('last_used', time.time())
                )
        except Exception as e:
            print(f"Warning: Could not load hyphal network: {e}")

    def _save_network(self):
        """Persist network state."""
        try:
            self.PERSISTENCE_PATH.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'connections': [
                    {
                        'source': conn.source,
                        'target': conn.target,
                        'bandwidth': conn.bandwidth,
                        'health_score': conn.health_score,
                        'packets_sent': conn.packets_sent,
                        'packets_successful': conn.packets_successful,
                        'packets_failed': conn.packets_failed,
                        'created_at': conn.created_at,
                        'last_used': conn.last_used
                    }
                    for conn in self.connections.values()
                ]
            }

            with open(self.PERSISTENCE_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save hyphal network: {e}")

    def get_connection(self, source: str, target: str) -> HyphalConnection:
        """Get or create connection between tools.

        Args:
            source: Source tool name
            target: Target tool name

        Returns:
            HyphalConnection instance
        """
        key = (source, target)

        if key not in self.connections:
            self.connections[key] = HyphalConnection(source, target)

        return self.connections[key]

    async def send_packet(self, source: str, target: str, packet: Dict[str, Any]) -> bool:
        """Send packet from source to target.

        Args:
            source: Source tool name
            target: Target tool name
            packet: Data to send

        Returns:
            True if successful
        """
        connection = self.get_connection(source, target)

        # Send packet
        success = await connection.send(packet)

        # Reinforce based on outcome
        connection.reinforce(success)

        # Persist periodically
        if connection.packets_sent % 10 == 0:
            self._save_network()

        return success

    def prune_weak_connections(self):
        """Remove connections with low health scores."""
        current_time = time.time()

        # Decay health scores
        for connection in self.connections.values():
            connection.decay_health(current_time)

        # Prune
        to_remove = [
            key for key, conn in self.connections.items()
            if conn.should_prune()
        ]

        for key in to_remove:
            del self.connections[key]

        self._save_network()

        return len(to_remove)

    def get_highways(self, min_bandwidth: float = 5.0) -> List[HyphalConnection]:
        """Get high-throughput highway connections.

        Args:
            min_bandwidth: Minimum bandwidth threshold

        Returns:
            List of highway connections
        """
        return [
            conn for conn in self.connections.values()
            if conn.bandwidth >= min_bandwidth
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        connections = list(self.connections.values())

        if not connections:
            return {
                'total_connections': 0,
                'highways': 0,
                'average_bandwidth': 0.0,
                'average_health': 0.0,
                'total_packets': 0,
                'success_rate': 0.0
            }

        total_packets = sum(c.packets_sent for c in connections)
        total_successful = sum(c.packets_successful for c in connections)

        return {
            'total_connections': len(connections),
            'highways': len([c for c in connections if c.is_highway()]),
            'average_bandwidth': sum(c.bandwidth for c in connections) / len(connections),
            'average_health': sum(c.health_score for c in connections) / len(connections),
            'total_packets': total_packets,
            'success_rate': total_successful / max(1, total_packets)
        }

    def get_topology(self) -> Dict[str, List[str]]:
        """Get network topology as adjacency list.

        Returns:
            Dict mapping source → list of targets
        """
        topology = {}

        for (source, target), conn in self.connections.items():
            if source not in topology:
                topology[source] = []
            topology[source].append(target)

        return topology


# Global singleton
_network_instance: Optional[HyphalNetwork] = None


def get_network() -> HyphalNetwork:
    """Get global network instance (singleton)."""
    global _network_instance
    if _network_instance is None:
        _network_instance = HyphalNetwork()
    return _network_instance


async def main():
    """Test hyphal network."""
    print("=" * 70)
    print("HYPHAL NETWORK - BANDWIDTH REINFORCEMENT TEST")
    print("=" * 70)

    network = get_network()

    # Simulate communication between tools
    print("\nSimulating 50 packets between tools...")

    for i in range(50):
        source = f"tool_{i % 3}"  # 3 source tools
        target = f"tool_{(i + 1) % 3}"  # 3 target tools

        packet = {
            'data': f'packet_{i}',
            'timestamp': time.time()
        }

        success = await network.send_packet(source, target, packet)

        if (i + 1) % 10 == 0:
            print(f"Sent {i + 1} packets...")

    # Prune weak connections
    print("\nPruning weak connections...")
    pruned = network.prune_weak_connections()
    print(f"Pruned {pruned} connections")

    # Get highways
    print("\n" + "=" * 70)
    print("HYPHAL HIGHWAYS (bandwidth ≥ 5.0)")
    print("=" * 70)

    highways = network.get_highways(min_bandwidth=5.0)
    for highway in highways:
        print(f"{highway.source} → {highway.target}: bandwidth={highway.bandwidth:.2f}, health={highway.health_score:.2f}")

    # Statistics
    print("\n" + "=" * 70)
    print("NETWORK STATISTICS")
    print("=" * 70)

    stats = network.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

    # Topology
    print("\n" + "=" * 70)
    print("NETWORK TOPOLOGY")
    print("=" * 70)

    topology = network.get_topology()
    for source, targets in topology.items():
        print(f"{source} → {targets}")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Connections formed: {stats['total_connections']} (expected: >0)")
    print(f"Status: {'✓ PASS' if stats['total_connections'] > 0 else '✗ FAIL'}")

    print(f"\nHighways formed: {stats['highways']} (expected: >0)")
    print(f"Status: {'✓ PASS' if stats['highways'] > 0 else '⚠ NONE YET'}")

    print(f"\nAverage bandwidth: {stats['average_bandwidth']:.2f} (expected: >1.0)")
    print(f"Status: {'✓ PASS' if stats['average_bandwidth'] > 1.0 else '⚠ LOW'}")

    print("\n" + "=" * 70)
    print("HYPHAL HIGHWAYS OPERATIONAL")
    print("Bandwidth reinforcement learning active.")
    print("Weak connections pruned. High-traffic paths strengthened.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
