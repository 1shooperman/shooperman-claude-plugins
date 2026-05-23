# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately via [GitHub's private vulnerability reporting](https://github.com/1shooperman/shooperman-claude-plugins/security/advisories/new) rather than opening a public issue.

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or proof-of-concept
- Any suggested mitigations (if known)

You can expect an initial response within **7 days** and a resolution or status update within **30 days**.

## Scope

This repository contains Claude Code plugins. Security concerns most relevant to this project include:

- Hook scripts that auto-approve tool permissions — overly broad approval patterns could allow unintended command execution
- Cache files written to `~/.cache/pokemon-gbl/` — should not contain sensitive data
- WebFetch calls to external domains — currently scoped to `pokemondb.net`

## Supported Versions

Only the latest published version of each plugin is actively maintained.
