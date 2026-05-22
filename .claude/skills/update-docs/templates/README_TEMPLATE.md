# {plugin-name}

{One sentence describing what the plugin does and who it is for.}

## Skills

List only user-invocable skills here. Do not include internal dependency skills (`user-invocable: false`).

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `skill-name` | `/skill-name <required> [optional]` | What this skill does in one line |

## Usage

```
/skill-name arg1 arg2
/skill-name arg1
```

## Data Sources

List any external services, local data files, or APIs the plugin reads from. Omit this section if the plugin has no data dependencies.

- **source-name** — what it provides and how it is used
- Local file at `skills/{skill-name}/.cache/{file}.json`

## Prerequisites

List any tools, credentials, or setup steps required before the plugin works. Omit this section if there are none.

- Python 3.x (for scripts in `skills/*/scripts/`)
- `SOME_API_KEY` environment variable

## Install

```bash
claude plugin install {plugin-name}
```
