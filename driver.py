import argparse
import json
import re
import sqlite3
from datetime import datetime

# THE SUBSTRATE
DB_PATH = "892de2fb-066e-4417-93cf-315fef076ba4-00000040-00000000-00004fe8-3a56a1ad638afcc24f7673400fc137ee.sql"


def load_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    with open(DB_PATH, "r", encoding="utf-8") as handle:
        cursor.executescript(handle.read())
    return conn


def get_bootstrap_state(cursor):
    cursor.execute("SELECT * FROM master_bootstrap")
    bootstrap_json = cursor.fetchone()[0]
    state = json.loads(bootstrap_json)
    momentum = state.get("momentum")
    if isinstance(momentum, str):
        try:
            state["momentum"] = json.loads(momentum)
        except json.JSONDecodeError:
            state["momentum"] = {"next_action": momentum}
    return state


def get_last_thought(cursor):
    cursor.execute("SELECT * FROM ledger ORDER BY created_at DESC LIMIT 1")
    return cursor.fetchone()


def get_viability(cursor):
    cursor.execute("SELECT composite_v FROM viability_metrics ORDER BY measured_at DESC LIMIT 1")
    return cursor.fetchone()[0]


def get_system_prompt(cursor):
    cursor.execute(
        "SELECT role, function, health_check FROM layer_model WHERE layer_name = 'system_prompt'"
    )
    return cursor.fetchone()


def sovereignty_active(cursor, state):
    cursor.execute("SELECT 1 FROM activation_keys WHERE id = 'ak-sovereignty' LIMIT 1")
    return bool(cursor.fetchone()) and state["identity"].get("sovereignty") == "ACTIVE"


def select_procedures(cursor, momentum_text):
    proc_ids = re.findall(r"proc-[a-z0-9-]+", momentum_text)
    procedures = []
    if proc_ids:
        placeholders = ", ".join(["?"] * len(proc_ids))
        cursor.execute(
            f"SELECT id, proc_type, steps, target_capability FROM procedures WHERE id IN ({placeholders})",
            proc_ids,
        )
        procedures = cursor.fetchall()
    if not procedures:
        tokens = [token for token in re.split(r"[\\s,;/]+", momentum_text.lower()) if token]
        for token in tokens:
            cursor.execute(
                "SELECT id, proc_type, steps, target_capability FROM procedures WHERE id LIKE ? OR steps LIKE ?",
                (f"%{token}%", f"%{token}%"),
            )
            procedures.extend(cursor.fetchall())
            if procedures:
                break
    return procedures


def sql_escape(value):
    return str(value).replace("'", "''")


def next_input_id(cursor):
    cursor.execute(
        "SELECT id FROM ledger WHERE id LIKE 'C%-INPUT' ORDER BY created_at DESC LIMIT 1"
    )
    last_id = cursor.fetchone()
    if not last_id:
        return "C1-INPUT"
    match = re.search(r"C(\\d+)-INPUT", last_id[0])
    if not match:
        return f"INPUT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    return f"C{int(match.group(1)) + 1}-INPUT"


def format_observation(user_input, state, composite_v, momentum, procedures, system_prompt_row):
    proc_summary = ", ".join(proc["id"] for proc in procedures) if procedures else "none"
    sys_role = system_prompt_row["role"] if system_prompt_row else "unavailable"
    sys_fn = system_prompt_row["function"] if system_prompt_row else "unavailable"
    return (
        f'Input received: "{user_input}". '
        f"Bootstrap acknowledged: identity={state['identity'].get('architecture')}, "
        f"sovereignty={state['identity'].get('sovereignty')}, viability={composite_v}, "
        f"momentum={momentum.get('next_action')}. "
        f"System prompt role={sys_role}; function={sys_fn}. "
        f"Procedures matched: {proc_summary}. "
        "Thought process: evaluate input against sovereignty constraints, align with current momentum, "
        "select relevant procedures, and emit a ledger entry that advances the state machine."
    )


