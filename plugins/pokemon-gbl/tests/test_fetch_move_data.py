import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "ingest-mons" / "scripts"))
import fetch_move_data
from fetch_move_data import collect_moves, move_display_name, to_pokeapi_name


# --- move_display_name ---

def test_move_display_name_simple():
    assert move_display_name("METAL_CLAW") == "Metal Claw"

def test_move_display_name_strips_charge_prefix():
    assert move_display_name("AEGISLASH_CHARGE_SHADOW_BALL") == "Shadow Ball"

def test_move_display_name_single_word():
    assert move_display_name("SURF") == "Surf"


# --- to_pokeapi_name ---

def test_to_pokeapi_name():
    assert to_pokeapi_name("Metal Claw") == "metal-claw"

def test_to_pokeapi_name_multiword():
    assert to_pokeapi_name("Shadow Ball") == "shadow-ball"


# --- collect_moves ---

def test_collect_moves_reads_cache(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    rankings_dir.mkdir()
    cache_file = rankings_dir / "all_1500_overall.json"
    cache_file.write_text(json.dumps([
        {"speciesId": "registeel", "moveset": ["METAL_CLAW", "FLASH_CANNON", "FOCUS_BLAST"]},
        {"speciesId": "medicham", "moveset": ["COUNTER", "PSYCHIC", "ICE_PUNCH"]},
    ]))

    monkeypatch.setattr(fetch_move_data, "RANKINGS_CACHE", rankings_dir)
    moves = collect_moves()
    assert "Metal Claw" in moves
    assert "Flash Cannon" in moves
    assert "Counter" in moves

def test_collect_moves_strips_species_charge_prefix(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    rankings_dir.mkdir()
    cache_file = rankings_dir / "test.json"
    cache_file.write_text(json.dumps([
        {"speciesId": "aegislash", "moveset": ["METAL_CLAW", "AEGISLASH_CHARGE_SHADOW_BALL", "IRON_HEAD"]},
    ]))

    monkeypatch.setattr(fetch_move_data, "RANKINGS_CACHE", rankings_dir)
    moves = collect_moves()
    assert "Shadow Ball" in moves

def test_collect_moves_raises_when_no_cache(tmp_path, monkeypatch):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    monkeypatch.setattr(fetch_move_data, "RANKINGS_CACHE", empty_dir)
    with pytest.raises(SystemExit):
        collect_moves()


# --- main: uses overrides, skips existing, writes output ---

def test_main_uses_override_and_skips_existing(tmp_path, monkeypatch):
    rankings_dir = tmp_path / "rankings"
    rankings_dir.mkdir()
    output = tmp_path / "move_data.json"

    rankings_dir.joinpath("cup.json").write_text(json.dumps([
        {"speciesId": "foo", "moveset": ["RETURN", "FLASH_CANNON", "COUNTER"]},
    ]))

    # Pre-populate Counter so it is skipped
    output.write_text(json.dumps({"Counter": {"type": "fighting"}}))

    monkeypatch.setattr(fetch_move_data, "RANKINGS_CACHE", rankings_dir)
    monkeypatch.setattr(fetch_move_data, "OUTPUT", output)

    fetched = []

    def fake_fetch(api_name):
        fetched.append(api_name)
        return {"type": "steel"}

    monkeypatch.setattr(fetch_move_data, "fetch_move_info", fake_fetch)

    fetch_move_data.main()

    result = json.loads(output.read_text())
    assert result["Return"]["type"] == "normal"       # override applied
    assert result["Counter"]["type"] == "fighting"    # pre-existing preserved
    assert "flash-cannon" in fetched                  # fetched via API
    assert "return" not in fetched                    # not fetched (override)
    assert "counter" not in fetched                   # not fetched (pre-existing)
