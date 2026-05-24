import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "ingest-mons" / "scripts"))
from ingest import (
    ENRICHED_COLUMNS,
    bool_val,
    ensure_db,
    int_or_none,
    ingest,
    load_existing_enriched,
    parse_name,
)


# --- parse_name ---

def test_parse_name_plain():
    assert parse_name("Registeel") == ("Registeel", None, False)

def test_parse_name_alolan():
    assert parse_name("Muk (Alolan)") == ("Muk", "Alolan", False)

def test_parse_name_shadow():
    assert parse_name("Registeel (Shadow)") == ("Registeel", None, True)

def test_parse_name_alolan_shadow():
    assert parse_name("Marowak (Alolan Shadow)") == ("Marowak", "Alolan", True)

def test_parse_name_unknown_parens_treated_as_species():
    species, form, shadow = parse_name("Mr. Mime (Galarian)")
    assert species == "Mr. Mime"
    assert form == "Galarian"
    assert shadow is False

def test_parse_name_unrecognised_tag():
    species, form, shadow = parse_name("Castform (Sunny)")
    assert species == "Castform (Sunny)"
    assert form is None
    assert shadow is False


# --- bool_val / int_or_none ---

def test_bool_val_true():
    assert bool_val("true") == 1
    assert bool_val("True") == 1

def test_bool_val_false():
    assert bool_val("false") == 0
    assert bool_val("") == 0

def test_int_or_none_value():
    assert int_or_none("1499") == 1499

def test_int_or_none_empty():
    assert int_or_none("") is None


# --- ensure_db ---

def test_ensure_db_creates_schema(tmp_path):
    conn = ensure_db(tmp_path / "mons.db")
    cols = {row[1] for row in conn.execute("PRAGMA table_info(mons)").fetchall()}
    for col, _ in ENRICHED_COLUMNS:
        assert col in cols, f"Missing column: {col}"
    conn.close()

def test_ensure_db_migrates_lean_db(tmp_path):
    db = tmp_path / "mons.db"
    # Create a lean DB without enriched columns
    conn = sqlite3.connect(db)
    conn.execute("""
        CREATE TABLE mons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_name TEXT NOT NULL, species TEXT NOT NULL, form TEXT,
            shadow INTEGER NOT NULL DEFAULT 0, purified INTEGER NOT NULL DEFAULT 0,
            cp INTEGER, gl_rank INTEGER, fast_move TEXT, charge_move_1 TEXT,
            charge_move_2 TEXT, legacy_move INTEGER NOT NULL DEFAULT 0,
            legacy_move_name TEXT, has_return INTEGER NOT NULL DEFAULT 0, notes TEXT
        )
    """)
    conn.execute("INSERT INTO mons (raw_name, species) VALUES ('Registeel', 'Registeel')")
    conn.commit()
    conn.close()

    conn = ensure_db(db)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(mons)").fetchall()}
    for col, _ in ENRICHED_COLUMNS:
        assert col in cols
    # Existing row preserved
    assert conn.execute("SELECT COUNT(*) FROM mons").fetchone()[0] == 1
    conn.close()


# --- load_existing_enriched ---

def test_load_existing_enriched_empty(tmp_path):
    conn = ensure_db(tmp_path / "mons.db")
    assert load_existing_enriched(conn) == {}
    conn.close()

def test_load_existing_enriched_returns_data(tmp_path):
    conn = ensure_db(tmp_path / "mons.db")
    conn.execute(
        """INSERT INTO mons (raw_name, species, cp, notes, fast_move, types, sprite_url)
           VALUES ('Registeel', 'Registeel', 1484, '', 'Metal Claw', '["steel"]', 'http://x.png')"""
    )
    conn.commit()

    result = load_existing_enriched(conn)
    key = ("Registeel", 1484, "")
    assert key in result
    assert result[key]["fast_move"] == "Metal Claw"
    assert result[key]["types"] == '["steel"]'
    assert result[key]["sprite_url"] == "http://x.png"
    conn.close()


# --- ingest round-trip ---

CSV_CONTENT = """\
name,shadow,purified,cp,gl_rank,legacy_move,has_return,notes
Registeel,false,false,1484,1,false,false,
Medicham,false,false,1499,3,false,false,
Marowak (Alolan Shadow),true,false,1477,12,true,false,
"""

def test_ingest_basic(tmp_path):
    csv_file = tmp_path / "mons.csv"
    csv_file.write_text(CSV_CONTENT)
    db = tmp_path / "mons.db"

    inserted, total = ingest(csv_file, db)
    assert inserted == 3
    assert total == 3

def test_ingest_preserves_enriched_on_reingest(tmp_path):
    csv_file = tmp_path / "mons.csv"
    csv_file.write_text(CSV_CONTENT)
    db = tmp_path / "mons.db"

    ingest(csv_file, db)

    # Manually set enriched data
    conn = sqlite3.connect(db)
    conn.execute(
        "UPDATE mons SET types=?, sprite_url=?, fast_move=? WHERE raw_name=?",
        ('["steel"]', "http://registeel.png", "Metal Claw", "Registeel"),
    )
    conn.commit()
    conn.close()

    # Re-ingest — enriched data should survive
    ingest(csv_file, db)

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM mons WHERE raw_name='Registeel'").fetchone()
    assert row["types"] == '["steel"]'
    assert row["sprite_url"] == "http://registeel.png"
    assert row["fast_move"] == "Metal Claw"
    conn.close()

def test_ingest_shadow_from_name(tmp_path):
    csv_file = tmp_path / "mons.csv"
    csv_file.write_text(CSV_CONTENT)
    db = tmp_path / "mons.db"
    ingest(csv_file, db)

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM mons WHERE species='Marowak'").fetchone()
    assert row["shadow"] == 1
    assert row["form"] == "Alolan"
    conn.close()
