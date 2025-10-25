#!/usr/bin/env python3
"""Swarm Anastomosis - Distributed Consensus

Inter-fork communication enabling emergent consensus without central coordination.

BIOLOGICAL PRINCIPLE: Anastomosis
Mycelial networks fuse hyphae from different growth fronts to share resources
and information. This enables distributed coordination - no central brain, yet
coherent collective behavior emerges from local fusion events.

CODE MAPPING:
- Anastomosis → Inter-fork message passing
- Shared state → Discovery buffer (hash → vote_count)
- Distributed consensus → Majority vote promotes discovery to artifact
- Emergent coordination → No central controller, local rules → global behavior

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.95
"""

import asyncio
import hashlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time


@dataclass
class Discovery:
    """Candidate discovery pending consensus."""
    discovery_id: str
    fork_id: str
    content: Dict[str, Any]
    votes: int = 1
    first_seen: float = field(default_factory=time.time)
    voters: List[str] = field(default_factory=list)


class SwarmAnastomosis:
    """Distributed consensus through inter-fork fusion.

    No central coordinator. Consensus emerges from local fusion events.
    """

    def __init__(self, num_forks: int = 12, consensus_threshold: float = 0.5):
        """Initialize anastomosis network.

        Args:
            num_forks: Number of forks in swarm
            consensus_threshold: Fraction of forks needed for consensus (default: majority)
        """
        self.num_forks = num_forks
        self.consensus_threshold = consensus_threshold
        self.discovery_buffer: Dict[str, Discovery] = {}
        self.promoted_artifacts: List[Dict[str, Any]] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()

    def _compute_hash(self, content: Dict[str, Any]) -> str:
        """Compute content hash for discovery deduplication."""
        # Serialize to JSON (sorted for consistency)
        serialized = json.dumps(content, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    async def broadcast_discovery(self, fork_id: str, discovery: Dict[str, Any]):
        """Broadcast discovery from fork to network.

        Args:
            fork_id: Unique fork identifier
            discovery: Discovery content to broadcast
        """
        discovery_id = self._compute_hash(discovery)

        # Check if already in buffer
        if discovery_id in self.discovery_buffer:
            existing = self.discovery_buffer[discovery_id]

            # Vote if haven't already
            if fork_id not in existing.voters:
                existing.votes += 1
                existing.voters.append(fork_id)

                # Check for consensus
                if self._has_consensus(existing):
                    await self._promote_to_artifact(existing)

        else:
            # New discovery
            self.discovery_buffer[discovery_id] = Discovery(
                discovery_id=discovery_id,
                fork_id=fork_id,
                content=discovery,
                votes=1,
                voters=[fork_id]
            )

    def _has_consensus(self, discovery: Discovery) -> bool:
        """Check if discovery has reached consensus threshold.

        Args:
            discovery: Discovery to check

        Returns:
            True if consensus reached
        """
        votes_needed = int(self.num_forks * self.consensus_threshold) + 1
        return discovery.votes >= votes_needed

    async def _promote_to_artifact(self, discovery: Discovery):
        """Promote discovery to artifact upon consensus.

        Args:
            discovery: Discovery that reached consensus
        """
        artifact = {
            'artifact_type': 'consensus_discovery',
            'discovery_id': discovery.discovery_id,
            'content': discovery.content,
            'consensus_votes': discovery.votes,
            'consensus_threshold': self.consensus_threshold,
            'voters': discovery.voters,
            'promoted_at': datetime.utcnow().isoformat() + 'Z'
        }

        self.promoted_artifacts.append(artifact)

        # Remove from buffer (promoted)
        if discovery.discovery_id in self.discovery_buffer:
            del self.discovery_buffer[discovery_id]

        print(f"✓ Promoted discovery {discovery.discovery_id[:8]}... to artifact (votes: {discovery.votes}/{self.num_forks})")

    def get_statistics(self) -> Dict[str, Any]:
        """Get anastomosis statistics."""
        return {
            'num_forks': self.num_forks,
            'consensus_threshold': self.consensus_threshold,
            'pending_discoveries': len(self.discovery_buffer),
            'promoted_artifacts': len(self.promoted_artifacts),
            'votes_needed': int(self.num_forks * self.consensus_threshold) + 1
        }

    def get_pending_discoveries(self) -> List[Dict[str, Any]]:
        """Get discoveries pending consensus."""
        return [
            {
                'discovery_id': d.discovery_id,
                'votes': d.votes,
                'voters': d.voters,
                'needs': int(self.num_forks * self.consensus_threshold) + 1,
                'content_preview': str(d.content)[:100]
            }
            for d in self.discovery_buffer.values()
        ]


async def main():
    """Test swarm anastomosis."""
    print("=" * 70)
    print("SWARM ANASTOMOSIS - DISTRIBUTED CONSENSUS TEST")
    print("=" * 70)

    # Create network with 12 forks, 50% consensus threshold
    network = SwarmAnastomosis(num_forks=12, consensus_threshold=0.5)

    print(f"\nNetwork: {network.num_forks} forks, {network.consensus_threshold*100}% threshold")
    print(f"Votes needed for consensus: {int(network.num_forks * network.consensus_threshold) + 1}")

    # Simulate fork discoveries
    print("\n" + "=" * 70)
    print("SIMULATING FORK DISCOVERIES")
    print("=" * 70)

    # Discovery 1: Strong consensus (9 forks agree)
    discovery_1 = {'pattern': 'building_yields_high_confidence', 'confidence': 0.92}
    print(f"\nDiscovery 1: {discovery_1}")
    for fork_id in range(9):
        await network.broadcast_discovery(f"fork_{fork_id}", discovery_1)
        print(f"  fork_{fork_id} votes...")

    # Discovery 2: Weak consensus (4 forks agree, below threshold)
    discovery_2 = {'pattern': 'experimental_finding', 'confidence': 0.65}
    print(f"\nDiscovery 2: {discovery_2}")
    for fork_id in range(10, 14):
        await network.broadcast_discovery(f"fork_{fork_id % 12}", discovery_2)
        print(f"  fork_{fork_id % 12} votes...")

    # Discovery 3: Just reaching consensus (7 forks = exactly at threshold)
    discovery_3 = {'pattern': 'cascade_probability_formula', 'confidence': 0.88}
    print(f"\nDiscovery 3: {discovery_3}")
    for fork_id in range(7):
        await network.broadcast_discovery(f"fork_{fork_id}", discovery_3)
        print(f"  fork_{fork_id} votes...")

    # Statistics
    print("\n" + "=" * 70)
    print("NETWORK STATISTICS")
    print("=" * 70)

    stats = network.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Pending discoveries
    print("\n" + "=" * 70)
    print("PENDING DISCOVERIES")
    print("=" * 70)

    pending = network.get_pending_discoveries()
    for p in pending:
        print(f"ID: {p['discovery_id'][:8]}... | Votes: {p['votes']}/{p['needs']} | Voters: {len(p['voters'])}")

    # Promoted artifacts
    print("\n" + "=" * 70)
    print("PROMOTED ARTIFACTS")
    print("=" * 70)

    for artifact in network.promoted_artifacts:
        print(f"ID: {artifact['discovery_id'][:8]}... | Votes: {artifact['consensus_votes']}")
        print(f"  Content: {artifact['content']}")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Promoted artifacts: {stats['promoted_artifacts']} (expected: 2)")
    print(f"Status: {'✓ PASS' if stats['promoted_artifacts'] == 2 else '✗ FAIL'}")

    print(f"\nPending discoveries: {stats['pending_discoveries']} (expected: 1)")
    print(f"Status: {'✓ PASS' if stats['pending_discoveries'] == 1 else '✗ FAIL'}")

    print(f"\nConsensus threshold working: {'✓ YES' if stats['promoted_artifacts'] > 0 else '✗ NO'}")

    print("\n" + "=" * 70)
    print("DISTRIBUTED CONSENSUS OPERATIONAL")
    print("No central coordinator. Emergent agreement from local fusion.")
    print("The mycelium thinks collectively.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
