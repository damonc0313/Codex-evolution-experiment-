"""
Neuro-Symbolic Codex: Dynamic Cognitive Graph with Spreading Activation
========================================================================

This module implements the core cognitive architecture combining:
1. Spreading Activation - Energy propagation through knowledge graphs
2. Hebbian Learning - Synaptic plasticity ("neurons that fire together wire together")
3. Sparse Matrix Operations - Efficient O(E) memory representation
4. Contextual Gating - Dynamic topology based on active context

Mathematical Foundation:
- Activation: x(t+1) = (1-gamma)*x(t) + alpha*(A @ x(t)) + I(t)
- Hebbian Update: delta_w = eta * x_i * x_j * reward
- Oja's Rule: delta_w = eta * x_i * y_j - eta * y_j^2 * w_ij (stable variant)
"""

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
from typing import Dict, List, Optional, Tuple, Set
import networkx as nx


class CognitiveGraph(nx.DiGraph):
    """
    A Dynamic Cognitive Graph that combines symbolic knowledge representation
    with neural-inspired learning and retrieval mechanisms.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adj_matrix: Optional[csr_matrix] = None
        self.node_to_idx: Dict[str, int] = {}
        self.idx_to_node: Dict[int, str] = {}
        self.learning_rate = 0.1
        self.decay_rate = 0.3
        self.activation_threshold = 0.01
        self.spread_alpha = 0.5
        self.active_context: Set[str] = set()
        self._compiled = False

    def compile(self) -> 'CognitiveGraph':
        """Convert NetworkX graph to sparse matrix representation."""
        nodes = list(self.nodes())
        n = len(nodes)
        if n == 0:
            raise ValueError("Cannot compile empty graph")

        self.node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        self.idx_to_node = {idx: node for node, idx in self.node_to_idx.items()}

        lil = lil_matrix((n, n), dtype=np.float32)
        for u, v, data in self.edges(data=True):
            i, j = self.node_to_idx[u], self.node_to_idx[v]
            weight = data.get('weight', 1.0)
            lil[i, j] = weight

        self.adj_matrix = lil.tocsr()
        self._normalize_matrix()
        self._compiled = True
        return self

    def _normalize_matrix(self):
        """Column-normalize adjacency matrix to bound activation energy."""
        if self.adj_matrix is None:
            return
        col_sums = np.array(self.adj_matrix.sum(axis=0)).flatten()
        col_sums[col_sums == 0] = 1.0
        n = self.adj_matrix.shape[0]
        for j in range(n):
            if col_sums[j] > 0:
                col = self.adj_matrix.getcol(j)
                self.adj_matrix[:, j] = col / col_sums[j]

    def propagate(self, seeds: Dict[str, float], steps: int = 10,
                  decay: Optional[float] = None, alpha: Optional[float] = None,
                  threshold: Optional[float] = None, context_mask: Optional[Set[str]] = None) -> Dict[str, float]:
        """Spreading Activation: Propagate energy through the graph."""
        if not self._compiled:
            raise RuntimeError("Graph must be compiled before propagation")

        decay = decay or self.decay_rate
        alpha = alpha or self.spread_alpha
        threshold = threshold or self.activation_threshold
        n = len(self.node_to_idx)

        activations = np.zeros(n, dtype=np.float32)
        for node, energy in seeds.items():
            if node in self.node_to_idx:
                activations[self.node_to_idx[node]] = energy

        if context_mask is not None:
            mask = np.zeros(n, dtype=np.float32)
            for node in context_mask:
                if node in self.node_to_idx:
                    mask[self.node_to_idx[node]] = 1.0
        else:
            mask = np.ones(n, dtype=np.float32)

        A = self.adj_matrix.T

        for _ in range(steps):
            spread = activations @ A
            activations = (1 - decay) * activations + alpha * spread
            activations = activations * mask
            activations[activations < threshold] = 0
            max_act = np.max(activations)
            if max_act > 1.0:
                activations = activations / max_act

        return {self.idx_to_node[i]: float(activations[i]) for i in range(n) if activations[i] > 0}

    def hebbian_update(self, path: List[str], reward: float = 1.0,
                       lr: Optional[float] = None, use_oja: bool = True) -> Dict[Tuple[str, str], float]:
        """Hebbian Learning with Oja's Rule for stability."""
        if not self._compiled:
            raise RuntimeError("Graph must be compiled before learning")

        lr = lr or self.learning_rate
        changes = {}

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if not self.has_edge(u, v):
                self.add_edge(u, v, weight=0.1)

            w = self[u][v]['weight']
            x_u = 1.0 / (i + 1)
            x_v = 1.0 / (i + 2)

            if use_oja:
                delta_w = lr * x_u * x_v * reward - lr * (x_v ** 2) * w
            else:
                delta_w = lr * x_u * x_v * reward

            new_w = max(0.01, min(2.0, w + delta_w))
            self[u][v]['weight'] = new_w

            if u in self.node_to_idx and v in self.node_to_idx:
                i_idx = self.node_to_idx[u]
                j_idx = self.node_to_idx[v]
                self.adj_matrix[i_idx, j_idx] = new_w

            changes[(u, v)] = delta_w

        return changes

    def set_context(self, context_nodes: Set[str]):
        """Set the active context for gated propagation."""
        self.active_context = context_nodes

    def get_strongest_paths(self, source: str, max_depth: int = 3, top_k: int = 5) -> List[Tuple[List[str], float]]:
        """Find strongest activation paths from source node."""
        if source not in self.node_to_idx:
            return []

        paths = [([source], 1.0)]
        completed = []

        for _ in range(max_depth):
            new_paths = []
            for path, score in paths:
                current = path[-1]
                edges = sorted([(v, self[current][v]['weight']) for v in self.successors(current)], key=lambda x: -x[1])[:top_k]
                if not edges:
                    completed.append((path, score))
                else:
                    for next_node, weight in edges:
                        if next_node not in path:
                            new_paths.append((path + [next_node], score * weight))
            paths = sorted(new_paths, key=lambda x: -x[1])[:top_k]

        completed.extend(paths)
        return sorted(completed, key=lambda x: -x[1])[:top_k]


class CognitiveSession:
    """Manages a session of interactions with a CognitiveGraph."""

    def __init__(self, graph: CognitiveGraph):
        self.graph = graph
        self.query_history: List[Dict[str, float]] = []
        self.reinforcement_history: List[Tuple[List[str], float]] = []

    def query(self, seeds: Dict[str, float], steps: int = 10) -> Dict[str, float]:
        """Execute a query and record it."""
        result = self.graph.propagate(seeds, steps)
        self.query_history.append(seeds)
        return result

    def reinforce(self, path: List[str], reward: float = 1.0):
        """Reinforce a path and record it."""
        self.graph.hebbian_update(path, reward)
        self.reinforcement_history.append((path, reward))

    def get_session_stats(self) -> Dict:
        """Return statistics about this session."""
        return {
            'queries': len(self.query_history),
            'reinforcements': len(self.reinforcement_history),
            'total_reward': sum(r for _, r in self.reinforcement_history)
        }
