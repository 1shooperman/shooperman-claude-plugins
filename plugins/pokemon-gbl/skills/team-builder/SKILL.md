---
name: team-builder
description: Builds and evaluates GBL teams for a given cup and CP cap. Activated when the user asks to "build a team", "suggest a team", or "help me with team building" for Pokemon GO Battle League.
allowed-tools: [Bash(sqlite3 *), Skill(get-rankings)]
argument-hint: "<cup> <cp>"
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `cup` and `cp` from `$ARGUMENTS` (e.g. `jungle 1500`). If either is missing, ask for them before proceeding.

## Instructions

Always ground team suggestions in the current meta by invoking the `get-rankings` skill first. Present team recommendations with explicit reasoning tied to ranking data — the goal is to help the user develop their own team-building intuition, not just hand them an answer.

Structure every response as:
1. Meta context — what the top threats and cores are in this cup
2. Recommended team with role for each slot (lead / safe switch / closer)
3. Why each pick addresses the meta
4. One or two alternatives if the top picks are expensive or unavailable

## Data

Reference the local `.cache` folders (at `$CLAUDE_PLUGIN_ROOT/skills/get-rankings/.cache/`) for cached cup rankings. If the cache is missing or stale, use `get-rankings` to refresh it.
