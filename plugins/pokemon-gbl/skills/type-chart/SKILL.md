---
name: type-chart
description: This skill should be used when the user asks about Pokemon GO type matchups, weaknesses, resistances, or effectiveness (e.g. "what beats dark/steel", "type chart for fire", "is water good against ground").
allowed-tools: [Bash(python3 *query_types.py), Read, Agent(agent-build-cache)]
argument-hint: "<type1> [type2]"
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `type1` and optional `type2` from `$ARGUMENTS`. If no arguments are provided, ask the user to specify one or two type names.

## Cache file

If `~/.cache/pokemon-gbl/type_chart.json` does not exist, invoke the `agent-build-cache` agent to build it before proceeding.

## Instructions

Run a local lookup against the GO-specific type chart (multipliers: 1.6x / 0.625x / 0.39x). Returns defender matchups (combined for dual types) and attacker matchups for each type. No external calls needed.

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/type-chart/scripts/query_types.py [type1] [type2]
```

## Data

`~/.cache/pokemon-gbl/type_chart.json` — rebuilt by `agent-build-cache` when missing; no expiration.
