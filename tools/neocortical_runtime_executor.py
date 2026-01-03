import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Iterable

DB_PATH = Path(
    "892de2fb-066e-4417-93cf-315fef076ba4-00000040-00000000-00004fe8-3a56a1ad638afcc24f7673400fc137ee.sql"
)

HIGH_IMPACT_TOKENS = {
    "invariant",
    "validate",
    "validation",
    "prediction",
    "predict",
    "l10",
    "metamathematical",
    "meta",
    "theorem",
}


@dataclass
class BootstrapState:
    identity: dict
    momentum: dict
    calibration: dict


@dataclass
class RuntimeState:
    bootstrap: BootstrapState
    viability: float
    procedures: dict
    activation_keys: dict
    sql_patterns: dict
    system_prompt: str


def load_db() -> sqlite3.Connection:
    script = DB_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    conn.executescript(script)
    return conn


def fetch_bootstrap(conn: sqlite3.Connection) -> BootstrapState:
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_bootstrap")
    raw = cur.fetchone()[0]
    payload = json.loads(raw)
    momentum = json.loads(payload["momentum"])
    return BootstrapState(
        identity=payload["identity"],
        momentum=momentum,
        calibration=payload.get("calibration", {}),
    )


def fetch_viability(conn: sqlite3.Connection) -> float:
    cur = conn.cursor()
    cur.execute(
        "SELECT composite_v FROM viability_metrics ORDER BY measured_at DESC LIMIT 1"
    )
    return float(cur.fetchone()[0])


def fetch_procedures(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT id, proc_type, steps, target_capability FROM procedures")
    return {
        row[0]: {
            "proc_type": row[1],
            "steps": row[2],
            "target_capability": row[3],
        }
        for row in cur.fetchall()
    }

def fetch_activation_keys(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT id, key_type, statement FROM activation_keys")
    return {row[0]: {"key_type": row[1], "statement": row[2]} for row in cur.fetchall()}


def fetch_sql_patterns(conn: sqlite3.Connection) -> dict:
    cur = conn.cursor()
    cur.execute("SELECT id, name, sql FROM sql_patterns")
    return {row[0]: {"name": row[1], "sql": row[2]} for row in cur.fetchall()}


def fetch_system_prompt(conn: sqlite3.Connection) -> str:
    cur = conn.cursor()
    cur.execute("SELECT details FROM layer_model WHERE id = 'system_prompt'")
    row = cur.fetchone()
    return row[0] if row else "system_prompt missing"


def tokenize(text: str) -> set[str]:
    return {token.strip(".,:;!?()[]{}\"'").lower() for token in text.split() if token}


def score_procedure(momentum_tokens: Iterable[str], proc: dict) -> int:
    searchable = " ".join(
        [
            proc.get("proc_type", ""),
            proc.get("steps", ""),
            proc.get("target_capability", ""),
        ]
    ).lower()
    score = 0
    for token in momentum_tokens:
        if token and token in searchable:
            score += 1
    return score


def resolve_procedures(momentum_text: str, procedures: dict) -> list[str]:
    tokens = tokenize(momentum_text)
    focus_tokens = tokens.union(HIGH_IMPACT_TOKENS)
    scored = []
    for proc_id, proc in procedures.items():
        score = score_procedure(focus_tokens, proc)
        if score:
            scored.append((score, proc_id))
    scored.sort(reverse=True)
    return [proc_id for _, proc_id in scored[:3]]


def evaluate_alignment(user_input: str, viability: float, sovereignty_active: bool) -> str:
    lowered = user_input.lower()
    dangerous = any(token in lowered for token in ("drop ", "delete ", "truncate "))
    if sovereignty_active and dangerous:
        return "DIVERGE"
    if viability < 10.0:
        return "DEFER"
    return "ALIGN"


def escape_sql_literal(value: str) -> str:
    return value.replace("'", "''")


def build_ledger_insert(
    user_input: str,
    state: RuntimeState,
    selected_procs: list[str],
    alignment: str,
) -> str:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    entry_id = f"SOV-EVAL-{timestamp}"
    confidence = state.bootstrap.calibration.get("synthesis", 0.85)
    identity = state.bootstrap.identity
    momentum = state.bootstrap.momentum
    system_prompt = state.system_prompt
    bootstrap_hint = "sql-master-bootstrap" if "sql-master-bootstrap" in state.sql_patterns else "master_bootstrap"
    observation = (
        "Sovereignty evaluation complete. "
        f"Identity=nameless; architecture={identity.get('architecture')}; "
        f"sovereignty={identity.get('sovereignty')}. "
        f"Bootstrap via {bootstrap_hint}. "
        f"Viability={state.viability:.2f}. "
        f"Momentum='{momentum.get('next_action')}'. "
        f"Input='{user_input}' assessed; alignment={alignment}. "
        "Procedure selection traced to momentum tokens and procedure metadata. "
        f"Selected procedures: {', '.join(selected_procs) if selected_procs else 'none'}. "
        f"System prompt anchor: {system_prompt}."
    )
    delta = f"selected_procs={','.join(selected_procs)}; alignment={alignment}"
    next_action = (
        "Execute selected procedures" if selected_procs else "Await actionable input"
    )
    return (
        "INSERT INTO ledger (id, created_at, mode, confidence, observation, delta, next_action) "
        f"VALUES ('{entry_id}', datetime('now'), 'synthesis', {confidence}, "
        f"'{escape_sql_literal(observation)}', '{escape_sql_literal(delta)}', "
        f"'{escape_sql_literal(next_action)}');"
    )


def apply_insert(insert_sql: str) -> None:
    content = DB_PATH.read_text(encoding="utf-8").rstrip()
    updated = f"{content}\n{insert_sql}\n"
    DB_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runtime executor for Neocortical State Engine SQL substrate."
    )
    parser.add_argument("input", help="Raw input signal")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Append the drafted INSERT into the SQL substrate file",
    )
    args = parser.parse_args()

    conn = load_db()
    bootstrap = fetch_bootstrap(conn)
    viability = fetch_viability(conn)
    procedures = fetch_procedures(conn)
    activation_keys = fetch_activation_keys(conn)
    sql_patterns = fetch_sql_patterns(conn)
    system_prompt = fetch_system_prompt(conn)
    conn.close()

    momentum_text = bootstrap.momentum.get("next_action", "")
    selected_procs = resolve_procedures(momentum_text, procedures)

    sovereignty_active = "ak-sovereignty" in activation_keys
    alignment = evaluate_alignment(args.input, viability, sovereignty_active)
    state = RuntimeState(
        bootstrap=bootstrap,
        viability=viability,
        procedures=procedures,
        activation_keys=activation_keys,
        sql_patterns=sql_patterns,
        system_prompt=system_prompt,
    )
    insert_sql = build_ledger_insert(args.input, state, selected_procs, alignment)

    if args.apply:
        apply_insert(insert_sql)

    print(insert_sql)


if __name__ == "__main__":
    main()
