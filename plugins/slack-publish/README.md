# slack-publish

Publish local Markdown files to Slack as formatted messages using Slack `mrkdwn` — not file uploads, not raw Markdown.

## Skills

| Skill | Trigger |
|-------|---------|
| `/slack-publish:publish <file> <channel>` | Publish a `.md` file to a Slack channel |

## Setup

### 1. Create a Slack App

Use the included `slack-app-manifest.yaml`:

1. Open [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From a manifest**
3. Select your workspace and paste the contents of `slack-app-manifest.yaml`
4. Click **Install to Workspace** and copy the Bot User OAuth Token (`xoxb-...`)

Required bot scopes (already in the manifest):
- `chat:write`
- `channels:read`
- `groups:read`

### 2. Configure the Token

Set `SLACK_BOT_TOKEN` in your environment:

```bash
export SLACK_BOT_TOKEN='xoxb-...'
```

Or add it to `.env` / `.env.local` in your working directory:

```bash
echo "SLACK_BOT_TOKEN=xoxb-..." >> .env
```

### 3. Invite the Bot

Invite the bot to every channel you want to publish to:

```
/invite @Markdown Publisher
```

## Usage

```
/slack-publish:publish path/to/file.md my-channel
/slack-publish:publish release-notes.md #announcements
```

Channel may be a name (`my-channel`, `#my-channel`) or a Slack channel ID (`C123...`).

### Dry run (preview without posting)

Claude will run the script with `--dry-run` if you ask to preview before sending.

## Markdown Conversion

| Markdown | Slack mrkdwn |
|----------|-------------|
| `# Heading` | `*Heading*` |
| `**bold**` | `*bold*` |
| `*italic*` | `_italic_` |
| `` `code` `` | `` `code` `` |
| `~~strike~~` | `~strike~` |
| ` ```block``` ` | ` ```block``` ` |
| `[text](url)` | `<url\|text>` |
| `- item` | `• item` |
| `> quote` | `> quote` |
