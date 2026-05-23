## Git

Never commit directly to `main`. Always create a feature branch (e.g. `feat/description` or `fix/description`) and open a PR.

## Commands

- `make test` — run plugin tests
- `make validate` — validate marketplace.json via claude CLI

## CI

- Validate step only runs when plugin paths change (`.claude-plugin/`, `plugins/*/` skills/agents/hooks/commands)
- Validate step uses `warn-invariants: I1 I5 I8`

## Docs

After plugin changes, run `/update-docs` to sync READMEs and wiki.
