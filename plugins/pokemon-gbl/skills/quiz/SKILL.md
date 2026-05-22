---
name: quiz
description: Quiz the user on Pokemon GO type matchups drawn from local type chart data
allowed-tools: [Bash(python3 ./scripts/gen_question.py), Skill(type-chart)]
argument-hint: <required-arg> [optional-arg]
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

## Instructions

When this skill is invoked:

1. Parse the arguments provided by the user
2. Perform the requested action using allowed tools
3. Report results back to the user

## Example usage

Invocation: `/quiz` or `/quiz [n]` to run n questions in a row (default: 1)

## How to run a question

1. Execute the question generator:
```bash
python3 ./scripts/gen_question.py
```

2. The script outputs JSON with fields: `question`, `answer`, `mult`, `explanation`

3. Present ONLY the `question` field to the user. Do NOT reveal the answer or explanation yet.

4. Wait for the user's response.

5. Evaluate their answer against the `answer` field:
   - For multiplier questions: accept reasonable approximations (e.g. "super effective", "1.6", "SE" all count for a 1.6x answer)
   - For list questions: require all correct types; minor ordering/spelling ok
   - Partial credit: if they get the multiplier bucket right (SE/NVE/neutral/immune) but not the exact value, count as correct with a note

6. Give feedback:
   - Correct: confirm + reinforce WHY (use the `explanation` field)
   - Wrong: give the correct answer + explanation, then connect it to a real in-game scenario if possible

## Scoring (multi-question sessions)
Track score across the session. At the end report: X/N correct, flag any category that appeared more than once and was missed.

## Question types (weighted)
- Single type matchup (1x weight)
- Dual type defender matchup (2x weight — most relevant in-game)
- List all SE attackers vs a type (1x weight)
- Double weakness on a dual type (1x weight)

## Data source
SKILL: type-chart — local, no external calls.