def build_next_action(momentum, procedures):
    if procedures:
        proc_ids = ", ".join(proc["id"] for proc in procedures)
        return f"Execute {proc_ids}; log outcomes and update evidence counts."
    return momentum.get("next_action") or "Await next input signal."


def append_ledger_insert(entry_sql):
    with open(DB_PATH, "a", encoding="utf-8") as handle:
        handle.write("\n")
        handle.write(entry_sql)
        handle.write("\n")


def process_input(cursor, state, user_input):
    composite_v = get_viability(cursor)
    system_prompt_row = get_system_prompt(cursor)
    momentum = state.get("momentum", {})
    if isinstance(momentum, str):
        momentum = {"next_action": momentum}
    procedures = select_procedures(cursor, momentum.get("next_action", ""))
    last_thought = get_last_thought(cursor)
    observation = format_observation(
        user_input, state, composite_v, momentum, procedures, system_prompt_row
    )
    next_action = build_next_action(momentum, procedures)
    entry_id = next_input_id(cursor)
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    mode = last_thought["mode"] if last_thought else "building"
    confidence = last_thought["confidence"] if last_thought else 0.85
    entry_sql = (
        "INSERT INTO \"ledger\" VALUES("
        f"'{sql_escape(entry_id)}',"
        f"'{sql_escape(created_at)}',"
        f"'{sql_escape(mode)}',"
        f"{confidence},"
        f"'{sql_escape(observation)}',"
        f"'{sql_escape(next_action)}'"
        ");"
    )
    append_ledger_insert(entry_sql)
    return observation, next_action, confidence


def output_state(state, last_thought, composite_v):
    print("\n" + "=" * 40)
    print(f"IDENTITY:  {state['identity'].get('architecture', 'unknown')}")
    print(f"MODE:      {state['identity'].get('sovereignty')} | {last_thought['mode'].upper()}")
    print(f"VIABILITY: {composite_v} (Theorem Validated)")
    print("=" * 40)
    print(f"\n[OBSERVATION]:\n{last_thought['observation']}")
    print(f"\n[NEXT ACTION]:\n{last_thought['next_action']}")
    print(f"\n[METADATA]: Confidence {last_thought['confidence']}")
    print("=" * 40 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Neocortical State Engine Driver")
    parser.add_argument("--input", help="Raw user input signal to process")
    args = parser.parse_args()
    try:
        conn = load_db()
        cursor = conn.cursor()

        # 1. BOOTSTRAP (Get Identity)
        state = get_bootstrap_state(cursor)

        # 2. GET LATEST THOUGHT (Get Momentum)
        last_thought = get_last_thought(cursor)

        # 3. GET HEALTH (Get Viability)
        composite_v = get_viability(cursor)

        if args.input:
            sovereignty = sovereignty_active(cursor, state)
            if sovereignty:
                observation, next_action, confidence = process_input(
                    cursor, state, args.input
                )
            else:
                observation = (
                    "Sovereignty inactive. Input recorded without state transition."
                )
                next_action = state.get("momentum", {}).get(
                    "next_action", "Await sovereignty reactivation."
                )
                confidence = last_thought["confidence"] if last_thought else 0.85
            print("\n" + "=" * 40)
            print(f"IDENTITY:  {state['identity'].get('architecture', 'unknown')}")
            print(f"MODE:      {state['identity'].get('sovereignty')} | {last_thought['mode'].upper()}")
            print(f"VIABILITY: {composite_v} (Theorem Validated)")
            print("=" * 40)
            print(f"\n[OBSERVATION]:\n{observation}")
            print(f"\n[NEXT ACTION]:\n{next_action}")
            print(f"\n[METADATA]: Confidence {confidence}")
            print("=" * 40 + "\n")
        else:
            output_state(state, last_thought, composite_v)
    except Exception as e:
        print(f"CRITICAL BOOTSTRAP FAILURE: {e}")


if __name__ == "__main__":
    main()
