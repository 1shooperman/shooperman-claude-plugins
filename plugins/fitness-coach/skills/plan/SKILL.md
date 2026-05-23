---
name: plan
description: Use this skill when the user asks to write a fitness plan
user-invocable: true
---

## Invocation

`/plan`

## Instructions

Prompt me for deep cut information on my fitness goals and available equipment so we can build the right fitness plan for me.

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
