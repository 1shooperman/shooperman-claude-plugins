#!/usr/bin/env python3
"""
Populate enriched fields in mons.db from move_data.json and PokeAPI.

Adds/updates: fast_move_type, fast_move_turns, charge_move_*_type/energy/attacks,
types (JSON array), and sprite_url.

Run after ingest.py and fetch_move_data.py.
"""

import json
import math
import sqlite3
import time
import urllib.request
from pathlib import Path

DEFAULT_DB = Path.home() / ".cache/pokemon-gbl/mons.db"
MOVE_DATA = Path.home() / ".cache/pokemon-gbl/move_data.json"

SPRITE_OVERRIDES: dict[str, str] = {
    "Shaymin__Sky":          "https://img.pokemondb.net/sprites/scarlet-violet/normal/shaymin-sky.png",
    "Wormadam__Trash Cloak": "https://img.pokemondb.net/sprites/home/normal/wormadam-trash.png",
}

TYPE_OVERRIDES: dict[str, list[str]] = {
    "Aegislash__None":        ["steel", "ghost"],
    "Jellicent__None":        ["water", "ghost"],
    "Gourgeist__None":        ["ghost", "grass"],
    "Morpeko__None":          ["dark", "electric"],
    "Wormadam__Trash Cloak":  ["bug", "steel"],
    "Shaymin__Sky":           ["grass", "flying"],
}


def pokeapi_name(species: str, form: str | None) -> str:
    n = species.lower().replace(" ", "-").replace("'", "").replace(".", "")
    if form == "Alolan":
        return f"{n}-alola"
    if form == "Galarian":
        return f"{n}-galar"
    if form == "Male":
        return f"{n}-male"
    if form == "Female":
        return f"{n}-female"
    return n


def sprite_url(species: str, form: str | None) -> str:
    n = species.lower().replace(" ", "-").replace("'", "").replace(".", "")
    if form == "Alolan":
        n = f"{n}-alolan"
    elif form == "Galarian":
        n = f"{n}-galarian"
    return f"https://img.pokemondb.net/sprites/home/normal/{n}.png"


def fetch_types(api_name: str) -> list[str] | None:
    url = f"https://pokeapi.co/api/v2/pokemon/{api_name}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pokemon-gbl-plugin"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            types_list = data.get("types")
            if types_list is None:
                print(f"  WARN types {api_name} → missing 'types' field in response")
                return None
            return [t.get("type", {}).get("name") for t in types_list if t.get("type", {}).get("name")]
    except Exception as e:
        print(f"  WARN types {api_name} → {e}")
        return None


def main():
    import sys
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB

    if not db_path.exists():
        print(f"ERROR: DB not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    if not MOVE_DATA.exists():
        print(f"ERROR: move_data.json not found at {MOVE_DATA}", file=sys.stderr)
        print("Run fetch_move_data.py first.", file=sys.stderr)
        sys.exit(1)

    try:
        move_data: dict = json.loads(MOVE_DATA.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: corrupt move_data.json at {MOVE_DATA}: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(move_data)} move entries")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Clear previously-poisoned rows so they are re-fetched this run.
    conn.execute("UPDATE mons SET types = NULL WHERE types = '[]'")
    conn.commit()

    rows = conn.execute("SELECT * FROM mons").fetchall()

    type_cache: dict[str, list[str] | None] = {}
    updated = 0

    for row in rows:
        species, form = row["species"], row["form"]
        key = f"{species}__{form}"

        if key not in type_cache:
            if key in TYPE_OVERRIDES:
                type_cache[key] = TYPE_OVERRIDES[key]
            else:
                api = pokeapi_name(species, form)
                print(f"  fetching types: {api}…")
                type_cache[key] = fetch_types(api)
                time.sleep(0.25)

        types = type_cache[key]
        if types is None:
            print(f"ERROR: types unresolved for {key} — add to TYPE_OVERRIDES or fix pokeapi_name()", file=sys.stderr)
            conn.close()
            sys.exit(1)

        url = SPRITE_OVERRIDES.get(key) or sprite_url(species, form)

        def move_info(name: str | None) -> dict:
            if not name:
                return {"type": None, "turns": None, "energy": None, "energyGain": None}
            m = move_data.get(name, {})
            return {
                "type":       m.get("type"),
                "turns":      m.get("turns"),
                "energy":     m.get("energy"),
                "energyGain": m.get("energyGain"),
            }

        fm  = move_info(row["fast_move"])
        cm1 = move_info(row["charge_move_1"])
        cm2 = move_info(row["charge_move_2"])

        def attacks_to_charge(charge_energy):
            eg = fm["energyGain"]
            if charge_energy and eg:
                return math.ceil(charge_energy / eg)
            return None

        conn.execute(
            """UPDATE mons SET
                fast_move_type=?, fast_move_turns=?,
                charge_move_1_type=?, charge_move_1_energy=?, charge_move_1_attacks=?,
                charge_move_2_type=?, charge_move_2_energy=?, charge_move_2_attacks=?,
                types=?, sprite_url=?
               WHERE id=?""",
            (
                fm["type"], fm["turns"],
                cm1["type"], cm1["energy"], attacks_to_charge(cm1["energy"]),
                cm2["type"], cm2["energy"], attacks_to_charge(cm2["energy"]),
                json.dumps(types),
                url,
                row["id"],
            ),
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"\n✓ Enriched {updated} mons in {db_path}")



if __name__ == "__main__":
    main()
