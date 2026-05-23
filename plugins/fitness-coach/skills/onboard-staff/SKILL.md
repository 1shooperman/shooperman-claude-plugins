---
name: onboard-staff
description: Use this skill to create the coaching staff
user-invocable: false
argument-hint: "[n]"
allowed-tools: [WebFetch]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse number from `$ARGUMENTS` (e.g. `5`). If either is missing, ask for them before proceeding.

## Instructions

- Given [NUMBER] advisors aka real people who are subject matter experts in health and fitness.
- Use $CLAUDE_PLUGIN_ROOT/EXAMPLE.md for the coach persona format.

For each advisor, include:
- Their name
- A 2-3 sentence personality profile describing how they think, what they prioritize, and what biases they bring (you will find this online)

