---
name: type-chart
description: Pokemon GO type effectiveness lookup for single or dual types
allowed-tools: [Bash(python3 ./scripts/query_types.py)]
argument-hint: <required-arg> [optional-arg]
user-invocable: true
---

# Example Command (skill format):
- `/type-chart dark steel`
- `/type-chart fire`
- `/type-chart water ground`

## Arguments

The user invoked this with: $ARGUMENTS

## Instructions
1. Parse the arguments provided by the user
2. Local lookup against GO-specific type chart (1.6x / 0.625x / 0.39x multipliers).
3. Returns defender matchups (combined for dual types) and attacker matchups for each type.
4. No WebFetch calls needed.

When this skill is invoked:

1. Parse the arguments provided by the user
2. Perform the requested action using allowed tools
3. Report results back to the user

## Execution
```bash
python3 ./scripts/query_types.py [type1] [type2]
```

## Data
`./.cache/type_chart.json` — versioned, user-triggered refresh when GO patches drop.
