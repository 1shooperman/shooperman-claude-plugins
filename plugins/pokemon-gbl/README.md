# pokemon-gbl

A Claude Code plugin for building and evaluating Pokemon GO Battle League (GBL) teams using live rankings from pvpoke.com and local type chart data.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `team-builder` | `/team-builder <cup> <cp>` | Build or evaluate a GBL team for the given cup and CP cap |
| `type-chart` | `/type-chart <type1> [type2]` | Look up GO type effectiveness for a single or dual type |
| `quiz` | `/quiz [n]` | Quiz yourself on type matchups; optionally run `n` questions in a row |

## Usage

```
/team-builder great 1500
/team-builder jungle 1500
/type-chart dark steel
/type-chart fire
/quiz
/quiz 5
```

## Data Sources

- **pvpoke.com** — rankings JSON (cached locally for 48 hours)
- **pokemongo.com/en/news** — GO Battle League news for move change context
- Local type chart at `skills/type-chart/.cache/type_chart.json`

## Install

```bash
claude plugin install pokemon-gbl
```
