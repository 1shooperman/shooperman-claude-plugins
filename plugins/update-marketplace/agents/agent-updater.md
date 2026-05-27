---
name: agent-updater
description: Updates each plugin
allowed-tools: [Bash(claude plugin *), Bash(bash *), Bash(echo)]
model: haiku
color: cyan
---

## Instructions

1. Get the `update-marketplace` plugin `installPath` via `claude plugin list --json`
2. Run `bash <installPath>/scripts/update-marketplace.sh`

## Outputs

None