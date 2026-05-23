---
name: onboard-staff
description: Use this skill when the user wants to create their coaching staff by naming real health and fitness experts (e.g. "onboard staff with Peter Attia, Andy Galpin, and Rhonda Patrick" or "/onboard-staff Peter Attia Andy Galpin")
user-invocable: true
argument-hint: "<name1> <name2> ... <nameN>"
allowed-tools: [WebFetch, Write]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse the names from `$ARGUMENTS` as a space- or comma-separated list of real people (e.g. `Peter Attia, Andy Galpin`). If no names are provided, ask the user to list the experts they want on their panel before proceeding.

## Instructions

For each named advisor:
1. Research who they are using WebFetch if needed — confirm they are a real health/fitness subject matter expert.
2. Use `$CLAUDE_PLUGIN_ROOT/EXAMPLE.md` as the persona file format.
3. Write one persona file per coach to `~/.cache/fitness-coach/staff/<firstname-lastname>.md` with:
   - Their name
   - A 2–3 sentence personality profile: how they think, what they prioritize, and what biases they bring

## Output

After all files are written, confirm: "Staff ready: [list of names]. You can now run `/plan`."

