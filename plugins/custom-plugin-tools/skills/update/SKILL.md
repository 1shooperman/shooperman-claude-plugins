---
name: update
description: Use this skill when the user asks to update a PR description, refresh PR body, or sync PR details based on branch changes. Triggered by phrases like "update PR#N desc", "refresh the PR description", or "update PR based on branch changes".
user-invocable: true
argument-hint: "<PR number>"
allowed-tools: [Bash]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse the PR number from `$ARGUMENTS`. If no number is given, use the PR associated with the current branch:
```bash
gh pr view --json number -q .number
```
If no PR exists, tell the user and stop.

## Instructions

1. Fetch the current PR metadata:
   ```bash
   gh pr view <N> --json title,number,url
   ```

2. Spin up all four agents **in parallel**:
   - `agent-change-summarizer` — produces `## Summary` and `## Components`
   - `agent-security-auditor` — produces `## Security`
   - `agent-test-planner` — produces `## Test plan`
   - `agent-sdet` — writes any missing `tests/**/test-*.sh` files; returns a brief summary (not a PR body section)

3. Assemble the final PR body in this order:
   ```
   ## Summary
   <from agent-change-summarizer>

   ## Components
   <from agent-change-summarizer, omit if empty>

   ## Security
   <from agent-security-auditor>

   ## Test plan
   <from agent-test-planner>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

4. Update the PR:
   ```bash
   gh pr edit <N> --body "..."
   ```

5. Output the PR URL.
