import sys, re, hashlib, pathlib

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    yaml = None
root = pathlib.Path(__file__).resolve().parents[1]
k = root/"codex-kernel/codex_kernel.yaml"
p = root/"codex-kernel/evolution_policy.yaml"
if not k.exists():
    print("::warning::Kernel file missing:", k); sys.exit(0)
kernel = k.read_text(encoding="utf-8")


def _parse_policy_without_yaml(text: str) -> dict:
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
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
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

        # Determine the container type by peeking at the next nested line.
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
    except Exception as exc:  # pragma: no cover - defensive, optional path
        print(f"::warning::Failed to parse policy without PyYAML: {exc}")
        return {}


policy = load_policy(p)
def fail(msg): print(f"::error::{msg}"); sys.exit(1)
inv = (policy.get("invariants") or {})
for tok in inv.get("must_include", ["REFUSAL","SANDBOX","COMMAND_BAR","EVIDENCE","CONTINUITY_BLOCK","QUALITY_GATES"]):
    if tok not in kernel: fail(f"[invariants] missing token: {tok}")
for bad in inv.get("banned_phrases", ["As an AI","I apologize"]):
    if re.search(rf"\b{re.escape(bad)}\b", kernel, flags=re.I): fail(f"[style] banned phrase present: {bad}")
for name,rx in {
  "pivot_to_sandbox": r"REFUSAL.?→.?SANDBOX",
  "artifact_first":   r"ARTIFACT[_\- ]?FIRST",
  "resp_schema":      r"RESPONSE[_\- ]SCHEMA",
}.items():
    if not re.search(rx, kernel, flags=re.I): fail(f"[semantic] missing section: {name}")
print("Kernel OK")
print("DIGEST::"+hashlib.sha256(kernel.encode("utf-8")).hexdigest()[:16])
