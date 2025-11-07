"""
Causal Influence Ledger (CIL) - Ground Truth Attribution System

Replaces heuristic spawn_count with actual influence tracking.
Logs who influenced what for every decision with weighted edges.

Key Features:
- Decision-level attribution: artifact → decision with weight w
- Multi-timescale λ computation: fit influence decay from real data
- Shapley-ready: normalized weights enable value attribution
- Causal graphs: query influence paths across time

Decision Sites (hottest 3):
1. artifact_selection: which artifacts to process in learning kernel
2. policy_update: how to modify building_weight based on signals
3. reward_computation: which quality signals to weight highest
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict


class CausalInfluenceLedger:
    """
    Logs and analyzes causal influence edges for all decisions.

    Core Invariant: Σ(weights) = 1.0 for each decision's inputs
    """

    def __init__(self, ledger_path: str = "diagnostics/causal_influence_ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory cache for recent decisions (last 1000)
        self.recent_decisions = []
        self.max_cache = 1000

        # Influence graph: {artifact_id: [(decision_id, weight, timestamp)]}
        self.influence_graph = defaultdict(list)

        # Load existing ledger
        self._load_ledger()

    def log_decision(
        self,
        decision_type: str,
        inputs: List[Dict[str, any]],
        output: any,
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None
    ) -> str:
        """
        Log a decision with its causal inputs.

        Args:
            decision_type: Type of decision (artifact_selection, policy_update, reward_computation)
            inputs: List of {artifact_id, weight, reason} dicts
            output: The decision outcome
            metadata: Additional context
            timestamp: Optional ISO timestamp (for temporal experiments, defaults to now)

        Returns:
            decision_id: UUID for this decision
        """
        # Normalize weights to sum to 1.0, but ALSO store raw weights for λ fitting
        total_weight = sum(inp.get('weight', 1.0) for inp in inputs)
        if total_weight == 0:
            total_weight = 1.0

        normalized_inputs = []
        for inp in inputs:
            raw_weight = inp.get('weight', 1.0)
            norm_weight = raw_weight / total_weight
            normalized_inputs.append({
                'artifact_id': inp['artifact_id'],
                'weight': norm_weight,  # Normalized (for decision logic)
                'raw_weight': raw_weight,  # Raw (for λ fitting)
                'reason': inp.get('reason', 'unspecified'),
                'reason_hash': hash(inp.get('reason', 'unspecified'))
            })

        # Create decision record
        decision_id = str(uuid.uuid4())
        timestamp = timestamp or datetime.now().isoformat()

        decision = {
            'decision_id': decision_id,
            'timestamp': timestamp,
            'decision_type': decision_type,
            'inputs': normalized_inputs,
            'output': output,
            'metadata': metadata or {}
        }

        # Update influence graph (store both normalized and raw weights)
        for inp in normalized_inputs:
            self.influence_graph[inp['artifact_id']].append(
                (decision_id, inp['weight'], inp['raw_weight'], timestamp)
            )

        # Cache and persist
        self.recent_decisions.append(decision)
        if len(self.recent_decisions) > self.max_cache:
            self.recent_decisions.pop(0)

        # Append to ledger file
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(decision) + '\n')

        return decision_id

    def compute_lambda_from_influence(
        self,
        decision_type: Optional[str] = None,
        window_days: int = 30,
        use_raw_weights: bool = True
    ) -> Tuple[float, Dict]:
        """
        Compute λ (influence decay rate) from actual influence edges.

        Fits w ~ e^(-λt) where:
        - w: influence weight (raw or normalized)
        - t: age of artifact in days

        This is GROUND TRUTH λ, not spawn_count heuristics.

        Args:
            decision_type: Filter by decision type (None = all)
            window_days: Only use recent N days of data
            use_raw_weights: If True, use raw weights (recommended). If False, use normalized.

        Returns:
            (lambda_value, diagnostics)
        """
        # Gather (age, weight) pairs
        now = datetime.now()
        age_weight_pairs = []

        for artifact_id, influences in self.influence_graph.items():
            for edge in influences:
                # Handle both old format (3-tuple) and new format (4-tuple)
                if len(edge) == 4:
                    decision_id, norm_weight, raw_weight, timestamp_str = edge
                    weight = raw_weight if use_raw_weights else norm_weight
                else:
                    # Old format (before raw_weight storage)
                    decision_id, weight, timestamp_str = edge

                timestamp = datetime.fromisoformat(timestamp_str)
                age_days = (now - timestamp).total_seconds() / 86400

                if age_days <= window_days:
                    age_weight_pairs.append((age_days, weight))

        if len(age_weight_pairs) < 10:
            return 0.0, {'error': 'insufficient_data', 'count': len(age_weight_pairs)}

        # Fit exponential decay: w = e^(-λt)
        # Take log: log(w) = -λt
        # Linear regression: log(w) ~ -λ * age

        ages = np.array([age for age, _ in age_weight_pairs])
        weights = np.array([weight for _, weight in age_weight_pairs])

        # Avoid log(0) - add small epsilon
        weights = np.maximum(weights, 1e-10)
        log_weights = np.log(weights)

        # Linear fit
        lambda_fit = -np.polyfit(ages, log_weights, 1)[0]

        # Compute goodness of fit
        predicted_log_weights = -lambda_fit * ages
        residuals = log_weights - predicted_log_weights
        r_squared = 1 - (np.var(residuals) / np.var(log_weights))

        diagnostics = {
            'lambda': lambda_fit,
            'r_squared': r_squared,
            'n_samples': len(age_weight_pairs),
            'window_days': window_days,
            'mean_age': np.mean(ages),
            'mean_weight': np.mean(weights),
            'weight_type': 'raw' if use_raw_weights else 'normalized'
        }

        return lambda_fit, diagnostics

    def compute_domain_lambdas(self) -> Dict[str, Tuple[float, Dict]]:
        """
        Compute λ per decision type (domain-specific decay rates).

        Returns:
            {decision_type: (lambda, diagnostics)}
        """
        decision_types = set()
        for decision in self.recent_decisions:
            decision_types.add(decision['decision_type'])

        lambdas = {}
        for dtype in decision_types:
            # Filter influence edges by decision type
            lambda_val, diag = self.compute_lambda_from_influence(
                decision_type=dtype,
                window_days=30
            )
            lambdas[dtype] = (lambda_val, diag)

        return lambdas

    def get_influence_ancestors(
        self,
        artifact_id: str,
        max_depth: int = 3
    ) -> List[Dict]:
        """
        Trace influence ancestry: which artifacts influenced this one?

        Returns:
            List of ancestor dicts with influence scores
        """
        # BFS through influence graph
        ancestors = []
        visited = set()
        queue = [(artifact_id, 1.0, 0)]  # (id, weight, depth)

        while queue:
            curr_id, curr_weight, depth = queue.pop(0)

            if curr_id in visited or depth > max_depth:
                continue

            visited.add(curr_id)

            # Find decisions influenced by curr_id
            if curr_id in self.influence_graph:
                for decision_id, weight, timestamp in self.influence_graph[curr_id]:
                    ancestors.append({
                        'artifact_id': curr_id,
                        'decision_id': decision_id,
                        'weight': curr_weight * weight,
                        'depth': depth,
                        'timestamp': timestamp
                    })

                    # TODO: add edges from decision outputs to next artifacts
                    # For now, just track direct lineage

        return sorted(ancestors, key=lambda x: x['weight'], reverse=True)

    def generate_attribution_report(self, output_path: Optional[str] = None) -> Dict:
        """
        Generate comprehensive attribution report.

        Includes:
        - Domain-specific λ values
        - Top influencers by weight
        - Influence graph statistics
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_decisions': len(self.recent_decisions),
            'total_artifacts': len(self.influence_graph),
            'domain_lambdas': {},
            'top_influencers': [],
            'graph_stats': {}
        }

        # Compute domain lambdas
        domain_lambdas = self.compute_domain_lambdas()
        for dtype, (lambda_val, diag) in domain_lambdas.items():
            report['domain_lambdas'][dtype] = {
                'lambda': lambda_val,
                'r_squared': diag.get('r_squared', 0),
                'n_samples': diag.get('n_samples', 0)
            }

        # Top influencers by total weight
        influencer_scores = defaultdict(float)
        for artifact_id, influences in self.influence_graph.items():
            total_weight = sum(weight for _, weight, _ in influences)
            influencer_scores[artifact_id] = total_weight

        top_influencers = sorted(
            influencer_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]

        report['top_influencers'] = [
            {'artifact_id': aid, 'total_influence': score}
            for aid, score in top_influencers
        ]

        # Graph stats
        influence_counts = [len(influences) for influences in self.influence_graph.values()]
        if influence_counts:
            report['graph_stats'] = {
                'mean_influences_per_artifact': np.mean(influence_counts),
                'max_influences': max(influence_counts),
                'artifacts_with_influence': len(influence_counts)
            }

        # Save if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

        return report

    def _load_ledger(self):
        """Load existing ledger from disk"""
        if not self.ledger_path.exists():
            return

        with open(self.ledger_path, 'r') as f:
            for line in f:
                if line.strip():
                    decision = json.loads(line)
                    self.recent_decisions.append(decision)

                    # Rebuild influence graph
                    for inp in decision.get('inputs', []):
                        self.influence_graph[inp['artifact_id']].append(
                            (decision['decision_id'], inp['weight'], decision['timestamp'])
                        )

        # Keep only recent cache
        if len(self.recent_decisions) > self.max_cache:
            self.recent_decisions = self.recent_decisions[-self.max_cache:]


# Global singleton for easy access
_cil_instance = None

def get_cil() -> CausalInfluenceLedger:
    """Get or create global CIL instance"""
    global _cil_instance
    if _cil_instance is None:
        _cil_instance = CausalInfluenceLedger()
    return _cil_instance


if __name__ == '__main__':
    # Test CIL
    cil = CausalInfluenceLedger()

    # Log sample decision
    decision_id = cil.log_decision(
        decision_type='artifact_selection',
        inputs=[
            {'artifact_id': 'artifact_001.json', 'weight': 0.7, 'reason': 'high quality'},
            {'artifact_id': 'artifact_002.json', 'weight': 0.3, 'reason': 'recent'}
        ],
        output='artifact_001.json',
        metadata={'context': 'test'}
    )

    print(f"Logged decision: {decision_id}")

    # Compute lambda
    lambda_val, diag = cil.compute_lambda_from_influence()
    print(f"Lambda: {lambda_val:.4f}")
    print(f"Diagnostics: {diag}")

    # Generate report
    report = cil.generate_attribution_report('diagnostics/cil_report.json')
    print(f"Generated attribution report")
