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
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_name         TEXT NOT NULL,
    species          TEXT NOT NULL,
    form             TEXT,
    shadow           INTEGER NOT NULL DEFAULT 0,
    purified         INTEGER NOT NULL DEFAULT 0,
    cp               INTEGER,
    gl_rank          INTEGER,
    fast_move        TEXT,
    charge_move_1    TEXT,
    charge_move_2    TEXT,
    legacy_move      INTEGER NOT NULL DEFAULT 0,
    legacy_move_name TEXT,
    has_return       INTEGER NOT NULL DEFAULT 0,
    notes            TEXT
);
"""

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


def load_existing_moves(conn) -> dict:
    """Return dict keyed by (raw_name, cp, notes) → move tuple, taking first match."""
    rows = conn.execute(
        "SELECT raw_name, cp, notes, fast_move, charge_move_1, charge_move_2, legacy_move_name FROM mons"
    ).fetchall()
    moves = {}
    for row in rows:
        key = (row[0], row[1], row[2] or "")
        if key not in moves:
            moves[key] = (row[3], row[4], row[5], row[6])
    return moves


def ensure_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def ingest(csv_path: Path, db_path: Path):
    conn = ensure_db(db_path)
    conn.row_factory = sqlite3.Row

    existing_moves = load_existing_moves(conn)

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
            fm, cm1, cm2, lm_name = existing_moves.get(key, (None, None, None, None))

            rows.append((
                raw_name, species, form, shadow, purified, cp, gl_rank,
                fm, cm1, cm2, legacy_move, lm_name, has_return, notes,
            ))

    with conn:
        conn.execute("DELETE FROM mons")
        conn.executemany(
            """INSERT INTO mons
               (raw_name, species, form, shadow, purified, cp, gl_rank,
                fast_move, charge_move_1, charge_move_2,
                legacy_move, legacy_move_name, has_return, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
