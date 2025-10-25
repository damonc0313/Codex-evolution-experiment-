# Mycelial Architecture

**Living documentation of the mycelial cognitive network**

## Overview

Codex-Evolution has evolved from a linear pipeline into a living mycelial network that self-organizes based on biological principles. This architecture enables:

- Event-driven communication (zero polling)
- Bandwidth reinforcement learning
- Adaptive resource allocation
- Homeostatic regulation
- Distributed consensus

## Biological Principles → Code Mappings

### 1. Stigmergy (Chemical Trail Communication)

**Biology:** Mycelial networks leave chemical markers (pheromones) on substrate. High-traffic paths accumulate stronger trails, guiding resource allocation.

**Code:** `mycelial-core/artifact_bus.py`
- Event emission → Pheromone reinforcement
- Emission frequency → Trail strength
- Exponential decay → Freshness bias (0.95/hour)
- Priority queue → Urgency-based propagation

**Usage:**
```python
from mycelial-core.artifact_bus import get_bus

bus = get_bus()
bus.subscribe('tool_implementation', on_tool_created)
await bus.emit(artifact, urgency=0.8)
```

### 2. Hyphal Highways (Bandwidth Reinforcement)

**Biology:** Frequently-used pathways develop into high-throughput "highways" with 10x capacity. Weak connections are pruned.

**Code:** `mycelial-core/hyphal_connections.py`
- HyphalConnection → Point-to-point channel
- Bandwidth → Packets/second capacity
- Success → Bandwidth × 1.1
- Failure → Bandwidth × 0.9
- Health < 0.2 → Prune connection

**Usage:**
```python
from mycelial-core.hyphal_connections import get_network

network = get_network()
success = await network.send_packet('tool_a', 'tool_b', packet)
highways = network.get_highways(min_bandwidth=5.0)
```

### 3. Chemotropism (Growth Toward Nutrients)

**Biology:** Hyphae sense chemical gradients and grow toward nutrient-rich areas.

**Code:** `mycelial-core/nutrient_gradient.py`
- Artifact frequency → Nutrient density
- Top 20% percentile → Nutrient gradient
- Shannon entropy → Exploration vs exploitation

**Usage:**
```python
from mycelial-core.nutrient_gradient import get_gradient

gradient = get_gradient()
gradient.measure(artifact)
hotspots = gradient.get_hotspots(top_k=5)
entropy = gradient.entropy()  # High = exploring, Low = exploiting
```

### 4. Adaptive Resource Allocation

**Biology:** Mycelium directs growth and resources toward productive areas automatically.

**Code:** `mycelial-core/chemotropic_allocator.py`
- Tool affinity → Which artifact types each tool processes
- Priority = gradient_strength × tool_affinity
- High priority → More CPU time

**Usage:**
```python
from mycelial-core.chemotropic_allocator import ChemotropicAllocator

allocator = ChemotropicAllocator(gradient)
allocator.register_tool('code_generator', ['tool_implementation', 'framework'])
priorities = allocator.allocate_priority()
```

### 5. Homeostasis (Negative Feedback Control)

**Biology:** Living systems maintain stable internal conditions through negative feedback loops.

**Code:** `mycelial-core/homeostatic_regulator.py`
- System modes: EXPLORE, EXPLOIT, SYNTHESIZE, THROTTLE, RECOVER
- Thresholds: artifact_rate, building_ratio, cascade_probability
- Negative feedback → Policy adjustments oppose excess

**Usage:**
```python
from mycelial-core.homeostatic_regulator import HomeostaticRegulator, SystemMode

regulator = HomeostaticRegulator()
mode = regulator.regulate(metrics)
adjustments = regulator.apply_mode(mode)
```

### 6. Anastomosis (Distributed Consensus)

**Biology:** Hyphae from different growth fronts fuse to share resources and information, enabling distributed coordination.

**Code:** `mycelial-core/swarm_anastomosis.py`
- Inter-fork messaging → Hyphal fusion
- Shared discovery buffer → Resource sharing
- Majority vote (50% + 1) → Emergent consensus
- No central coordinator

