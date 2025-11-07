"""
Autocurriculum Engine (ACE) - Autonomous Task Selection

Selects next task that maximizes expected information gain and fitness.
Pre-registers predictions, executes, and measures actual outcomes.

Core Formula:
  score(task) = α·Δcoverage + β·E[Δquality] + γ·E[Δreuse] + δ·ΔH_pressure - penalty_risk

Key Features:
- Autonomous task proposal (no human prompt required)
- Pre-registered predictions (testable claims)
- Coverage-driven exploration (hits blind spots)
- Metabolic-aware (pressure-tests ΔH_crit)
- Risk-budgeted (time, tokens, blast radius caps)

Author: Claude Code
Date: 2025-11-07
Purpose: Move from "prompted agent" to "autonomous agent"
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class AutocurriculumEngine:
    """
    Autonomous task selection engine.

    Proposes tasks that maximize expected learning gain.
    """

    def __init__(
        self,
        resource_map_path: str = "mycelial-core/resource_map.json",
        ledger_path: str = "continuity_ledger.jsonl",
        curriculum_log_path: str = "diagnostics/autocurriculum_log.jsonl",
        alpha: float = 0.3,  # Coverage weight
        beta: float = 0.3,   # Quality weight
        gamma: float = 0.2,  # Reuse weight
        delta: float = 0.2   # Entropy pressure weight
    ):
        self.resource_map_path = Path(resource_map_path)
        self.ledger_path = Path(ledger_path)
        self.curriculum_log_path = Path(curriculum_log_path)
        self.curriculum_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Scoring weights (must sum to ~1.0)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta

        # Task history
        self.proposed_tasks = []
        self.completed_tasks = []

        # Coverage tracker: {domain: num_tasks}
        self.coverage_map = defaultdict(int)

        # Load existing coverage from ledger
        self._load_coverage()

    def score_task(self, task: Dict) -> float:
        """
        Score task by expected info gain + fitness improvement.

        Args:
            task: Task dict with 'domain', 'complexity', 'risk', etc.

        Returns:
            score: Higher = more valuable
        """
        # Component 1: Coverage gain (favor unexplored domains)
        domain = task.get('domain', 'unknown')
        current_coverage = self.coverage_map.get(domain, 0)
        max_coverage = max(self.coverage_map.values()) if self.coverage_map else 1

        # Inverse coverage: less explored = higher score
        coverage_gain = 1.0 / (1.0 + current_coverage) if current_coverage < max_coverage else 0.2

        # Component 2: Expected quality gain
        complexity = task.get('complexity', 0.5)  # 0-1 scale
        estimated_learning_rate = self._estimate_learning_rate(domain)
        quality_gain = complexity * estimated_learning_rate

        # Component 3: Expected reuse gain
        generality = task.get('generality', 0.5)  # How reusable is output?
        reuse_gain = generality

        # Component 4: Entropy pressure (test limits)
        entropy_pressure = task.get('entropy_pressure', 0.3)

        # Component 5: Risk penalty
        risk_level = task.get('risk_level', 0.3)  # 0-1 scale
        time_budget = task.get('estimated_time_minutes', 30)
        token_budget = task.get('estimated_tokens', 10000)

        # Cap risks
        time_penalty = max(0, (time_budget - 60) / 60)  # Penalize >60 min
        token_penalty = max(0, (token_budget - 50000) / 50000)  # Penalize >50k tokens
        risk_penalty = (risk_level + time_penalty + token_penalty) / 3

        # Final score
        score = (
            self.alpha * coverage_gain +
            self.beta * quality_gain +
            self.gamma * reuse_gain +
            self.delta * entropy_pressure -
            risk_penalty
        )

        return max(0.0, score)  # Clamp to non-negative

    def propose_tasks(self, num_tasks: int = 3) -> List[Dict]:
        """
        Propose N tasks with pre-registered predictions.

        Returns:
            List of task proposals with predictions
        """
        # Generate candidate tasks
        candidates = self._generate_candidates()

        # Score and rank
        scored = [(self.score_task(task), task) for task in candidates]
        scored.sort(reverse=True)
        top_tasks = scored[:num_tasks]

        # Pre-register predictions for each
        proposals = []
        for score, task in top_tasks:
            prediction = self._predict_kpi_deltas(task)

            proposal = {
                'task_id': f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.proposed_tasks)}",
                'timestamp': datetime.now().isoformat(),
                'task': task,
                'score': score,
                'predicted': prediction,
                'status': 'proposed'
            }

            self.proposed_tasks.append(proposal)
            proposals.append(proposal)

            # Log to curriculum ledger
            self._log_proposal(proposal)

        return proposals

    def record_completion(
        self,
        task_id: str,
        actual_outcomes: Dict
    ) -> Dict:
        """
        Record task completion with actual KPI deltas.

        Args:
            task_id: ID of completed task
            actual_outcomes: Measured KPI changes

        Returns:
            validation: Prediction vs actual comparison
        """
        # Find proposal
        proposal = None
        for p in self.proposed_tasks:
            if p['task_id'] == task_id:
                proposal = p
                break

        if not proposal:
            return {'error': 'task_not_found'}

        # Compare predicted vs actual
        predicted = proposal['predicted']
        validation = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'predicted': predicted,
            'actual': actual_outcomes,
            'errors': {},
            'mse': 0.0
        }

        # Calculate errors for each KPI
        total_squared_error = 0.0
        num_kpis = 0

        for kpi in ['delta_lambda', 'delta_entropy', 'delta_quality', 'delta_throughput']:
            if kpi in predicted and kpi in actual_outcomes:
                pred_val = predicted[kpi]
                actual_val = actual_outcomes[kpi]
                error = actual_val - pred_val
                squared_error = error ** 2

                validation['errors'][kpi] = {
                    'predicted': pred_val,
                    'actual': actual_val,
                    'error': error,
                    'absolute_error': abs(error),
                    'percent_error': (error / pred_val * 100) if pred_val != 0 else 0
                }

                total_squared_error += squared_error
                num_kpis += 1

        if num_kpis > 0:
            validation['mse'] = total_squared_error / num_kpis
            validation['rmse'] = np.sqrt(validation['mse'])

        # Update coverage
        domain = proposal['task'].get('domain', 'unknown')
        self.coverage_map[domain] += 1

        # Mark completed
        proposal['status'] = 'completed'
        proposal['actual'] = actual_outcomes
        proposal['validation'] = validation
        self.completed_tasks.append(proposal)

        # Log completion
        self._log_completion(proposal)

        return validation

    def get_curriculum_stats(self) -> Dict:
        """
        Get curriculum statistics.

        Returns:
            Stats on task proposals, completions, prediction accuracy
        """
        completed = [p for p in self.proposed_tasks if p['status'] == 'completed']

        if not completed:
            return {
                'total_proposed': len(self.proposed_tasks),
                'total_completed': 0,
                'completion_rate': 0.0,
                'coverage_map': dict(self.coverage_map),
                'prediction_accuracy': {}
            }

        # Prediction accuracy
        mses = [p.get('validation', {}).get('mse', 0) for p in completed if 'validation' in p]
        mean_mse = np.mean(mses) if mses else 0.0

        # Domain coverage
        domains_explored = len(self.coverage_map)

        stats = {
            'total_proposed': len(self.proposed_tasks),
            'total_completed': len(completed),
            'completion_rate': len(completed) / len(self.proposed_tasks) if self.proposed_tasks else 0.0,
            'coverage_map': dict(self.coverage_map),
            'domains_explored': domains_explored,
            'prediction_accuracy': {
                'mean_mse': mean_mse,
                'mean_rmse': np.sqrt(mean_mse) if mean_mse > 0 else 0.0,
                'num_tasks_with_validation': len(mses)
            }
        }

        return stats

    def _generate_candidates(self) -> List[Dict]:
        """
        Generate candidate tasks.

        This is where autonomy happens - no human prompts.
        """
        candidates = []

        # Task template domains
        domains = [
            {
                'domain': 'refactoring',
                'tasks': [
                    {
                        'name': 'Orphan pruning',
                        'description': 'Archive 87% orphaned modules to separate directory',
                        'complexity': 0.7,
                        'generality': 0.6,
                        'entropy_pressure': 0.4,
                        'risk_level': 0.3,
                        'estimated_time_minutes': 45,
                        'estimated_tokens': 30000
                    },
                    {
                        'name': 'Dependency restructure',
                        'description': 'Reorganize into core/experiments/archive structure',
                        'complexity': 0.8,
                        'generality': 0.7,
                        'entropy_pressure': 0.5,
                        'risk_level': 0.4,
                        'estimated_time_minutes': 60,
                        'estimated_tokens': 40000
                    },
                    {
                        'name': 'Interface standardization',
                        'description': 'Standardize all module interfaces to common spec',
                        'complexity': 0.6,
                        'generality': 0.8,
                        'entropy_pressure': 0.3,
                        'risk_level': 0.2,
                        'estimated_time_minutes': 50,
                        'estimated_tokens': 35000
                    }
                ]
            },
            {
                'domain': 'validation',
                'tasks': [
                    {
                        'name': 'Ablation study',
                        'description': 'Disable each component and measure degradation',
                        'complexity': 0.7,
                        'generality': 0.9,
                        'entropy_pressure': 0.6,
                        'risk_level': 0.3,
                        'estimated_time_minutes': 40,
                        'estimated_tokens': 25000
                    },
                    {
                        'name': 'Cross-model replication',
                        'description': 'Run same experiments on different model',
                        'complexity': 0.8,
                        'generality': 0.8,
                        'entropy_pressure': 0.7,
                        'risk_level': 0.5,
                        'estimated_time_minutes': 90,
                        'estimated_tokens': 60000
                    }
                ]
            },
            {
                'domain': 'skill_synthesis',
                'tasks': [
                    {
                        'name': 'Extract statistical validation skill',
                        'description': 'Convert recurring validation pattern into reusable skill',
                        'complexity': 0.6,
                        'generality': 0.9,
                        'entropy_pressure': 0.4,
                        'risk_level': 0.2,
                        'estimated_time_minutes': 30,
                        'estimated_tokens': 20000
                    },
                    {
                        'name': 'Extract ablation skill',
                        'description': 'Convert ablation pattern into reusable skill',
                        'complexity': 0.6,
                        'generality': 0.9,
                        'entropy_pressure': 0.4,
                        'risk_level': 0.2,
                        'estimated_time_minutes': 30,
                        'estimated_tokens': 20000
                    }
                ]
            },
            {
                'domain': 'meta_learning',
                'tasks': [
                    {
                        'name': 'Lambda convergence analysis',
                        'description': 'Analyze λ trajectory across domains and regimes',
                        'complexity': 0.5,
                        'generality': 0.7,
                        'entropy_pressure': 0.3,
                        'risk_level': 0.1,
                        'estimated_time_minutes': 25,
                        'estimated_tokens': 15000
                    },
                    {
                        'name': 'Attractor prediction',
                        'description': 'Predict final convergence point for policy weights',
                        'complexity': 0.7,
                        'generality': 0.8,
                        'entropy_pressure': 0.5,
                        'risk_level': 0.2,
                        'estimated_time_minutes': 35,
                        'estimated_tokens': 25000
                    }
                ]
            }
        ]

        # Flatten into candidate list
        for domain_group in domains:
            domain_name = domain_group['domain']
            for task in domain_group['tasks']:
                task['domain'] = domain_name
                candidates.append(task)

        return candidates

    def _predict_kpi_deltas(self, task: Dict) -> Dict:
        """
        Predict KPI changes from executing this task.

        Uses simple heuristics for now; upgrade to learned model later.
        """
        domain = task.get('domain', 'unknown')
        complexity = task.get('complexity', 0.5)
        generality = task.get('generality', 0.5)

        # Heuristic predictions (these are testable claims!)
        predictions = {
            'delta_lambda': 0.0,
            'delta_entropy': 0.0,
            'delta_quality': 0.0,
            'delta_throughput': 0.0,
            'delta_reuse_ratio': 0.0
        }

        # Domain-specific heuristics
        if domain == 'refactoring':
            predictions['delta_lambda'] = -0.01 * complexity  # Cleanup reduces complexity
            predictions['delta_entropy'] = -0.05 * complexity  # Less chaos
            predictions['delta_quality'] = 0.05 * generality  # Better structure
            predictions['delta_throughput'] = 0.10 * generality  # Easier to navigate

        elif domain == 'validation':
            predictions['delta_quality'] = 0.10 * complexity  # Better understanding
            predictions['delta_entropy'] = 0.02 * complexity  # Learning adds info

        elif domain == 'skill_synthesis':
            predictions['delta_reuse_ratio'] = 0.15 * generality  # More reuse
            predictions['delta_throughput'] = 0.08 * generality  # Faster execution
            predictions['delta_quality'] = 0.05 * generality  # More consistent

        elif domain == 'meta_learning':
            predictions['delta_lambda'] = 0.01 * complexity  # Better decay model
            predictions['delta_quality'] = 0.08 * complexity  # Deeper understanding

        return predictions

    def _estimate_learning_rate(self, domain: str) -> float:
        """
        Estimate learning rate for domain.

        High learning rate = high potential for improvement.
        """
        # Heuristic: less explored = higher learning rate
        current_coverage = self.coverage_map.get(domain, 0)

        if current_coverage == 0:
            return 1.0  # Virgin territory
        elif current_coverage < 5:
            return 0.7  # Still learning
        elif current_coverage < 10:
            return 0.4  # Diminishing returns
        else:
            return 0.2  # Saturated

    def _load_coverage(self):
        """Load existing coverage from continuity ledger"""
        if not self.ledger_path.exists():
            return

        try:
            with open(self.ledger_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        # Infer domain from artifact type
                        artifact_type = entry.get('artifact_type', 'unknown')
                        domain = self._infer_domain(artifact_type)
                        self.coverage_map[domain] += 1
        except Exception:
            pass

    def _infer_domain(self, artifact_type: str) -> str:
        """Map artifact type to domain"""
        type_lower = artifact_type.lower()

        if any(kw in type_lower for kw in ['tool', 'pipeline', 'validator', 'schema']):
            return 'building'
        elif any(kw in type_lower for kw in ['analysis', 'synthesis', 'audit', 'retrospective']):
            return 'analysis'
        elif any(kw in type_lower for kw in ['test', 'validation', 'proof']):
            return 'validation'
        else:
            return 'unknown'

    def _log_proposal(self, proposal: Dict):
        """Log task proposal to curriculum ledger"""
        with open(self.curriculum_log_path, 'a') as f:
            f.write(json.dumps({
                'event': 'task_proposed',
                'timestamp': proposal['timestamp'],
                'task_id': proposal['task_id'],
                'task': proposal['task'],
                'score': proposal['score'],
                'predicted': proposal['predicted']
            }) + '\n')

    def _log_completion(self, proposal: Dict):
        """Log task completion to curriculum ledger"""
        with open(self.curriculum_log_path, 'a') as f:
            f.write(json.dumps({
                'event': 'task_completed',
                'timestamp': datetime.now().isoformat(),
                'task_id': proposal['task_id'],
                'actual': proposal.get('actual', {}),
                'validation': proposal.get('validation', {})
            }) + '\n')


if __name__ == '__main__':
    # Test ACE
    print("=" * 70)
    print("AUTOCURRICULUM ENGINE - TEST")
    print("=" * 70)

    ace = AutocurriculumEngine()

    # Propose 3 tasks
    print("\nProposing 3 highest-value tasks...")
    proposals = ace.propose_tasks(num_tasks=3)

    for i, proposal in enumerate(proposals, 1):
        print(f"\n[Task {i}] {proposal['task']['name']}")
        print(f"  Domain: {proposal['task']['domain']}")
        print(f"  Score: {proposal['score']:.4f}")
        print(f"  Complexity: {proposal['task']['complexity']:.2f}")
        print(f"  Predictions:")
        for kpi, value in proposal['predicted'].items():
            print(f"    {kpi}: {value:+.4f}")

    # Simulate completion
    print("\n" + "=" * 70)
    print("Simulating task completion...")

    task_id = proposals[0]['task_id']
    actual_outcomes = {
        'delta_lambda': -0.008,
        'delta_entropy': -0.042,
        'delta_quality': 0.053,
        'delta_throughput': 0.095
    }

    validation = ace.record_completion(task_id, actual_outcomes)

    print(f"\nValidation for {task_id}:")
    print(f"  RMSE: {validation['rmse']:.4f}")
    for kpi, metrics in validation['errors'].items():
        print(f"  {kpi}:")
        print(f"    Predicted: {metrics['predicted']:+.4f}")
        print(f"    Actual: {metrics['actual']:+.4f}")
        print(f"    Error: {metrics['error']:+.4f} ({metrics['percent_error']:+.1f}%)")

    # Stats
    print("\n" + "=" * 70)
    print("CURRICULUM STATS")
    print("=" * 70)
    stats = ace.get_curriculum_stats()
    print(json.dumps(stats, indent=2))
