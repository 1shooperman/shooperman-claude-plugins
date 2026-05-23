# pokemon-gbl

A Claude Code plugin for building and evaluating Pokemon GO Battle League (GBL) teams using live rankings from pvpoke.com, local type chart data, and your personal pokemon collection.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `team-builder` | `/team-builder <cup> <cp>` | Build or evaluate a GBL team for the given cup and CP cap |
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

## Data Sources

- **pvpoke.com** — rankings JSON (cached locally for 48 hours at `skills/get-rankings/.cache/`)
- **pokemondb.net** — GO type matchup chart (fetched once, cached indefinitely at `~/.cache/pokemon-gbl/type_chart.json`)
- **pokemongo.com/en/news** — GO Battle League news for move change context
- **mons.db** — personal pokemon collection (SQLite, written by `ingest-mons`, queried via the `mons-db` MCP server at `~/.cache/pokemon-gbl/mons.db`)

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
