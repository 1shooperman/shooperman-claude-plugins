# custom-plugin-tools

A Claude Code plugin that writes PR descriptions using three parallel agents: one summarizes the changes, one audits for security issues, and one generates a concrete test plan and fills gaps in the test suite.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `update` | `/custom-plugin-tools:update [PR number]` | Build or refresh a PR description for the current branch or a specified PR number |

## Usage

```
/custom-plugin-tools:update
/custom-plugin-tools:update 42
```

If no PR number is given, the skill resolves the PR for the current branch automatically.

## How it works

Three agents run in parallel and each produce one section of the PR body:

| Agent | Output | What it does |
|-------|--------|--------------|
| `agent-change-summarizer` | `## Summary`, `## Components` | Reads git diff and changed files to describe what changed and why |
| `agent-security-auditor` | `## Security` | Checks changed files against a plugin-specific security checklist; always reports |
| `agent-test-planner` | `## Test plan` | Reads changed skills/agents/hooks and produces a specific, invocation-level test checklist |
| `agent-sdet` | _(no PR section)_ | Finds gaps in `tests/hooks/` for changed hook scripts and writes missing `test-*.sh` files |

## Install

```bash
claude plugin install custom-plugin-tools
```
