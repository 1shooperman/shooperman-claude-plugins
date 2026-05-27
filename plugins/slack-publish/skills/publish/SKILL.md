---
name: publish
description: Publish a local Markdown file to a Slack channel as a formatted message (not a file upload). Use when the user asks to send or publish a .md file to Slack, e.g. "publish foo.md to #general", "send this markdown to my-channel", or runs /slack-publish:publish.
user-invocable: true
argument-hint: "<markdown-file> <channel>"
allowed-tools: [Bash(python3 *)]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `<markdown-file>` and `<channel>` from `$ARGUMENTS`. Both are required — if either is missing, ask the user before proceeding.

- `<channel>` may be a channel name (`my-channel`, `#my-channel`) or a Slack channel ID (`C123...`, `G123...`).

## Workflow

1. **Check for `SLACK_BOT_TOKEN`** before anything else — use the `slack-publish:agent-token-checker` agent. If it reports "Token missing", **stop here** and show the user this guidance:
   If this exits non-zero, **stop here** and show the user this guidance:

   > **`SLACK_BOT_TOKEN` is not set.** To publish to Slack you need a bot token. Here's how to get one:
   >
   > 1. Go to **https://api.slack.com/apps** and click **Create New App → From a manifest**
   > 2. Select your workspace and paste the contents of `slack-app-manifest.yaml` (in the plugin directory)
   > 3. Click **Install to Workspace** and copy the **Bot User OAuth Token** (starts with `xoxb-`)
   > 4. Invite the bot to your target channel: `/invite @Markdown Publisher`
   > 5. Set the token in one of these ways:
   >    - **Shell environment**: `export SLACK_BOT_TOKEN='xoxb-...'`
   >    - **`.env` file** in your working directory: `SLACK_BOT_TOKEN=xoxb-...`
   >    - **Pass at runtime**: re-run with `--env-file /path/to/file.env`
   >
   > Once the token is set, try again.

2. Verify the markdown file exists at the given path.

3. Run the publisher script, quoting each argument as a discrete shell word to prevent shell injection:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>"
   ```

4. To use a different token file:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>" --env-file "<path>"
   ```

5. To preview the converted Slack text without posting:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/publish/scripts/publish_markdown_to_slack.py" \
     -- "<markdown-file>" "<channel>" --dry-run
   ```

6. Report success including the resolved channel ID and message timestamp (`ts`).

7. If posting fails, report the exact Slack API error. Common causes:
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
