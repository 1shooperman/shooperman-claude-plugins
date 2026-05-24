import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "ingest-mons" / "scripts"))
import enrich
from enrich import pokeapi_name, sprite_url


# --- pokeapi_name ---

def test_pokeapi_name_plain():
    assert pokeapi_name("Registeel", None) == "registeel"

def test_pokeapi_name_alolan():
    assert pokeapi_name("Muk", "Alolan") == "muk-alola"

def test_pokeapi_name_galarian():
    assert pokeapi_name("Weezing", "Galarian") == "weezing-galar"

def test_pokeapi_name_strips_apostrophe():
    assert pokeapi_name("Farfetch'd", None) == "farfetchd"


# --- sprite_url ---

def test_sprite_url_plain():
    assert sprite_url("Registeel", None) == "https://img.pokemondb.net/sprites/home/normal/registeel.png"

def test_sprite_url_alolan():
    assert sprite_url("Marowak", "Alolan") == "https://img.pokemondb.net/sprites/home/normal/marowak-alolan.png"

def test_sprite_url_galarian():
    assert sprite_url("Stunfisk", "Galarian") == "https://img.pokemondb.net/sprites/home/normal/stunfisk-galarian.png"


# --- main (integration, no network) ---

def _make_db(db_path: Path, rows: list[dict]):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE mons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_name TEXT, species TEXT, form TEXT,
            fast_move TEXT, charge_move_1 TEXT, charge_move_2 TEXT,
            fast_move_type TEXT, fast_move_turns INTEGER,
            charge_move_1_type TEXT, charge_move_1_energy INTEGER, charge_move_1_attacks INTEGER,
            charge_move_2_type TEXT, charge_move_2_energy INTEGER, charge_move_2_attacks INTEGER,
            types TEXT, sprite_url TEXT
        )
    """)
    for r in rows:
        conn.execute(
            """INSERT INTO mons (raw_name, species, form, fast_move, charge_move_1, charge_move_2)
               VALUES (:raw_name, :species, :form, :fast_move, :charge_move_1, :charge_move_2)""",
            r,
        )
    conn.commit()
    conn.close()


MOVE_DATA = {
    "Metal Claw": {"type": "steel", "turns": 3, "energy": 0, "energyGain": 8},
    "Flash Cannon": {"type": "steel", "turns": 1, "energy": 70, "energyGain": 0},
    "Focus Blast": {"type": "fighting", "turns": 1, "energy": 75, "energyGain": 0},
}


def test_enrich_populates_fields(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    move_data_file = tmp_path / "move_data.json"
    move_data_file.write_text(json.dumps(MOVE_DATA))

    _make_db(db, [{
        "raw_name": "Registeel", "species": "Registeel", "form": None,
        "fast_move": "Metal Claw", "charge_move_1": "Flash Cannon", "charge_move_2": "Focus Blast",
    }])

    monkeypatch.setattr(enrich, "MOVE_DATA", move_data_file)
    monkeypatch.setattr(enrich, "DEFAULT_DB", db)

    fake_types = ["steel"]
    monkeypatch.setattr(enrich, "fetch_types", lambda _: fake_types)

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["enrich.py"])
    enrich.main()

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM mons WHERE species='Registeel'").fetchone()
    assert row["fast_move_type"] == "steel"
    assert row["fast_move_turns"] == 3
    assert row["charge_move_1_type"] == "steel"
    assert row["charge_move_1_energy"] == 70
    assert row["charge_move_1_attacks"] == 9   # ceil(70 / 8)
    assert row["charge_move_2_type"] == "fighting"
    assert json.loads(row["types"]) == ["steel"]
    assert "registeel" in row["sprite_url"]
    conn.close()


def test_enrich_uses_sprite_override(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    move_data_file = tmp_path / "move_data.json"
    move_data_file.write_text("{}")

    _make_db(db, [{
        "raw_name": "Shaymin (Sky)", "species": "Shaymin", "form": "Sky",
        "fast_move": None, "charge_move_1": None, "charge_move_2": None,
    }])

    monkeypatch.setattr(enrich, "MOVE_DATA", move_data_file)
    monkeypatch.setattr(enrich, "DEFAULT_DB", db)
    monkeypatch.setattr(enrich, "fetch_types", lambda _: ["grass", "flying"])

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["enrich.py"])
    enrich.main()

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM mons WHERE species='Shaymin'").fetchone()
    assert row["sprite_url"] == enrich.SPRITE_OVERRIDES["Shaymin__Sky"]
    conn.close()


def test_enrich_uses_type_override(tmp_path, monkeypatch):
    db = tmp_path / "mons.db"
    move_data_file = tmp_path / "move_data.json"
    move_data_file.write_text("{}")

    _make_db(db, [{
        "raw_name": "Aegislash", "species": "Aegislash", "form": "None",
        "fast_move": None, "charge_move_1": None, "charge_move_2": None,
    }])

    monkeypatch.setattr(enrich, "MOVE_DATA", move_data_file)
    monkeypatch.setattr(enrich, "DEFAULT_DB", db)
    # fetch_types should NOT be called for overridden species
    called = []
    monkeypatch.setattr(enrich, "fetch_types", lambda api: called.append(api) or [])

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["enrich.py"])
    enrich.main()

    assert called == [], "fetch_types should not be called for TYPE_OVERRIDES species"

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM mons").fetchone()
    assert json.loads(row["types"]) == ["steel", "ghost"]
    conn.close()
