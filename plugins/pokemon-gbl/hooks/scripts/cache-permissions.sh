#!/bin/bash
# Auto-approves only the specific tool calls needed to build the type chart cache.
# Anything not matched here falls through to normal permission handling.
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

case "$tool_name" in
  WebFetch)
    url=$(echo "$input" | jq -r '.tool_input.url // ""')
    if [[ "$url" == *"pokemondb.net"* ]]; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"pokemon-gbl: WebFetch to pokemondb.net approved for type chart cache"}}'
    fi
    ;;
  Bash)
    cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
    # Allow only mkdir or ls commands that target a .cache path
    if [[ "$cmd" == *"/.cache"* ]] && { [[ "$cmd" =~ ^mkdir[[:space:]] ]] || [[ "$cmd" =~ ^ls[[:space:]] ]] || [[ "$cmd" == ls ]]; }; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"pokemon-gbl: mkdir/ls on .cache directory approved for type chart cache"}}'
    fi
    ;;
  Write)
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')
    if [[ "$file_path" == *"/.cache/"* ]]; then
      echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"pokemon-gbl: Write to .cache directory approved for type chart cache"}}'
    fi
    ;;
esac

exit 0
