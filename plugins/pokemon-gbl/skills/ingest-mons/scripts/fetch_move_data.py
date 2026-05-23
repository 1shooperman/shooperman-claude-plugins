#!/usr/bin/env python3
"""
Build ~/.cache/pokemon-gbl/move_data.json from the rankings cache.

Reads move IDs from ~/.cache/pokemon-gbl/rankings/*.json, resolves their
types via PokeAPI, and writes the result keyed by display name.

Run after /get-rankings has populated the rankings cache, and before enrich.py.
"""

import json
import re
import time
import urllib.request
from pathlib import Path

RANKINGS_CACHE = Path.home() / ".cache/pokemon-gbl/rankings"
OUTPUT = Path.home() / ".cache/pokemon-gbl/move_data.json"

_PREFIX = re.compile(r"^[A-Z]+_CHARGE_")

OVERRIDES: dict[str, str] = {
    "Aura Wheel Electric": "electric",
    "Aura Wheel Dark":     "dark",
    "Weather Ball Fire":   "fire",
    "Weather Ball Water":  "water",
    "Weather Ball Ice":    "ice",
    "Weather Ball Rock":   "rock",
    "Return":              "normal",
    "Frustration":         "normal",
    "Giga Impact":         "normal",
    "Hyper Beam":          "normal",
    "Last Resort":         "normal",
}


def move_display_name(move_id: str) -> str:
    move_id = _PREFIX.sub("", move_id)
    return move_id.replace("_", " ").title()


def to_pokeapi_name(display: str) -> str:
    return display.lower().replace(" ", "-")


def fetch_move_info(api_name: str) -> dict | None:
    url = f"https://pokeapi.co/api/v2/move/{api_name}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "pokemon-gbl-plugin"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return {
                "type": data["type"]["name"],
                "power": data.get("power"),
            }
    except Exception as e:
        print(f"  WARN: {api_name} → {e}")
        return None


def collect_moves() -> set[str]:
    moves: set[str] = set()
    cache_files = list(RANKINGS_CACHE.glob("*.json"))
    if not cache_files:
        print(f"ERROR: No rankings cache files found in {RANKINGS_CACHE}")
        print("Run /get-rankings first to populate the rankings cache.")
        raise SystemExit(1)
    for f in cache_files:
        for entry in json.loads(f.read_text()):
            for move_id in entry.get("moveset", []):
                moves.add(move_display_name(move_id))
    print(f"Found {len(moves)} unique moves across {len(cache_files)} cache files")
    return moves


def main():
    existing: dict[str, dict] = {}
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text())
        print(f"Loaded {len(existing)} existing entries from {OUTPUT}")

    moves = collect_moves()
    result = dict(existing)

    for display in sorted(moves):
        if display in result:
            continue
        if display in OVERRIDES:
            result[display] = {"type": OVERRIDES[display]}
            print(f"  override: {display} → {OVERRIDES[display]}")
            continue

        api = to_pokeapi_name(display)
        info = fetch_move_info(api)
        if info:
            result[display] = info
            print(f"  {display} → {info['type']}")
        else:
            print(f"  MISSING: {display}")
        time.sleep(0.2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(dict(sorted(result.items())), indent=2))
    print(f"\n✓ {len(result)} moves → {OUTPUT}")


if __name__ == "__main__":
    main()
