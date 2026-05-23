## Commands

- `make test` — run plugin tests
- `make validate` — validate marketplace.json via claude CLI

## CI

- Validate step only runs when plugin paths change (`.claude-plugin/`, `plugins/*/` skills/agents/hooks/commands)
- Validate step uses `warn-invariants: I1 I3 I5 I8`

## Docs

After plugin changes, run `/update-docs` to sync READMEs and wiki.
