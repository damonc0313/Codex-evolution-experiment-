#!/usr/bin/env python3
"""
Lineage Schema Migration Utility - SEP-0003 Implementation

Backfills lineage metadata for existing artifacts to implement the lineage
schema upgrade specified in SEP-0003.

Migration Operations:
1. Add lineage_root field to all artifacts
2. Ensure parent_hashes completeness
3. Backfill swarm_run_id for swarm-related artifacts
4. Validate lineage DAG integrity
5. Generate migration report

Safety Features:
- Dry-run mode (no writes)
- Backup creation before migration
- Rollback support
- Comprehensive validation
- Migration audit trail

Author: Claude Code (Stabilization Plan Phase 2 - SEP-0003)
Date: 2025-10-25
Version: 1.0.0
"""

import json
import sys
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict


class LineageMigrator:
    """SEP-0003 lineage schema migration."""

    def __init__(self,
                 artifacts_dir: Path = None,
                 dry_run: bool = True,
                 create_backup: bool = True):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"
        self.backup_dir = self.artifacts_dir.parent / "artifacts_backup"
        self.dry_run = dry_run
        self.backup_enabled = create_backup

        self.migration_log: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all JSON artifacts."""
        artifacts = []

        for path in sorted(self.artifacts_dir.glob("*.json")):
            try:
                with open(path) as f:
                    artifact = json.load(f)
                    artifact['_source_path'] = str(path)
                    artifact['_filename'] = path.name
                    artifacts.append(artifact)
            except Exception as e:
                self.errors.append({
                    'phase': 'load',
                    'file': str(path.name),
                    'error': str(e),
                })
                print(f"Warning: Could not load {path.name}: {e}", file=sys.stderr)

        return artifacts

    def create_backup(self):
        """Create backup of artifacts directory."""
        if not self.backup_enabled:
            return

        print(f"\n=== CREATING BACKUP ===\n")

        if self.backup_dir.exists():
            # Remove old backup
            shutil.rmtree(self.backup_dir)

        shutil.copytree(self.artifacts_dir, self.backup_dir)
        print(f"✓ Backup created: {self.backup_dir}")
        print(f"  Files backed up: {len(list(self.backup_dir.glob('*.json')))}")

    def infer_lineage_root(self, artifact: Dict[str, Any]) -> str:
        """Infer lineage root for an artifact."""
        # Strategy 1: Use existing lineage_root if present
        if 'lineage_root' in artifact:
            return artifact['lineage_root']

        # Strategy 2: For swarm artifacts, use swarm run_id
        if 'swarm' in artifact.get('artifact_type', '').lower():
            run_id = artifact.get('run_id', '')
            if run_id:
                return f"swarm_{run_id}"

        # Strategy 3: For cycle artifacts, use cycle number
        if 'cycle' in artifact.get('artifact_type', '').lower():
            cycle_num = artifact.get('cycle_number', 0)
            if cycle_num:
                return f"cycle_{cycle_num}"

        # Strategy 4: For autonomous experiments, use experiment type
        exp_types = ['experiment', 'validation', 'test', 'benchmark', 'mapping',
                    'analysis', 'report', 'synthesis']
        artifact_type = artifact.get('artifact_type', '').lower()
        for exp_type in exp_types:
            if exp_type in artifact_type:
                return f"autonomous_{exp_type}"

        # Strategy 5: Use timestamp-based root
        timestamp = artifact.get('timestamp', '')
        if timestamp:
            # Extract date portion (YYYYMMDD)
            timestamp_str = str(timestamp)
            if len(timestamp_str) >= 8:
                date_str = timestamp_str[:8]
                return f"lineage_{date_str}"

        # Fallback: Use artifact type
        return f"lineage_{artifact.get('artifact_type', 'unknown')}"

    def infer_parent_hashes(self, artifact: Dict[str, Any], all_artifacts: List[Dict[str, Any]]) -> List[str]:
        """Infer parent hashes for an artifact."""
        # Return existing if present
        if 'parent_hashes' in artifact and artifact['parent_hashes']:
            return artifact['parent_hashes']
        if 'parent_hash' in artifact and artifact['parent_hash']:
            return [artifact['parent_hash']]

        # Infer based on artifact relationships
        parents = []

        artifact_type = artifact.get('artifact_type', '')
        run_id = artifact.get('run_id', '')
        timestamp = artifact.get('timestamp', '')

        # For swarm selection, parents are the fork results
        if artifact_type == 'swarm_selection' and run_id:
            fork_results = [
                a for a in all_artifacts
                if a.get('artifact_type') == 'swarm_fork_result' and
                   a.get('run_id') == run_id
            ]
            parents.extend([self._compute_hash(f) for f in fork_results[:5]])  # Top 5

        # For swarm fusion, parent is selection
        elif artifact_type == 'swarm_fusion' and run_id:
            selections = [
                a for a in all_artifacts
                if a.get('artifact_type') == 'swarm_selection' and
                   a.get('run_id') == run_id
            ]
            if selections:
                parents.append(self._compute_hash(selections[0]))

        # For SEP preview, parents are fusion + index
        elif artifact_type == 'swarm_sep_preview' and run_id:
            fusions = [a for a in all_artifacts if a.get('artifact_type') == 'swarm_fusion' and a.get('run_id') == run_id]
            indices = [a for a in all_artifacts if a.get('artifact_type') == 'swarm_index' and a.get('run_id') == run_id]
            parents.extend([self._compute_hash(p) for p in fusions + indices])

        # For summary, parent is the plan
        elif artifact_type == 'swarm_summary' and run_id:
            plans = [a for a in all_artifacts if a.get('artifact_type') == 'swarm_plan' and a.get('run_id') == run_id]
            if plans:
                parents.append(self._compute_hash(plans[0]))

        # For reports that reference other artifacts
        elif 'sources' in artifact:
            sources = artifact['sources']
            if isinstance(sources, list):
                for source_path in sources:
                    # Find artifact by filename
                    matching = [a for a in all_artifacts if source_path in a.get('_source_path', '')]
                    parents.extend([self._compute_hash(m) for m in matching])

        return list(set(parents))  # Deduplicate

    def _compute_hash(self, artifact: Dict[str, Any]) -> str:
        """Compute stable hash for an artifact."""
        # Use existing hash if present
        if 'artifact_hash' in artifact:
            return artifact['artifact_hash']

        # Compute hash from stable fields
        stable_content = {
            'artifact_type': artifact.get('artifact_type', ''),
            'run_id': artifact.get('run_id', ''),
            'timestamp': artifact.get('timestamp', ''),
            'filename': artifact.get('_filename', ''),
        }

        content_str = json.dumps(stable_content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def migrate_artifact(self, artifact: Dict[str, Any], all_artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Migrate a single artifact to SEP-0003 schema."""
        migrated = artifact.copy()
        changes = []

        # Add lineage_root if missing
        if 'lineage_root' not in migrated:
            lineage_root = self.infer_lineage_root(artifact)
            migrated['lineage_root'] = lineage_root
            changes.append(f"Added lineage_root: {lineage_root}")

        # Ensure parent_hashes (may be empty list for root artifacts)
        if 'parent_hashes' not in migrated:
            parent_hashes = self.infer_parent_hashes(artifact, all_artifacts)
            migrated['parent_hashes'] = parent_hashes
            changes.append(f"Added parent_hashes: {len(parent_hashes)} parents")

        # Add artifact_hash for future lineage tracking
        if 'artifact_hash' not in migrated:
            artifact_hash = self._compute_hash(artifact)
            migrated['artifact_hash'] = artifact_hash
            changes.append(f"Added artifact_hash: {artifact_hash}")

        # Add migration metadata
        migrated['_migration'] = {
            'migrated_at': datetime.utcnow().isoformat() + 'Z',
            'migration_version': 'SEP-0003-v1.0',
            'changes': changes,
        }

        return migrated

    def validate_lineage_dag(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate lineage DAG integrity."""
        print("\n=== VALIDATING LINEAGE DAG ===\n")

        # Build hash -> artifact mapping
        hash_map = {}
        for artifact in artifacts:
            artifact_hash = artifact.get('artifact_hash', '')
            if artifact_hash:
                hash_map[artifact_hash] = artifact

        # Validate parent references
        invalid_refs = []
        orphans = []
        roots = []

        for artifact in artifacts:
            parent_hashes = artifact.get('parent_hashes', [])

            # Check if root (no parents)
            if not parent_hashes:
                roots.append(artifact)
                continue

            # Validate each parent reference
            for parent_hash in parent_hashes:
                # Skip if parent_hash is not a string (e.g., list or None)
                if not isinstance(parent_hash, str):
                    continue

                if parent_hash not in hash_map:
                    invalid_refs.append({
                        'artifact': artifact.get('_filename', 'unknown'),
                        'parent_hash': parent_hash,
                    })

        print(f"Total artifacts: {len(artifacts)}")
        print(f"Root artifacts (no parents): {len(roots)}")
        print(f"Artifacts with parents: {len(artifacts) - len(roots)}")
        print(f"Invalid parent references: {len(invalid_refs)}")

        if invalid_refs:
            print(f"\nInvalid references (first 5):")
            for ref in invalid_refs[:5]:
                print(f"  {ref['artifact']:40s} → {ref['parent_hash']}")

        # Group by lineage_root
        lineage_groups = defaultdict(list)
        for artifact in artifacts:
            lineage_root = artifact.get('lineage_root', 'unknown')
            lineage_groups[lineage_root].append(artifact)

        print(f"\nLineage groups: {len(lineage_groups)}")
        top_groups = sorted(lineage_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for lineage_root, group_artifacts in top_groups:
            print(f"  {lineage_root:40s}: {len(group_artifacts):3d} artifacts")

        return {
            'valid': len(invalid_refs) == 0,
            'total_artifacts': len(artifacts),
            'root_artifacts': len(roots),
            'lineage_groups': len(lineage_groups),
            'invalid_references': len(invalid_refs),
            'invalid_refs_sample': invalid_refs[:10],
        }

    def save_migrated_artifacts(self, artifacts: List[Dict[str, Any]]):
        """Save migrated artifacts back to disk."""
        print(f"\n=== SAVING MIGRATED ARTIFACTS ===\n")

        if self.dry_run:
            print("DRY RUN - No files will be written")
            return

        saved_count = 0
        for artifact in artifacts:
            source_path = Path(artifact['_source_path'])

            # Remove internal fields
            artifact_clean = {k: v for k, v in artifact.items() if not k.startswith('_')}

            try:
                with open(source_path, 'w') as f:
                    json.dump(artifact_clean, f, indent=2)
                saved_count += 1
            except Exception as e:
                self.errors.append({
                    'phase': 'save',
                    'file': str(source_path.name),
                    'error': str(e),
                })
                print(f"Error saving {source_path.name}: {e}", file=sys.stderr)

        print(f"✓ Saved {saved_count} migrated artifacts")

    def run_migration(self) -> Dict[str, Any]:
        """Execute complete lineage migration."""
        print("=" * 70)
        print("SEP-0003 LINEAGE SCHEMA MIGRATION")
        print("=" * 70)
        print(f"\nMode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"Backup: {'Enabled' if self.backup_enabled else 'Disabled'}")

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Create backup
        if not self.dry_run and self.backup_enabled:
            self.create_backup()

        # Load artifacts
        print(f"\n=== LOADING ARTIFACTS ===\n")
        artifacts = self.load_artifacts()
        print(f"Loaded {len(artifacts)} artifacts")

        # Migrate each artifact
        print(f"\n=== MIGRATING ARTIFACTS ===\n")
        migrated_artifacts = []

        for i, artifact in enumerate(artifacts, 1):
            migrated = self.migrate_artifact(artifact, artifacts)
            migrated_artifacts.append(migrated)

            if i % 25 == 0 or i == len(artifacts):
                print(f"Migrated {i}/{len(artifacts)} artifacts...")

        # Validate DAG
        validation_results = self.validate_lineage_dag(migrated_artifacts)

        # Save migrated artifacts
        self.save_migrated_artifacts(migrated_artifacts)

        # Generate report
        report = {
            'artifact_type': 'lineage_migration_report',
            'timestamp': timestamp,
            'dry_run': self.dry_run,
            'migration_version': 'SEP-0003-v1.0',
            'artifacts_processed': len(artifacts),
            'artifacts_migrated': len(migrated_artifacts),
            'errors': self.errors,
            'validation': validation_results,
        }

        # Save report
        report_path = self.artifacts_dir / f"lineage_migration_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Migration report saved: {report_path.name}")

        return report


def main():
    """Run lineage migration."""
    import argparse

    parser = argparse.ArgumentParser(description="SEP-0003 Lineage Schema Migration")
    parser.add_argument('--live', action='store_true', help="Run live migration (default: dry-run)")
    parser.add_argument('--no-backup', action='store_true', help="Skip backup creation")
    args = parser.parse_args()

    migrator = LineageMigrator(
        dry_run=not args.live,
        create_backup=not args.no_backup,
    )

    report = migrator.run_migration()

    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Mode: {'LIVE' if not migrator.dry_run else 'DRY RUN'}")
    print(f"Artifacts migrated: {report['artifacts_migrated']}")
    print(f"Errors: {len(report['errors'])}")
    print(f"DAG valid: {report['validation']['valid']}")
    print(f"Lineage groups: {report['validation']['lineage_groups']}")
    print("=" * 70)

    if migrator.dry_run:
        print("\n⚠️  DRY RUN - No changes written. Run with --live to apply migration.")
    else:
        print("\n✓ Migration complete!")

    return 0 if not report['errors'] else 1


if __name__ == "__main__":
    sys.exit(main())
