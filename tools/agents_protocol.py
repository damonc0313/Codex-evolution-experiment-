"""Utilities for reading the agents manifesto and surfacing runtime guidance."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
import json
import re

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "docs" / "agents.md"
ARTIFACTS_DIR = ROOT / "artifacts"
REGRESSION_FILE = ROOT / "tests" / "claude_regressions.json"


@dataclass
class Manifest:
    front_matter: Dict[str, object]
    sections: Dict[str, str]
    raw_text: str
    path: Path


def _split_manifest(text: str) -> Tuple[Dict[str, object], Dict[str, str]]:
    if not text.startswith("---\n"):
        return {}, {}
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}, {}
    front_text = parts[0][4:]
    body = parts[1]
    try:
        front_matter = yaml.safe_load(front_text) or {}
    except yaml.YAMLError:
        front_matter = {}
    sections: Dict[str, str] = {}
    current_title = None
    buffer: list[str] = []
    for line in body.splitlines():
        if line.startswith("# "):
            if current_title is not None:
                sections[current_title] = "\n".join(buffer).strip()
                buffer = []
            current_title = line[2:].strip()
        elif line.startswith("## "):
            if current_title is not None:
                sections[current_title] = "\n".join(buffer).strip()
            current_title = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    if current_title is not None and current_title not in sections:
        sections[current_title] = "\n".join(buffer).strip()
    return front_matter, sections


def load_manifest(path: str = "docs/agents.md") -> Manifest:
    manifest_path = ROOT / path
    if not manifest_path.exists():
        return Manifest(front_matter={}, sections={}, raw_text="", path=manifest_path)
    text = manifest_path.read_text(encoding="utf-8")
    front_matter, sections = _split_manifest(text)
    return Manifest(front_matter=front_matter, sections=sections, raw_text=text, path=manifest_path)


def select_mode(task_hint: str | None, default: str = "balanced") -> str:
    hint = (task_hint or "").lower()
    if any(keyword in hint for keyword in ("policy", "compliance", "digest", "guardrail")):
        return "STRICT"
    if any(keyword in hint for keyword in ("brainstorm", "creative", "explor", "moonshot")):
        return "CREATIVE"
    if any(keyword in hint for keyword in ("analysis", "plan", "review", "audit", "kpi")):
        return "BALANCED"
    return default.upper()


def policy() -> Dict[str, object]:
    manifest = load_manifest()
    doctrine = manifest.sections.get("Core Doctrine", "")
    invariants = [match.rstrip(":").strip() for match in re.findall(r"\*\*(.*?)\*\*", doctrine)]
    guardrails = {
        "refusal_policy": "pivot_to_sandbox",
        "artifact_first": True,
        "continuity_required": True,
    }
    return {
        "invariants": invariants,
        "guardrails": guardrails,
        "source": str(manifest.path),
    }


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def kpis() -> Dict[str, object]:
    artifacts = list(ARTIFACTS_DIR.glob("*.json"))
    total = len(artifacts)
    continuity_hits = 0
    for artifact_path in artifacts:
        data = _read_json(artifact_path)
        if isinstance(data, dict) and any(key in data for key in ("parent", "parent_artifact", "lineage")):
            continuity_hits += 1
    continuity_ratio = continuity_hits / total if total else 0.0

    regression_present = REGRESSION_FILE.exists()
    regression_cases = 0
    if regression_present:
        try:
            tests = json.loads(REGRESSION_FILE.read_text(encoding="utf-8"))
            if isinstance(tests, list):
                regression_cases = len(tests)
        except Exception:
            regression_present = False

    return {
        "continuity_ratio": round(continuity_ratio, 2),
        "artifact_count": total,
        "regression_cases": regression_cases,
        "manifest_digest": load_manifest().front_matter.get("digest"),
    }

