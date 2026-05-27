---
name: agent-token-checker
description: Checks whether SLACK_BOT_TOKEN is available (env var or .env file). Returns exit code 0 if found, 1 if missing. Used by the publish skill before attempting to post to Slack.
allowed-tools: [Bash(python3 *)]
model: haiku
---

## Instruction

Run the token checker script and report the result:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/verify_slackbot_token.py"
```

- Exit code **0** → token is available. Report: "Token found."
- Exit code **1** → token is missing. Report: "Token missing."
