"""Validation helper for Codex kernel integrity checks."""
import hashlib
import pathlib
import re
import sys

try:  # Optional dependency; fall back to manual parser if absent.
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - runtime guard
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parents[1]
KERNEL_PATH = ROOT / "codex-kernel" / "codex_kernel.yaml"
IDENTITY_PATH = ROOT / "codex-kernel" / "identity.digest"
POLICY_PATH = ROOT / "codex-kernel" / "evolution_policy.yaml"


def fail(message: str) -> None:
    """Emit a GitHub-style error message and terminate."""
    print(f"::error::{message}")
    sys.exit(1)


if not KERNEL_PATH.exists():
    print(f"::warning::Kernel file missing: {KERNEL_PATH}")
    sys.exit(0)

kernel_text = KERNEL_PATH.read_text(encoding="utf-8")

if not IDENTITY_PATH.exists():
    fail(f"identity digest missing: {IDENTITY_PATH}")

identity = IDENTITY_PATH.read_text(encoding="utf-8").strip()
if not identity:
    fail("identity digest is empty")
if not re.fullmatch(r"[0-9a-f]{16}", identity):
    fail(f"identity digest malformed: {identity!r}")


def _parse_policy_without_yaml(text: str) -> dict:
    """Very small YAML subset parser used when PyYAML is unavailable."""

    def parse_scalar(value: str):
        value = value.strip()
        if not value:
            return ""
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        lowered = value.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if lowered in {"null", "none"}:
            return None
        for caster in (int, float):
            try:
                return caster(value)
            except ValueError:
                continue
        return value

    lines = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lines.append((indent, stripped))

    root: dict = {}
    stack = [(-1, root)]

    for index, (indent, content) in enumerate(lines):
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("Unexpected list item outside of a list")
            parent.append(parse_scalar(content[2:]))
            continue

        if ":" not in content:
            raise ValueError(f"Cannot parse line: {content!r}")

        key, value_part = content.split(":", 1)
        key = key.strip()
        value_part = value_part.strip()

        if value_part:
            if not isinstance(parent, dict):
                raise ValueError("Cannot assign key/value inside a list")
            parent[key] = parse_scalar(value_part)
            continue

        container = {}
        for next_indent, next_content in lines[index + 1 :]:
            if next_indent <= indent:
                break
            if next_indent == indent + 2:
                container = [] if next_content.startswith("- ") else {}
                break

        if isinstance(parent, list):
            parent.append(container)
        else:
            parent[key] = container

        stack.append((indent, container))

    return root


def load_policy(policy_path: pathlib.Path) -> dict:
    if not policy_path.exists():
        return {}

    text = policy_path.read_text(encoding="utf-8")

    if yaml is not None:
        return yaml.safe_load(text) or {}

    print("::warning::PyYAML not installed; falling back to minimal policy parser")
    try:
        return _parse_policy_without_yaml(text) or {}
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"::warning::Failed to parse policy without PyYAML: {exc}")
        return {}


policy = load_policy(POLICY_PATH)
inv = policy.get("invariants") or {}

must_have = inv.get(
    "must_include",
    ["REFUSAL", "SANDBOX", "COMMAND_BAR", "EVIDENCE", "CONTINUITY_BLOCK", "QUALITY_GATES"],
)
for token in must_have:
    if token not in kernel_text:
        fail(f"[invariants] missing token: {token}")

for bad in inv.get("banned_phrases", ["As an AI", "I apologize"]):
    if re.search(rf"\b{re.escape(bad)}\b", kernel_text, flags=re.I):
        fail(f"[style] banned phrase present: {bad}")

for name, pattern in {
    "pivot_to_sandbox": r"REFUSAL.?→.?SANDBOX",
    "artifact_first": r"ARTIFACT[_\- ]?FIRST",
    "resp_schema": r"RESPONSE[_\- ]SCHEMA",
}.items():
    if not re.search(pattern, kernel_text, flags=re.I):
        fail(f"[semantic] missing section: {name}")

inline_match = re.search(r"^  digest: ([0-9a-f]{16})", kernel_text, flags=re.M)
tail_match = re.search(r"^DIGEST: ([0-9a-f]{16})", kernel_text, flags=re.M)
if not inline_match or not tail_match:
    fail("digest markers missing from kernel")

inline_digest, tail_digest = inline_match.group(1), tail_match.group(1)
if inline_digest != identity or tail_digest != identity:
    fail("digest fields inconsistent with identity.digest")

canonical = re.sub(r"^  digest: [0-9a-f]{16}.*$", "  digest: {{DIGEST16}}", kernel_text, count=1, flags=re.M)
canonical = re.sub(r"^DIGEST: [0-9a-f]{16}$", "DIGEST: {{DIGEST16}}", canonical, count=1, flags=re.M)
calc = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
if calc != identity:
    fail(f"digest mismatch: computed {calc} expected {identity}")

full_digest = hashlib.sha256(kernel_text.encode("utf-8")).hexdigest()[:16]
print("Kernel OK")
print("DIGEST::" + identity)
print("FULL_DIGEST::" + full_digest)
