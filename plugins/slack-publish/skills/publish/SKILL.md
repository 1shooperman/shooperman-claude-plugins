---
name: publish
description: Publish a local Markdown file to a Slack channel as a formatted message (not a file upload). Use when the user asks to send or publish a .md file to Slack, e.g. "publish foo.md to #general", "send this markdown to my-channel", or runs /slack-publish:publish.
user-invocable: true
argument-hint: "<markdown-file> <channel>"
allowed-tools: [Bash]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `<markdown-file>` and `<channel>` from `$ARGUMENTS`. Both are required — if either is missing, ask the user before proceeding.

- `<channel>` may be a channel name (`my-channel`, `#my-channel`) or a Slack channel ID (`C123...`, `G123...`).

## Workflow

1. Verify the markdown file exists at the given path.

2. Run the publisher script, quoting each argument as a discrete shell word to prevent shell injection:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>"
   ```

3. If `SLACK_BOT_TOKEN` is not set in the environment, the script will also check `.env` and `.env.local` in the current directory automatically. To use a different token file:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>" --env-file "<path>"
   ```

4. To preview the converted Slack text without posting:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>" --dry-run
   ```

5. Report success including the resolved channel ID and message timestamp (`ts`).

6. If posting fails, report the exact Slack API error. Common causes:
   - Missing token scopes (`chat:write`, `channels:read`, `groups:read`)
   - Bot not invited to the destination channel

## Environment

`SLACK_BOT_TOKEN` must be available. Set it via:
- Shell environment: `export SLACK_BOT_TOKEN='xoxb-...'`
- `.env` or `.env.local` in the working directory
- `--env-file <path>` flag

Required bot token scopes:
- `chat:write`
- `channels:read` (public channel name lookup)
- `groups:read` (private channel name lookup)
