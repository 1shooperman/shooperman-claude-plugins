# slack-publish

Publish local Markdown files to Slack as formatted messages using Slack `mrkdwn` — not file uploads, not raw Markdown. Includes a `compose` skill for drafting messages before sending.

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `compose` | `/slack-publish:compose <filename> [channel]` | Draft a Markdown file in `~/.cache/slack-publish/` and optionally publish it immediately |
| `publish` | `/slack-publish:publish <markdown-file> <channel>` | Convert a `.md` file to Slack mrkdwn and post it to a channel |

## Usage

```
/slack-publish:compose release-notes #announcements
/slack-publish:compose draft
/slack-publish:publish path/to/file.md my-channel
/slack-publish:publish release-notes.md #announcements
```

Channel may be a name (`my-channel`, `#my-channel`) or a Slack channel ID (`C123...`).

## Data Sources

- **Slack API** — `chat.postMessage`, `conversations.list` via `https://slack.com/api`
- **XDG cache** — drafts saved to `~/.cache/slack-publish/` (respects `$XDG_CACHE_HOME`)

## Prerequisites

- Python 3.9+
- `SLACK_BOT_TOKEN` — set in environment, `.env` / `.env.local` in the working directory, or via `--env-file <path>`
- A Slack bot with scopes: `chat:write`, `channels:read`, `groups:read`
- Bot invited to the destination channel

### Create a Slack App

Use the included `slack-app-manifest.yaml`:

1. Open [https://api.slack.com/apps](https://api.slack.com/apps)
2. **Create New App** → **From a manifest** → select workspace → paste `slack-app-manifest.yaml`
3. **Install to Workspace** → copy the Bot User OAuth Token (`xoxb-...`)
4. Invite the bot to your target channel: `/invite @Markdown Publisher`

## Install

```bash
claude plugin install slack-publish
```
