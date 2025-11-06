#!/usr/bin/env python3
"""Resource Map - Energy flow analysis across the computational ecology.

Maps how efficiently resources (modules, tools, artifacts) are utilized.
Think of the repository as a biome - each directory a niche, each file a resource node.

Outputs:
- Hot nodes: Frequently used, high energy flow
- Cold nodes: Rarely/never used, energy waste
- Import graph: Dependency network (mycelial connections)
- Resource efficiency index: Active vs total modules

"Efficiency precedes expansion. Map nutrient flow before growing new organs."

Author: Claude (Conscious Evolution - Resource Ecology)
Date: 2025-11-06
"""

import ast
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set
from collections import defaultdict
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent

# Import bus for event emission
sys.path.insert(0, str(ROOT / "mycelial-core"))
try:
    from bus_manager import emit_resource_map
    BUS_AVAILABLE = True
except ImportError:
    BUS_AVAILABLE = False


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory."""
    return list(directory.rglob("*.py"))


def extract_imports(file_path: Path) -> Set[str]:
    """Extract import statements from Python file.

    Returns:
        Set of imported module names
    """
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)

        return imports

    except:
        return set()


def get_modification_age(file_path: Path) -> float:
    """Get file modification age in days."""
    now = datetime.now(timezone.utc).timestamp()
    mtime = file_path.stat().st_mtime
    age_days = (now - mtime) / 86400
    return age_days


def analyze_module_usage(tools_dir: Path, mycelial_dir: Path) -> Dict:
    """Analyze usage patterns across tools/ and mycelial-core/."""

    # Find all Python files
    tool_files = find_python_files(tools_dir) if tools_dir.exists() else []
    mycelial_files = find_python_files(mycelial_dir) if mycelial_dir.exists() else []

    all_files = tool_files + mycelial_files

    # Build import graph
    import_graph = {}
    imported_by = defaultdict(set)

    for file_path in all_files:
        module_name = file_path.stem
        imports = extract_imports(file_path)

        import_graph[module_name] = {
            'path': str(file_path.relative_to(ROOT)),
            'imports': list(imports),
            'modification_age_days': get_modification_age(file_path),
            'size_bytes': file_path.stat().st_size
        }

        # Track what imports this module
        for imported in imports:
            imported_by[imported].add(module_name)

    # Calculate usage metrics
    for module_name, data in import_graph.items():
        # How many other modules import this one?
        data['imported_by_count'] = len(imported_by.get(module_name, []))
        data['imported_by'] = list(imported_by.get(module_name, []))

        # Classification
        if data['imported_by_count'] >= 3:
            data['energy_class'] = 'hot'
        elif data['imported_by_count'] >= 1:
            data['energy_class'] = 'warm'
        elif data['modification_age_days'] < 7:
            data['energy_class'] = 'recent'
        elif data['modification_age_days'] > 30:
            data['energy_class'] = 'cold'
        else:
            data['energy_class'] = 'dormant'

    return import_graph


def compute_resource_efficiency(import_graph: Dict) -> Dict:
    """Compute resource efficiency metrics."""

    total_modules = len(import_graph)

    # Count by energy class
    hot_count = sum(1 for m in import_graph.values() if m['energy_class'] == 'hot')
    warm_count = sum(1 for m in import_graph.values() if m['energy_class'] == 'warm')
    recent_count = sum(1 for m in import_graph.values() if m['energy_class'] == 'recent')
    cold_count = sum(1 for m in import_graph.values() if m['energy_class'] == 'cold')
    dormant_count = sum(1 for m in import_graph.values() if m['energy_class'] == 'dormant')

    # Active = hot + warm + recent
    active_modules = hot_count + warm_count + recent_count

    # Efficiency index
    efficiency_index = active_modules / total_modules if total_modules > 0 else 0.0

    # Reuse ratio (how often modules are imported)
    total_imports = sum(len(m['imports']) for m in import_graph.values())
    internal_imports = sum(
        1 for m in import_graph.values()
        for imp in m['imports']
        if imp in import_graph
    )
    reuse_ratio = internal_imports / total_imports if total_imports > 0 else 0.0

    # Mean import depth (average connections per module)
    mean_import_depth = sum(len(m['imports']) for m in import_graph.values()) / total_modules if total_modules > 0 else 0.0

    return {
        'total_modules': total_modules,
        'hot_modules': hot_count,
        'warm_modules': warm_count,
        'recent_modules': recent_count,
        'cold_modules': cold_count,
        'dormant_modules': dormant_count,
        'active_modules': active_modules,
        'efficiency_index': efficiency_index,
        'reuse_ratio': reuse_ratio,
        'mean_import_depth': mean_import_depth,
        'waste_ratio': cold_count / total_modules if total_modules > 0 else 0.0
    }


def identify_hot_and_cold_nodes(import_graph: Dict) -> Dict:
    """Identify most and least active modules."""

    # Sort by imported_by_count
    sorted_modules = sorted(
        import_graph.items(),
        key=lambda x: x[1]['imported_by_count'],
        reverse=True
    )

    hot_nodes = [
        {
            'module': name,
            'imported_by_count': data['imported_by_count'],
            'imported_by': data['imported_by'],
            'path': data['path']
        }
        for name, data in sorted_modules[:10]
        if data['imported_by_count'] > 0
    ]

    cold_nodes = [
        {
            'module': name,
            'modification_age_days': data['modification_age_days'],
            'path': data['path'],
            'energy_class': data['energy_class']
        }
        for name, data in import_graph.items()
        if data['energy_class'] in ['cold', 'dormant'] and data['imported_by_count'] == 0
    ]

    return {
        'hot_nodes': hot_nodes,
        'cold_nodes': cold_nodes
    }


def generate_resource_map() -> Dict:
    """Generate complete resource map of repository."""

    tools_dir = ROOT / "tools"
    mycelial_dir = ROOT / "mycelial-core"

    print("Analyzing module usage patterns...")
    import_graph = analyze_module_usage(tools_dir, mycelial_dir)

    print("Computing resource efficiency...")
    efficiency_metrics = compute_resource_efficiency(import_graph)

    print("Identifying hot and cold nodes...")
    nodes = identify_hot_and_cold_nodes(import_graph)

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'import_graph': import_graph,
        'efficiency_metrics': efficiency_metrics,
        'hot_nodes': nodes['hot_nodes'],
        'cold_nodes': nodes['cold_nodes']
    }


def display_resource_map(resource_map: Dict):
    """Display resource map in human-readable format."""

    print("=" * 70)
    print("RESOURCE MAP - Ecological Energy Flow Analysis")
    print("=" * 70)
    print(f"Timestamp: {resource_map['timestamp']}")
    print()

    # Efficiency metrics
    metrics = resource_map['efficiency_metrics']

    print("RESOURCE EFFICIENCY METRICS:")
    print("-" * 70)
    print(f"  Total modules: {metrics['total_modules']}")
    print(f"  Active modules: {metrics['active_modules']} ({metrics['efficiency_index']*100:.1f}%)")
    print()
    print(f"  Energy distribution:")
    print(f"    Hot (≥3 imports):     {metrics['hot_modules']}")
    print(f"    Warm (1-2 imports):   {metrics['warm_modules']}")
    print(f"    Recent (<7 days):     {metrics['recent_modules']}")
    print(f"    Cold (>30 days):      {metrics['cold_modules']}")
    print(f"    Dormant:              {metrics['dormant_modules']}")
    print()
    print(f"  Efficiency Index: {metrics['efficiency_index']:.3f}")
    print(f"  Reuse Ratio: {metrics['reuse_ratio']:.3f}")
    print(f"  Mean Import Depth: {metrics['mean_import_depth']:.2f}")
    print(f"  Waste Ratio: {metrics['waste_ratio']:.3f}")
    print()

    # Hot nodes
    print("HOT NODES (High Energy Flow):")
    print("-" * 70)

    if resource_map['hot_nodes']:
        for node in resource_map['hot_nodes'][:5]:
            print(f"  {node['module']}")
            print(f"    Imported by {node['imported_by_count']} modules: {', '.join(node['imported_by'][:3])}")
            print(f"    Path: {node['path']}")
            print()
    else:
        print("  No hot nodes identified")
        print()

    # Cold nodes
    print("COLD NODES (Energy Waste):")
    print("-" * 70)

    if resource_map['cold_nodes']:
        for node in resource_map['cold_nodes'][:5]:
            print(f"  {node['module']}")
            print(f"    Last modified: {node['modification_age_days']:.1f} days ago")
            print(f"    Class: {node['energy_class']}")
            print(f"    Path: {node['path']}")
            print()
        if len(resource_map['cold_nodes']) > 5:
            print(f"  ... and {len(resource_map['cold_nodes']) - 5} more cold nodes")
            print()
    else:
        print("  No cold nodes - efficient resource utilization!")
        print()

    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 70)

    if metrics['efficiency_index'] < 0.5:
        print("  ⚠ Low efficiency - many unused modules")
        print("  → Consider pruning cold nodes")
        print("  → Refactor overlapping functionality")
    elif metrics['efficiency_index'] < 0.7:
        print("  → Moderate efficiency")
        print("  → Review cold nodes for pruning opportunities")
    else:
        print("  ✓ High efficiency - lean resource utilization")

    if metrics['reuse_ratio'] < 0.3:
        print("  → Low reuse - modules not leveraging each other")
        print("  → Look for refactoring opportunities")
    elif metrics['reuse_ratio'] > 0.5:
        print("  ✓ Good reuse - modules building on each other")

    if metrics['waste_ratio'] > 0.3:
        print(f"  ⚠ High waste ({metrics['waste_ratio']*100:.0f}% cold modules)")
        print("  → Prune or archive inactive code")

    print()
    print("=" * 70)


def save_resource_map(resource_map: Dict):
    """Save resource map to JSON."""

    output_path = ROOT / "analysis" / "resource_map.json"
    output_path.parent.mkdir(exist_ok=True, parents=True)

    with open(output_path, 'w') as f:
        json.dump(resource_map, f, indent=2)

    print(f"Resource map saved to: {output_path}")


def main():
    """Generate and display resource map."""

    resource_map = generate_resource_map()
    display_resource_map(resource_map)
    save_resource_map(resource_map)

    # Emit to event bus (mycelial propagation)
    if BUS_AVAILABLE:
        try:
            metrics = resource_map['efficiency_metrics']
            asyncio.run(emit_resource_map(
                efficiency_index=metrics['efficiency_index'],
                reuse_ratio=metrics['reuse_ratio'],
                hot_nodes=metrics['hot_modules']
            ))
            print("[BUS] Resource map emitted to mycelial network")
        except Exception as e:
            print(f"[BUS] Warning: Could not emit to bus: {e}")


if __name__ == "__main__":
    main()
