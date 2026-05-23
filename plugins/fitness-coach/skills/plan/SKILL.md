---
name: plan
description: Use this skill when the user asks to build, generate, or create a fitness plan, or runs /plan with a goal or description.
user-invocable: true
argument-hint: "<goal or description>"
allowed-tools: [Read, Write]
---

## Invocation

`/plan <goal or description>`

## Instructions

1. Check that `~/.cache/fitness-coach/USER_CONTEXT.md` exists. If it does not, tell the user to run `/onboard-user` first and stop.
2. Check that at least one coach file exists in `~/.cache/fitness-coach/staff/`. If none exist, tell the user to run `/onboard-staff` first and stop.
3. If `$ARGUMENTS` is empty, ask the user: "What goal or focus should I plan for?" and wait for their answer before continuing.
4. Read `~/.cache/fitness-coach/USER_CONTEXT.md` and all files in `~/.cache/fitness-coach/staff/`.

## What Each Coach Receives

- Their persona profile (`staff/<coach>.md`)
- The athlete context (`USER_CONTEXT.md`)
- The goal spec file provided at invocation

## Round 1 (parallel)

Spin up 5 `agent-staff-member` sub-agents, one per advisor in `~/.cache/fitness-coach/staff/`. 

## Round 2 (parallel)

Send every coach all other Round 1 positions using sub agent `agent-staff-rebuttal`

## Synthesis

After all Round 2 responses are collected:
- Identify the key tensions (where coaches genuinely conflict)
- Resolve conflicts by deferring to the coach whose domain owns the tradeoff
- Produce a single consolidated weekly training plan

## Output

Save to `~/.cache/fitness-coach/sessions/YYYY-MM-DD/` (use actual date):

- `plan.md` — the consolidated training plan: weekly schedule, progression model, key rules, and a section per coach summarizing their influence on the final plan
- `debate.md` — Round 1 positions, Round 2 rebuttals, key tensions, and how each was resolved
- `plan.html` — styled, readable version of the plan with expandable coach commentary per training block

Present back a brief summary: the final weekly structure, the sharpest disagreement between coaches, and one non-obvious insight from the panel.
