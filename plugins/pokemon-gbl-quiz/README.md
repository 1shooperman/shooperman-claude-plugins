# pokemon-gbl-quiz

A Claude Code plugin that quizzes you on Pokemon GO type matchups using GO-specific damage multipliers (1.6x / 0.625x / 0.39x).

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `quiz` | `/quiz [n]` | Run a type matchup quiz session with `n` questions (default: 1) |
| `type-chart` | `/type-chart <type1> [type2]` | Look up type effectiveness for a single or dual-type defender |

## Usage

```
/quiz          # single question
/quiz 5        # 5-question session with scoring
/type-chart fire
/type-chart water ground
```

## Question Types

- Single type matchup
- Dual-type defender matchup (most common in-game)
- List all super-effective attackers vs a type
- Double-weakness identification on dual types

## Install

```bash
claude plugin install pokemon-gbl-quiz
```
