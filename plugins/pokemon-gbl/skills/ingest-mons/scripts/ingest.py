#!/usr/bin/env python3
"""Ingest my_mons_gl.csv into mons.db, preserving existing move data."""

import csv
import re
import sqlite3
import sys
from pathlib import Path

DEFAULT_CSV = Path.home() / "my_mons_gl.csv"
DEFAULT_DB = Path.home() / ".cache/pokemon-gbl/mons.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS mons (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name              TEXT NOT NULL,
    species               TEXT NOT NULL,
    form                  TEXT,
    shadow                INTEGER NOT NULL DEFAULT 0,
    purified              INTEGER NOT NULL DEFAULT 0,
    cp                    INTEGER,
    gl_rank               INTEGER,
    fast_move             TEXT,
    fast_move_type        TEXT,
    fast_move_turns       INTEGER,
    charge_move_1         TEXT,
    charge_move_1_type    TEXT,
    charge_move_1_energy  INTEGER,
    charge_move_1_attacks INTEGER,
    charge_move_2         TEXT,
    charge_move_2_type    TEXT,
    charge_move_2_energy  INTEGER,
    charge_move_2_attacks INTEGER,
    legacy_move           INTEGER NOT NULL DEFAULT 0,
    legacy_move_name      TEXT,
    has_return            INTEGER NOT NULL DEFAULT 0,
    notes                 TEXT,
    types                 TEXT,
    sprite_url            TEXT
);
"""

ENRICHED_COLUMNS = [
    ("fast_move_type",        "TEXT"),
    ("fast_move_turns",       "INTEGER"),
    ("charge_move_1_type",    "TEXT"),
    ("charge_move_1_energy",  "INTEGER"),
    ("charge_move_1_attacks", "INTEGER"),
    ("charge_move_2_type",    "TEXT"),
    ("charge_move_2_energy",  "INTEGER"),
    ("charge_move_2_attacks", "INTEGER"),
    ("types",                 "TEXT"),
    ("sprite_url",            "TEXT"),
]

FORM_KEYWORDS = {"Alolan", "Galarian", "Hisuian", "Paldean", "Unovan"}


def parse_name(raw: str):
    """Return (species, form, shadow_from_name)."""
    # "(Form Shadow)" e.g. "Marowak (Alolan Shadow)"
    m = re.match(r"^(.+?)\s+\((\w+)\s+Shadow\)\s*$", raw)
    if m:
        return m.group(1).strip(), m.group(2), True

    # "(Shadow)" e.g. "Registeel (Shadow)"
    m = re.match(r"^(.+?)\s+\(Shadow\)\s*$", raw)
    if m:
        return m.group(1).strip(), None, True

    # "(Form)" e.g. "Muk (Alolan)"
    m = re.match(r"^(.+?)\s+\((\w+)\)\s*$", raw)
    if m:
        word = m.group(2)
        if word in FORM_KEYWORDS:
            return m.group(1).strip(), word, False
        # Treat unrecognised parens as part of species name
        return raw.strip(), None, False

    return raw.strip(), None, False


def bool_val(s: str) -> int:
    return 1 if s.strip().lower() == "true" else 0


def int_or_none(s: str):
    s = s.strip()
    return int(s) if s else None


def load_existing_enriched(conn) -> dict:
    """Return dict keyed by (raw_name, cp, notes) → enriched fields tuple, taking first match."""
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(mons)").fetchall()}
    enriched_names = [col for col, _ in ENRICHED_COLUMNS if col in existing_cols]
    if not enriched_names:
        return {}

    move_cols = "fast_move, charge_move_1, charge_move_2, legacy_move_name"
    enriched_cols = ", ".join(enriched_names)
    rows = conn.execute(
        f"SELECT raw_name, cp, notes, {move_cols}, {enriched_cols} FROM mons"
    ).fetchall()
    result = {}
    for row in rows:
        key = (row[0], row[1], row[2] or "")
        if key not in result:
            result[key] = {
                "fast_move": row[3],
                "charge_move_1": row[4],
                "charge_move_2": row[5],
                "legacy_move_name": row[6],
                **{name: row[7 + i] for i, name in enumerate(enriched_names)},
            }
    return result


def ensure_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    # Migrate existing DB: add enriched columns if absent
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(mons)").fetchall()}
    for col, col_type in ENRICHED_COLUMNS:
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE mons ADD COLUMN {col} {col_type}")
    conn.commit()
    return conn


def ingest(csv_path: Path, db_path: Path):
    conn = ensure_db(db_path)
    conn.row_factory = sqlite3.Row

    existing = load_existing_enriched(conn)
    enriched_names = [col for col, _ in ENRICHED_COLUMNS]

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_name = r["name"].strip()
            species, form, shadow_from_name = parse_name(raw_name)
            shadow = bool_val(r["shadow"]) or (1 if shadow_from_name else 0)
            purified = bool_val(r["purified"])
            cp = int_or_none(r["cp"])
            gl_rank = int_or_none(r["gl_rank"])
            legacy_move = bool_val(r["legacy_move"])
            has_return = bool_val(r["has_return"])
            notes = r.get("notes", "").strip()

            key = (raw_name, cp, notes)
            prior = existing.get(key, {})

            rows.append((
                raw_name, species, form, shadow, purified, cp, gl_rank,
                prior.get("fast_move"),
                prior.get("charge_move_1"),
                prior.get("charge_move_2"),
                legacy_move,
                prior.get("legacy_move_name"),
                has_return,
                notes,
                *[prior.get(col) for col in enriched_names],
            ))

    enriched_col_list = ", ".join(enriched_names)
    placeholders = ", ".join(["?"] * (14 + len(enriched_names)))

    with conn:
        conn.execute("DELETE FROM mons")
        conn.executemany(
            f"""INSERT INTO mons
               (raw_name, species, form, shadow, purified, cp, gl_rank,
                fast_move, charge_move_1, charge_move_2,
                legacy_move, legacy_move_name, has_return, notes,
                {enriched_col_list})
               VALUES ({placeholders})""",
            rows,
        )

    total = conn.execute("SELECT COUNT(*) FROM mons").fetchone()[0]
    conn.close()
    return len(rows), total


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    db_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DB

    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    inserted, total = ingest(csv_path, db_path)
    print(f"Ingested {inserted} rows from {csv_path.name}")
    print(f"Total mons in DB: {total}")


if __name__ == "__main__":
    main()
