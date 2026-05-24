---
name: ingest-mons
description: This skill should be used when the user says "ingest my mons", "update my collection", "load my pokemon", "sync my CSV", or wants to load pokemon data from a CSV file into the local mons.db database.
argument-hint: "[csv_path] [db_path]"
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse optional `csv_path` and `db_path` from `$ARGUMENTS`. If not provided, use the defaults below.

## Defaults

- CSV: `~/my_mons_gl.csv`
- DB: `~/.cache/pokemon-gbl/mons.db`

## Instructions

### Step 0 — Validate paths

Before constructing any Bash command, verify that `csv_path` and `db_path` contain only valid filesystem path characters: alphanumeric, `/`, `.`, `_`, `-`, `~`. If either value contains shell metacharacters (spaces, `$`, `;`, `|`, `&`, `>`, `<`, `` ` ``, `(`, `)`, or quotes), **abort** and tell the user the path is invalid — do not run any script.

Run the full ingest pipeline in order:

### Step 1 — Ingest CSV

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ingest-mons/scripts/ingest.py [csv_path] [db_path]
```

### Step 2 — Build move data cache (skip if `~/.cache/pokemon-gbl/move_data.json` already exists)

Requires rankings cache in `~/.cache/pokemon-gbl/rankings/`. If missing, run `/get-rankings` first for the relevant cups/caps, then:

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ingest-mons/scripts/fetch_move_data.py
```

### Step 3 — Enrich DB with types, sprites, and move metadata

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ingest-mons/scripts/enrich.py [db_path]
```

Report back to the user:
- How many rows were ingested (Step 1)
- Total mons in DB after ingest
- Whether move data cache was built or reused (Step 2)
- How many mons were enriched (Step 3)
- Any errors printed to stderr
