#!/bin/bash
# Auto-approves only the specific tool calls needed to build and use the type chart cache.
# Anything not matched here falls through to normal permission handling.
#
# Handles both PreToolUse and PermissionRequest events (same logic, output varies by event).
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
hook_event=$(echo "$input" | jq -r '.hook_event_name // "PreToolUse"')

allow() {
  local reason="$1"
  if [ "$hook_event" = "PermissionRequest" ]; then
    # PermissionRequest uses the top-level decision field, not hookSpecificOutput
    printf '{"decision":"allow","reason":"%s"}\n' "$reason"
  else
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"%s"}}\n' "$reason"
  fi
}

case "$tool_name" in
  WebFetch)
    url=$(echo "$input" | jq -r '.tool_input.url // ""')
    if [[ "$url" == *"pokemondb.net"* ]]; then
      allow "pokemon-gbl: WebFetch to pokemondb.net approved for type chart cache"
    fi
    ;;
  Bash)
    cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
    # python3 running a pokemon-gbl plugin script (with or without leading env var prefix)
    if [[ "$cmd" == *"python3"* ]] && [[ "$cmd" == *"/pokemon-gbl/"* ]]; then
      allow "pokemon-gbl: python3 plugin script approved"
    fi
    ;;
  Read)
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
    if [[ "$file_path" == *"/pokemon-gbl/"* ]]; then
      allow "pokemon-gbl: Read from plugin directory approved"
    fi
    ;;
esac

exit 0
