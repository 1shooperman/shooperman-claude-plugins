---
name: compose
description: Draft a new Markdown file for Slack publishing and save it to the XDG cache directory (~/.cache/slack-publish/). Use when the user wants to write or compose a message to send to Slack, e.g. "compose a Slack message", "draft a release announcement for Slack", "write a new post for #general", or runs /slack-publish:compose.
user-invocable: true
argument-hint: "<filename> [channel]"
allowed-tools: [Bash, Write, Read]
---

## Arguments

The user invoked this with: $ARGUMENTS

Parse `<filename>` and optionally `<channel>` from `$ARGUMENTS`.

- `<filename>` — name for the draft file, with or without `.md` extension. If omitted, generate one from the current date: `draft-YYYY-MM-DD.md`.
- `<channel>` — optional target channel to remember for the publish step.

## Cache Directory

Resolve the XDG-compliant cache directory:

```bash
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/slack-publish"
mkdir -p "$CACHE_DIR"
```

The draft file path is `$CACHE_DIR/<filename>.md`.

## Workflow

1. Resolve the cache directory and ensure it exists (run the bash snippet above).

2. If a draft file already exists at that path, read it and show the user the current content before proceeding.

3. Ask the user what content they want in the message, or ask them to describe the topic if they haven't already. Help them write clear, well-structured Markdown that will render nicely in Slack.

4. Write the final Markdown content to the draft file.

5. Confirm the file was saved and show the full path.

6. If a `<channel>` was provided (or the user mentions one), offer to publish immediately:
   > "Draft saved to `$CACHE_DIR/<filename>.md`. Publish to `<channel>` now?"
   
   If the user confirms, invoke the `slack-publish:publish` skill with the resolved file path and channel.

## Markdown Tips

Remind the user of conversions that apply when publishing:
- `# Heading` → bold header line in Slack
- `**bold**` / `__bold__` → `*bold*` (Slack bold)
- `*italic*` → `_italic_` (Slack italic)
- ` ```code block``` ` → preserved as-is
- `- item` / `1. item` → `• item`
- `[label](url)` → `<url|label>`
- `~~strike~~` → `~strike~`

## Listing Drafts

If the user asks to list drafts, run:

```bash
ls -1t "${XDG_CACHE_HOME:-$HOME/.cache}/slack-publish/"
```
