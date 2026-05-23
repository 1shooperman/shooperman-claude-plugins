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

Run the ingest script with the resolved paths:

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/ingest-mons/scripts/ingest.py [csv_path] [db_path]
```

Report back to the user:
- How many rows were ingested
- Total mons in DB after ingest
- Any errors printed to stderr
