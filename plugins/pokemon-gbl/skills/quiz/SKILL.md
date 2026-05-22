---
name: quiz
description: Quizzes the user on Pokemon GO type matchups drawn from local type chart data. Activated when the user says "quiz me", "test my type knowledge", or "/quiz".
allowed-tools: [Bash(python3 *gen_question.py), Skill(type-chart)]
argument-hint: "[n]"
user-invocable: true
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `n` from `$ARGUMENTS` as the number of questions to run (default: 1).

## How to run a question

1. Execute the question generator:
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/quiz/scripts/gen_question.py
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
