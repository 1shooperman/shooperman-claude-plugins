---
name: team-builder
description: This skill should be used when the user asks to "build a team", "suggest a team", "what team should I run", "is my team good", or wants help evaluating an existing team for a specific Pokemon GO Battle League cup and CP cap.
allowed-tools: [Bash(sqlite3 *), Skill(get-rankings)]
argument-hint: "<cup> <cp>"
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `cup` and `cp` from `$ARGUMENTS` (e.g. `jungle 1500`). If either is missing, ask for them before proceeding.

## Instructions

Always invoke the `get-rankings` skill first to ground suggestions in the current meta. Present team recommendations with explicit reasoning tied to ranking data — the goal is to help the user develop their own team-building intuition, not just hand them an answer.

Before offering alternatives for expensive or unavailable picks, ask the user which Pokemon they already have. Then structure every response as:

1. Meta context — what the top threats and cores are in this cup
2. Recommended team with role for each slot (lead / safe switch / closer)
3. Why each pick addresses the meta
4. One or two budget/accessible alternatives based on the user's available Pokemon
