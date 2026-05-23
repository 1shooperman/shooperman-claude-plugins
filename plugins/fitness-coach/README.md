# fitness-coach

A Claude Code plugin that builds personalized fitness plans using a panel of real-world health and fitness experts. Each coach reasons from their own domain perspective, debates the others, and the synthesis produces a single consolidated weekly plan.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `onboard-user` | `/onboard-user` | Run athlete intake and save profile to `~/.cache/fitness-coach/USER_CONTEXT.md` |
| `onboard-staff` | `/onboard-staff <name1> <name2> ...` | Build a coaching panel from named real-world experts |
| `plan` | `/plan <goal or description>` | Run the multi-coach debate and produce a consolidated training plan |

## Usage

```
/onboard-user
/onboard-staff Peter Attia Andy Galpin Rhonda Patrick
/plan I want to train for a sprint triathlon in 6 months
```

## Workflow

1. **[Once]** `/onboard-user` — collects athlete profile, injuries, measurements, and goals
2. **[Once]** `/onboard-staff <names>` — researches each expert and writes their persona to `~/.cache/fitness-coach/staff/`
3. `/plan <goal>` — runs two debate rounds in parallel, then synthesizes a weekly plan

## Output

Each `/plan` run saves to `~/.cache/fitness-coach/sessions/YYYY-MM-DD/`:

- `plan.md` — consolidated weekly schedule with coach influence summary
- `debate.md` — Round 1 positions, Round 2 rebuttals, and conflict resolutions
- `plan.html` — styled, readable plan with expandable coach commentary

## Install

```bash
claude plugin install fitness-coach
```
