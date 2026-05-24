# pokemon-gbl

A Claude Code plugin for building and evaluating Pokemon GO Battle League (GBL) teams using live rankings from pvpoke.com, local type chart data, and your personal pokemon collection.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `team-builder` | `/team-builder <cup> <cp>` | Build or evaluate a GBL team for the given cup and CP cap — responses voiced as [HomeSliceHenry](https://www.youtube.com/@HomeSliceHenry) |
| `type-chart` | `/type-chart <type1> [type2]` | Look up GO type effectiveness for a single or dual type |
| `quiz` | `/quiz [n]` | Quiz yourself on type matchups; optionally run `n` questions in a row |
| `ingest-mons` | `/ingest-mons [csv_path] [db_path]` | Load your personal pokemon collection from a CSV into the local mons.db |

## Usage

```
/team-builder great 1500
/team-builder jungle 1500
/type-chart dark steel
/type-chart fire
/quiz
/quiz 5
/ingest-mons
/ingest-mons ~/my_export.csv
```

## CSV Format

The `ingest-mons` skill expects a CSV with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Pokemon display name. Append `(Alolan)`, `(Galarian)`, etc. for regional forms; append `(Shadow)` or `(Alolan Shadow)` for shadow/form combos. |
| `shadow` | bool | `true` / `false` |
| `purified` | bool | `true` / `false` |
| `cp` | integer | CP at time of export |
| `gl_rank` | integer | Great League rank (leave blank if unranked) |
| `legacy_move` | bool | `true` if the pokemon has a legacy/event move |
| `has_return` | bool | `true` if it has Return (purified move) |
| `notes` | string | Free-form notes (optional) |

Example rows:
```
name,shadow,purified,cp,gl_rank,legacy_move,has_return,notes
Registeel,false,false,1484,1,false,false,
Medicham,false,false,1499,3,false,false,
Marowak (Alolan Shadow),true,false,1477,12,true,false,Shadow Bone legacy
Swampert,false,true,1488,5,false,true,
```

After ingesting, the skill also:
1. Fetches move type metadata (from PokeAPI, cached at `~/.cache/pokemon-gbl/move_data.json`) — requires the rankings cache to exist first (`/get-rankings`)
2. Enriches each mon with types, sprite URL, and move type/energy/turn counts

> **Note:** Types and sprite URLs are not preserved across re-ingests. Running `/ingest-mons` clears them; the enrich step (Step 3) must run after every ingest to repopulate them. If enrich exits with an unresolved types error, there are two remedies:
> - **Form stored as None but a form-specific override exists** — update the DB row directly: `UPDATE mons SET form='<Form Name>' WHERE species='<Species>';`, then re-run enrich. Use this for alternate forms (e.g. `Trash Cloak`, `Sky`, `Male`/`Female`).
> - **No override and no valid PokeAPI slug** — add the mon to `TYPE_OVERRIDES` in `enrich.py` with the key `"<Species>__<form or None>"`. Gender forms (`Male`/`Female`) are handled automatically by `pokeapi_name` via the `meowstic-male` / `meowstic-female` pattern.

## Data Sources

- **[PvPoke](https://pvpoke.com)** — rankings JSON (cached locally for 48 hours at `~/.cache/pokemon-gbl/rankings/`)
- **[PokemonDB](https://pokemondb.net)** — GO type matchup chart and sprite images (type chart fetched once, cached indefinitely at `~/.cache/pokemon-gbl/type_chart.json`)
- **[PokeAPI](https://pokeapi.co)** — Pokemon types and move metadata (fetched on first enrich, cached in `~/.cache/pokemon-gbl/move_data.json`)
- **[Pokemon GO](https://pokemongo.com/en/news)** — GO Battle League news for move change context
- **mons.db** — personal pokemon collection (SQLite, written by `ingest-mons`, queried via the `mons-db` MCP server at `~/.cache/pokemon-gbl/mons.db`)

## Attribution

This plugin relies on data from third-party sources. All data belongs to their respective owners:

- Rankings data provided by **[PvPoke](https://pvpoke.com)** — an open-source GO Battle League ranking and team-building tool
- Type chart and sprite images provided by **[PokemonDB](https://pokemondb.net)**
- Pokemon species and move data provided by **[PokeAPI](https://pokeapi.co)** — a free, open RESTful API
- Pokemon GO is a trademark of **Niantic, Inc.** Pokémon and all related names are trademarks of **Nintendo / Creatures Inc. / GAME FREAK inc.**

This plugin is not affiliated with or endorsed by any of the above.

The `team-builder` skill persona is modeled after **[HomeSliceHenry](https://www.youtube.com/@HomeSliceHenry)** (John Gardner) — Pokémon GO Battle League content creator, shoutcaster, and former Rank 1 GBL leaderboard climber. Used with admiration; not affiliated or endorsed.

## MCP Server

The plugin ships a local MCP server (`mcp/mons_server.py`) that exposes your collection to skills like `team-builder`. It is configured automatically via `.mcp.json` and requires the DB to be populated via `ingest-mons` first.

Available tools: `list_mons`, `search_mons`, `get_mon`, `collection_summary`

## Prerequisites

- Python 3.x (for scripts in `skills/*/scripts/` and the MCP server)
- A CSV export of your GO collection at `~/my_mons_gl.csv` (default path for `ingest-mons`)

## Install

```bash
claude plugin install pokemon-gbl
```
