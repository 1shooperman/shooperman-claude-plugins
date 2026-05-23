#!/bin/bash
set -euo pipefail

# Deduplicate across plugins: only one session-time hook fires per Claude session.
# $PPID is the Claude process PID — shared by all plugin hooks in the same session.
LOCK_FILE="/tmp/claude-session-time-${PPID}.lock"

if [ -f "$LOCK_FILE" ]; then
  exit 0
fi

touch "$LOCK_FILE"
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S %Z')
printf '{"systemMessage": "Current system time: %s"}\n' "$CURRENT_TIME"
