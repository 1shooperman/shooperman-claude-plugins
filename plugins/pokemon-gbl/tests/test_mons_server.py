import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "mcp"))
import mons_server


def _make_db(db_path: Path, rows: list[dict]):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE mons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_name TEXT, species TEXT, form TEXT,
            shadow INTEGER DEFAULT 0, purified INTEGER DEFAULT 0,
            cp INTEGER, gl_rank INTEGER,
            fast_move TEXT, charge_move_1 TEXT, charge_move_2 TEXT,
            legacy_move INTEGER DEFAULT 0, legacy_move_name TEXT,
            has_return INTEGER DEFAULT 0, notes TEXT,
            fast_move_type TEXT, fast_move_turns INTEGER,
            charge_move_1_type TEXT, charge_move_1_energy INTEGER, charge_move_1_attacks INTEGER,
            charge_move_2_type TEXT, charge_move_2_energy INTEGER, charge_move_2_attacks INTEGER,
            types TEXT, sprite_url TEXT
        )
    """)
    for r in rows:
        conn.execute(
            "INSERT INTO mons (raw_name, species, form, types) VALUES (:raw_name, :species, :form, :types)",
            r,
        )
    conn.commit()
    conn.close()


def test_row_to_dict_parses_types_to_list(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    _make_db(db, [{"raw_name": "Registeel", "species": "Registeel", "form": None, "types": '["steel"]'}])
    monkeypatch.setattr(mons_server, "DB_PATH", str(db))

    with mons_server.db() as conn:
        row = conn.execute("SELECT * FROM mons").fetchone()
    result = mons_server.row_to_dict(row)
    assert result["types"] == ["steel"]


def test_row_to_dict_returns_empty_list_for_null_types(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    _make_db(db, [{"raw_name": "Registeel", "species": "Registeel", "form": None, "types": None}])
    monkeypatch.setattr(mons_server, "DB_PATH", str(db))

    with mons_server.db() as conn:
        row = conn.execute("SELECT * FROM mons").fetchone()
    result = mons_server.row_to_dict(row)
    assert result["types"] == []


def test_row_to_dict_returns_empty_list_for_malformed_types(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    _make_db(db, [{"raw_name": "Registeel", "species": "Registeel", "form": None, "types": "not-json"}])
    monkeypatch.setattr(mons_server, "DB_PATH", str(db))

    with mons_server.db() as conn:
        row = conn.execute("SELECT * FROM mons").fetchone()
    result = mons_server.row_to_dict(row)
    assert result["types"] == []


def test_row_to_dict_parses_dual_types(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    _make_db(db, [{"raw_name": "Muk (Alolan)", "species": "Muk", "form": "Alolan", "types": '["poison","dark"]'}])
    monkeypatch.setattr(mons_server, "DB_PATH", str(db))

    with mons_server.db() as conn:
        row = conn.execute("SELECT * FROM mons").fetchone()
    result = mons_server.row_to_dict(row)
    assert result["types"] == ["poison", "dark"]