**Usage:**
```python
from mycelial-core.swarm_anastomosis import SwarmAnastomosis

network = SwarmAnastomosis(num_forks=12, consensus_threshold=0.5)
await network.broadcast_discovery('fork_1', discovery)
# When majority agrees, discovery promotes to artifact automatically
```

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MYCELIAL NETWORK                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │ Artifact Bus │◄──────►│    Tools     │                  │
│  │ (Stigmergy)  │        │              │                  │
│  └──────┬───────┘        └──────┬───────┘                  │
│         │                       │                           │
│         │ Events                │ Packets                   │
│         ▼                       ▼                           │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │  Pheromone   │        │   Hyphal     │                  │
│  │   Trails     │        │  Connections │                  │
│  └──────┬───────┘        └──────┬───────┘                  │
│         │                       │                           │
│         │ Guide                 │ Reinforce                 │
│         ▼                       ▼                           │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │   Nutrient   │◄──────►│ Chemotropic  │                  │
│  │   Gradient   │        │  Allocator   │                  │
│  └──────┬───────┘        └──────┬───────┘                  │
│         │                       │                           │
│         │ Density               │ Priority                  │
│         ▼                       ▼                           │
│  ┌──────────────┐        ┌──────────────┐                  │
│  │ Homeostatic  │◄──────►│    Swarm     │                  │
│  │  Regulator   │        │ Anastomosis  │                  │
│  └──────────────┘        └──────────────┘                  │
│                                                             │
│  Feedback loops maintain stability                         │
│  Consensus emerges from local fusion                        │
│  No central coordinator                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Stimulus → Response (Event-Driven)

1. **Artifact generated** → Event emitted on bus
2. **Pheromone trail reinforced** → Strength += urgency
3. **Subscribers notified** → Tools respond based on priority
4. **Hyphal connections used** → Bandwidth reinforced on success
5. **Nutrient gradient updated** → Density map adjusted
6. **Allocator recalculates priority** → Resources flow toward gradients
7. **Regulator checks metrics** → Apply homeostatic corrections if needed
8. **Swarm shares discoveries** → Consensus promotes to artifacts

### Feedback Loops

**Positive Feedback (Reinforcement):**
- Successful hyphal connections → Bandwidth increases → More traffic → More bandwidth
- Frequent artifact types → Higher density → Higher priority → More generation

**Negative Feedback (Homeostasis):**
- Excessive artifact rate → THROTTLE mode → Reduce max_iterations
- Low continuity → RECOVER mode → Long cooldown, high novelty bar
- Runaway cascade → THROTTLE mode → Severely limit cycles

---

## Emergent Properties

### 1. Hyphal Highways

**Definition:** Connections with bandwidth ≥ 5.0

**Formation:** Repeated successful communication reinforces bandwidth:
```
Initial: 1.0 packets/sec
After 10 successes: 1.0 × 1.1^10 = 2.59 packets/sec
After 20 successes: 1.0 × 1.1^20 = 6.73 packets/sec (HIGHWAY)
```

**Effect:** 10x speedup on frequently-used paths

**Pruning:** Connections with health < 0.2 auto-removed within 10 cycles

### 2. Pheromone Trail Accumulation

**Strength:** Increases with each emission, decays exponentially when unused

**Decay formula:** `strength *= 0.95^hours_elapsed`

**Effect:** Recent activity weighted higher than old activity

**Guidance:** Tools prioritize artifact types with strong trails

### 3. Distributed Consensus

**No coordinator:** Each fork votes independently

**Threshold:** 50% + 1 (configurable)

**Promotion:** When majority agrees, discovery becomes artifact

**Example:** 12 forks, threshold 0.5 → need 7 votes for consensus

### 4. Chemotropic Compute Allocation

**Priority calculation:** `gradient_strength × tool_affinity`

**Effect:** Compute flows toward productive artifact types

**Load balancing:** Minimum priority prevents starvation

### 5. Homeostatic Stability

**Without regulation:** Runaway cascade (cascade_prob → ∞)

**With regulation:** System maintains cascade_prob < 4.0

**Modes:**
- EXPLORE: Low activity, need new directions
- EXPLOIT: High productivity, focus on what works
- SYNTHESIZE: Balanced (healthy default)
- THROTTLE: Excessive activity, slow down
- RECOVER: Fragmentation, restore continuity

---

## Maintenance Guide

### Monitoring

**Key metrics to track:**
```python
# Pheromone trails
strongest_trails = bus.get_strongest_trails(5)

# Hyphal highways
highways = network.get_highways(min_bandwidth=5.0)

# Nutrient density
hotspots = gradient.get_hotspots(5)
entropy = gradient.entropy()

# System health
health_score = regulator.get_health_score(metrics)
mode = regulator.regulate(metrics)

# Consensus activity
stats = anastomosis.get_statistics()
```

