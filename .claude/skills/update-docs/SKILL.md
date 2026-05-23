---
name: update-docs
description: Update the local plugin marketplace docs accordingly.
allowed-tools: [Read, Write, Edit, Bash(git log *), Bash(git -C *), Bash(git diff *), Bash(git add *), Bash(git commit *), Bash(git push *)]
user-invocable: true
---

## Instruction

Keep all documentation in sync after plugin changes. Four targets:

1. **Plugin READMEs** — `plugins/*/README.md`, one per plugin, following `./templates/README_TEMPLATE.md`
2. **Root README** — `README.md` at repo root; does NOT follow the template; reflects the full plugin list and marketplace install instructions
3. **GitHub wiki** — markdown pages in `wiki/shooperman-claude-plugins.wiki/`; committed and pushed to the wiki remote after changes
4. **Root CLAUDE.md** - baseline Claude instructions. Keep up to date with relevant bits from the current session. Prefer efficient token usage over verbosity for CLAUDE.md files.

## Rules

- Only list `user-invocable: true` skills in READMEs — do not expose internal dependency skills
- Do not conflate internal references with user-invocable commands
- The root README is the only doc that should NOT follow the template structure
- Plugin README `Data Sources` section must reflect the actual current cache paths (e.g. `~/.cache/pokemon-gbl/`)

## Arguments

The user invoked this with: $ARGUMENTS

## Instructions

When this skill is invoked:

1. Read `git log --oneline -10` and `git diff HEAD~1..HEAD --name-only` to understand what changed
2. For each changed plugin under `plugins/`:
   - Re-read its skills, agents, and hooks
   - Update `plugins/<name>/README.md` using the template at `./templates/README_TEMPLATE.md`
3. Update root `README.md` if the plugin list or install instructions changed
4. Update the wiki:
   - Edit `wiki/shooperman-claude-plugins.wiki/Home.md` with a current overview of available plugins and skills
   - Create or update additional wiki pages (e.g. `Hook-Permissions.md`, `Cache-Architecture.md`) if the change warrants it
   - Commit and push the wiki changes:
     ```bash
     git -C wiki/shooperman-claude-plugins.wiki add -A
     git -C wiki/shooperman-claude-plugins.wiki commit -m "docs: sync wiki after <brief summary>"
     git -C wiki/shooperman-claude-plugins.wiki push
     ```
5. Report what was updated across all three targets
