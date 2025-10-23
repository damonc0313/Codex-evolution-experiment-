#!/usr/bin/env python3
"""Utilities for loading Natural Optimisation Signature data sources.

The mentor specification allows the runtime to ingest a mixture of CSV, JSON,
and Parquet datasets that describe evolutionary systems.  This module keeps the
implementation lightweight—only the standard library is required—but offers
extensibility hooks so richer parsers (e.g. pandas, pyarrow) can be enabled when
available.

Functions return descriptive metadata instead of raising when inputs are
missing; the surrounding automation can then decide whether to fall back to
synthetic defaults or pivot into a sandbox plan.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

try:  # Optional dependency for Parquet support
    import pandas as _pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _pd = None

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "runtime" / "nos_sources.yaml"


@dataclass
class SourceSpec:
    """Configuration record for a single NOS data source."""

    kind: str
    source_id: str
    path: Path
    fields: Dict[str, str]


@dataclass
class SourceSummary:
    """Observed metadata after attempting to load a source."""

    spec: SourceSpec
    exists: bool
    row_count: int
    digest: Optional[str]
    warnings: List[str]

    def to_payload(self) -> Dict[str, object]:
        return {
            "kind": self.spec.kind,
            "id": self.spec.source_id,
            "path": str(self.spec.path),
            "fields": self.spec.fields,
            "exists": self.exists,
            "row_count": self.row_count,
            "digest": self.digest,
            "warnings": self.warnings,
        }


class ConfigError(RuntimeError):
    """Raised when the configuration file cannot be parsed."""


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _normalise_fields(raw: Dict[str, object]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for key, value in raw.items():
        fields[str(key)] = str(value)
    return fields


def load_config(
    config_path: Path | None = None,
    *,
    root: Path | None = None,
) -> List[SourceSpec]:
    """Parse ``runtime/nos_sources.yaml`` into ``SourceSpec`` objects."""

    path = config_path or DEFAULT_CONFIG
    base = (root or ROOT).resolve()
    if not path.exists():
        return []
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - PyYAML optional
        raise ConfigError("PyYAML is required to parse nos_sources.yaml") from exc

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - propagate useful context
        raise ConfigError(f"Failed to parse {path}: {exc}") from exc

    specs: List[SourceSpec] = []
    sources = raw.get("sources", []) if isinstance(raw, dict) else []
    for entry in sources:
        if not isinstance(entry, dict):
            continue
        kind = str(entry.get("kind", ""))
        source_id = str(entry.get("id", ""))
        rel_path = Path(str(entry.get("path", "")))
        fields = _normalise_fields(entry.get("fields", {}))
        full_path = rel_path if rel_path.is_absolute() else (base / rel_path)
        specs.append(
            SourceSpec(
                kind=kind,
                source_id=source_id,
                path=full_path,
                fields=fields,
            )
        )
    return specs


def _load_csv(path: Path) -> Iterator[Dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield dict(row)


def _load_json(path: Path) -> Iterator[Dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield dict(item)
    elif isinstance(payload, dict):
        # Accept {"records": [...]} style payloads
        if "records" in payload and isinstance(payload["records"], list):
            for item in payload["records"]:
                if isinstance(item, dict):
                    yield dict(item)
        else:
            yield payload


def _load_parquet(path: Path) -> Iterator[Dict[str, object]]:
    if _pd is None:  # pragma: no cover - optional dependency
        raise RuntimeError("Parquet support requires pandas or pyarrow")
    frame = _pd.read_parquet(path)
    for record in frame.to_dict(orient="records"):
        yield record


def iter_rows(spec: SourceSpec) -> Iterator[Dict[str, object]]:
    """Yield normalised rows for ``spec``.  Missing sources return no rows."""

    if not spec.path.exists():
        return iter(())
    suffix = spec.path.suffix.lower()
    loader = None
    if suffix in {".csv", ".tsv"}:
        loader = _load_csv
    elif suffix in {".json"}:
        loader = _load_json
    elif suffix in {".parquet"}:
        loader = _load_parquet
    else:
        raise RuntimeError(f"Unsupported data source extension: {suffix}")
    return loader(spec.path)


def summarise_sources(specs: Iterable[SourceSpec]) -> List[SourceSummary]:
    """Load sources and collect row counts/digests."""

    summaries: List[SourceSummary] = []
    for spec in specs:
        exists = spec.path.exists()
        row_count = 0
        digest: Optional[str] = None
        warnings: List[str] = []
        if exists:
            try:
                rows = list(iter_rows(spec))
                row_count = len(rows)
                digest = _sha256(spec.path)
                # Basic schema sanity check: ensure declared fields exist.
                declared = set(spec.fields)
                if declared and rows:
                    missing = sorted(declared - set(rows[0].keys()))
                    if missing:
                        warnings.append(
                            f"Missing fields: {', '.join(missing)}"
                        )
            except Exception as exc:  # pragma: no cover - best-effort ingest
                warnings.append(f"Failed to load source: {exc}")
        else:
            warnings.append("Source file not found; using defaults")
        summaries.append(
            SourceSummary(
                spec=spec,
                exists=exists,
                row_count=row_count,
                digest=digest,
                warnings=warnings,
            )
        )
    return summaries


def derive_feature_averages(rows: Iterable[Dict[str, object]], fields: Iterable[str]) -> float:
    """Helper for computing the mean of declared numeric fields."""

    values: List[float] = []
    for row in rows:
        for field in fields:
            value = row.get(field)
            if isinstance(value, (int, float)):
                values.append(float(value))
            else:
                try:
                    values.append(float(str(value)))
                except (TypeError, ValueError):
                    continue
    if not values:
        return 0.0
    return sum(values) / len(values)


def extract_primitives(summaries: Iterable[SourceSummary]) -> Dict[str, float]:
    """Create NOS primitives from the available sources.

    The mapping is intentionally heuristic: evolutionary datasets differ widely,
    so the function prefers broad proxies to ensure deterministic outputs.  When
    a data file is missing the primitive falls back to ``0.0`` which signals the
    caller to retain default weights.
    """

    primitives = {
        "energy_efficiency": 0.0,
        "coherence": 0.0,
        "resilience": 0.0,
        "entropy": 0.0,
    }
    for summary in summaries:
        if not summary.exists:
            continue
        rows = list(iter_rows(summary.spec))
        if not rows:
            continue
        if summary.spec.kind == "evolution_rates":
            primitives["energy_efficiency"] = derive_feature_averages(
                rows, ["mutation_rate", "selection_gradient"]
            )
        elif summary.spec.kind == "population_dynamics":
            primitives["resilience"] = derive_feature_averages(
                rows, ["birth_rate", "carrying_capacity"]
            )
        elif summary.spec.kind == "fitness_landscapes":
            ruggedness = derive_feature_averages(rows, ["ruggedness"])
            neutrality = derive_feature_averages(rows, ["neutrality"])
            peaks = derive_feature_averages(rows, ["peaks"])
            primitives["entropy"] = max(ruggedness + neutrality, 0.0)
            primitives["coherence"] = max(peaks, 0.0)
    return primitives


__all__ = [
    "SourceSpec",
    "SourceSummary",
    "ConfigError",
    "load_config",
    "summarise_sources",
    "extract_primitives",
    "derive_feature_averages",
]