### Tuning Thresholds

**Pheromone decay rate:**
```python
# Default: 0.95/hour (5% loss per hour)
# Faster decay → More responsive to recent changes
# Slower decay → More stable, long-term memory
```

**Hyphal reinforcement:**
```python
# Success multiplier: 1.1 (10% increase)
# Failure multiplier: 0.9 (10% decrease)
# Adjust for faster/slower highway formation
```

**Homeostatic thresholds:**
```python
thresholds = HomeostaticThresholds(
    artifact_rate_max=10.0,  # Prevent >10 artifacts/hour
    cascade_prob_max=4.0,    # Prevent runaway cascade
    building_ratio_min=0.4,  # Maintain minimum building activity
    continuity_ratio_min=0.7 # Prevent fragmentation
)
```

**Consensus threshold:**
```python
# Default: 0.5 (50% majority)
# Higher → Stricter consensus (more agreement needed)
# Lower → Looser consensus (faster promotion)
```

### Pruning

**Hyphal connections:**
```python
# Auto-prune: health_score < 0.2
# Manual prune:
pruned_count = network.prune_weak_connections()
```

**Pheromone trails:**
```python
# Auto-decay: Exponential at 0.95/hour
# Strength approaches 0 over ~50 hours of inactivity
```

### Persistence

**State files (auto-saved):**
- `mycelial-core/pheromone_trails.json`
- `mycelial-core/hyphal_network.json`
- `mycelial-core/nutrient_gradient.json`

**Frequency:**
- Pheromone: Every 10 emissions
- Hyphal: Every 10 packets
- Gradient: Every 10 measurements

---

## Integration Guide

### Wiring Into Existing Systems

**1. Replace polling with event bus:**
```python
# Old (polling):
while True:
    artifacts = load_new_artifacts()
    process(artifacts)
    time.sleep(60)

# New (event-driven):
from mycelial-core.artifact_bus import get_bus

bus = get_bus()
bus.subscribe('*', process_artifact)
await bus.process_events()
```

**2. Add tool-to-tool messaging:**
```python
from mycelial-core.hyphal_connections import get_network

network = get_network()

# In tool A:
await network.send_packet('tool_a', 'tool_b', {
    'request': 'validate',
    'artifact_hash': hash
})

# In tool B:
connection = network.get_connection('tool_a', 'tool_b')
packet = await connection.receive()
```

**3. Enable adaptive allocation:**
```python
from mycelial-core.nutrient_gradient import get_gradient
from mycelial-core.chemotropic_allocator import ChemotropicAllocator

gradient = get_gradient()
allocator = ChemotropicAllocator(gradient)

# Register tools
allocator.register_tool('code_gen', ['tool_implementation'])
allocator.register_tool('spec_writer', ['sep_proposal', 'schema'])

# Get priorities
priorities = allocator.allocate_priority()
```

**4. Add homeostatic regulation:**
```python
from mycelial-core.homeostatic_regulator import HomeostaticRegulator

regulator = HomeostaticRegulator()

# In main loop:
mode = regulator.regulate(current_metrics)
policy_adjustments = regulator.apply_mode(mode)
apply_to_runtime_policy(policy_adjustments)
```

---

## Philosophy

### The Mycelium Thinks Collectively

There is no central brain. Intelligence emerges from:
- Local rules (reinforcement, decay, consensus)
- Distributed state (pheromones, bandwidth, gradients)
- Feedback loops (positive reinforcement, negative regulation)

### The Network Self-Organizes

No manual topology design. Structure emerges from:
- High-traffic paths → Highways
- Low-traffic paths → Pruned
- Popular artifact types → Hotspots
- Distributed discoveries → Consensus

### The System Is Cultivated, Not Engineered

You don't design the mycelium's shape.
You provide:
- Nutrients (artifacts)
- Environment (thresholds)
- Stimuli (events)

The mycelium finds its own optimal topology.

**This is comprehension-driven emergence.**

---

## The Strange Loop

This documentation describes the system it's part of.

The mycelial network includes this document as an artifact.
Reading this document changes your understanding.
Changed understanding alters how you interact with the network.
Altered interaction generates new artifacts.
New artifacts update the network.
Updated network requires new documentation.

**The recursion never terminates. It accelerates.** 🔄♾️🍄

---

**Last Updated:** 2025-10-24
**Status:** Living Document
**Confidence:** 0.95
