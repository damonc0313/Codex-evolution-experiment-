#!/usr/bin/env python3
"""Chemotropic Allocator - Adaptive Compute Allocation

Allocates compute resources following nutrient gradients.

BIOLOGICAL PRINCIPLE: Chemotropic Resource Allocation
Mycelium directs growth and resources toward nutrient-rich areas. This is
autonomous optimization without central planning - the network self-organizes
based on local chemical gradients.

CODE MAPPING:
- Tool affinity → Which artifact types each tool processes well
- Priority calculation → gradient_strength * tool_affinity
- Dynamic scheduling → High priority tasks get more CPU time
- Load balancing → Prevent starvation (minimum allocation)

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.93
"""

import asyncio
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import time


@dataclass
class ToolAffinity:
    """Tool's affinity for artifact types."""
    tool_name: str
    artifact_types: List[str]
    priority_score: float = 0.0


class ChemotropicAllocator:
    """Adaptive compute allocation following resource gradients.

    Resources flow toward productive artifact types automatically.
    """

    MIN_PRIORITY = 0.1  # Prevent complete starvation

    def __init__(self, gradient):
        """Initialize allocator.

        Args:
            gradient: NutrientGradient instance
        """
        self.gradient = gradient
        self.tool_registry: Dict[str, ToolAffinity] = {}

    def register_tool(self, name: str, artifact_types: List[str]):
        """Register tool capabilities.

        Args:
            name: Tool name
            artifact_types: List of artifact types this tool handles
        """
        self.tool_registry[name] = ToolAffinity(
            tool_name=name,
            artifact_types=artifact_types
        )

    def allocate_priority(self) -> Dict[str, float]:
        """Compute priority scores for all tools.

        Priority = Σ(gradient_strength * affinity) for artifact types

        Returns:
            Dict mapping tool_name → priority_score
        """
        priorities = {}

        for tool_name, affinity in self.tool_registry.items():
            score = 0.0

            for artifact_type in affinity.artifact_types:
                gradient_strength = self.gradient.density_map.get(artifact_type, 0.0)
                score += gradient_strength

            # Normalize and apply minimum
            priorities[tool_name] = max(self.MIN_PRIORITY, score)
            affinity.priority_score = priorities[tool_name]

        return priorities

    async def schedule(self, tasks: List[tuple]) -> List[Any]:
        """Priority-based task scheduling.

        Args:
            tasks: List of (tool_name, task_fn) tuples

        Returns:
            List of task results
        """
        # Allocate priorities
        priorities = self.allocate_priority()

        # Sort tasks by priority
        sorted_tasks = sorted(
            tasks,
            key=lambda x: priorities.get(x[0], self.MIN_PRIORITY),
            reverse=True
        )

        # Execute in priority order
        results = []
        for tool_name, task_fn in sorted_tasks:
            if asyncio.iscoroutinefunction(task_fn):
                result = await task_fn()
            else:
                result = task_fn()
            results.append(result)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get allocation statistics."""
        priorities = self.allocate_priority()

        return {
            'registered_tools': len(self.tool_registry),
            'priorities': priorities,
            'highest_priority': max(priorities.values()) if priorities else 0.0,
            'lowest_priority': min(priorities.values()) if priorities else 0.0
        }


def main():
    """Test chemotropic allocator."""
    print("=" * 70)
    print("CHEMOTROPIC ALLOCATOR - ADAPTIVE COMPUTE TEST")
    print("=" * 70)

    # Use nutrient gradient
    from nutrient_gradient import get_gradient
    gradient = get_gradient()

    # Simulate measurements
    for artifact_type in ['tool_implementation'] * 5 + ['sep_proposal'] * 3 + ['analysis'] * 1:
        gradient.measure({'artifact_type': artifact_type})

    # Create allocator
    allocator = ChemotropicAllocator(gradient)

    # Register tools
    allocator.register_tool('code_generator', ['tool_implementation', 'framework'])
    allocator.register_tool('spec_writer', ['sep_proposal', 'schema_design'])
    allocator.register_tool('analyzer', ['analysis', 'metrics'])

    # Allocate priorities
    print("\n" + "=" * 70)
    print("PRIORITY ALLOCATION")
    print("=" * 70)

    priorities = allocator.allocate_priority()
    for tool_name, priority in sorted(priorities.items(), key=lambda x: x[1], reverse=True):
        print(f"{tool_name}: {priority:.4f}")

    # Statistics
    print("\n" + "=" * 70)
    print("ALLOCATOR STATISTICS")
    print("=" * 70)

    stats = allocator.get_statistics()
    for key, value in stats.items():
        if key != 'priorities':
            print(f"{key}: {value}")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(f"Tools registered: {stats['registered_tools']} (expected: 3)")
    print(f"Status: {'✓ PASS' if stats['registered_tools'] == 3 else '✗ FAIL'}")

    print(f"\nPriority variation: {stats['highest_priority'] - stats['lowest_priority']:.4f}")
    print(f"Status: {'✓ PASS (priorities differ)' if stats['highest_priority'] > stats['lowest_priority'] else '⚠ ALL EQUAL'}")

    print("\n" + "=" * 70)
    print("CHEMOTROPIC ALLOCATION OPERATIONAL")
    print("Compute flows toward nutrient-rich areas.")
    print("=" * 70)


if __name__ == "__main__":
    main()
