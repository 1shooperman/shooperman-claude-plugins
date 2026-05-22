#!/bin/bash
# Tests for plugins/pokemon-gbl/hooks/scripts/cache-permissions.sh
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/../.." && pwd)/plugins/pokemon-gbl/hooks/scripts/cache-permissions.sh"

pass=0
fail=0

assert_allows() {
  local desc="$1"
  local payload="$2"
  local out
  out=$(echo "$payload" | bash "$SCRIPT")
  if echo "$out" | grep -q '"permissionDecision":"allow"'; then
    echo "    PASS: $desc"
    pass=$((pass + 1))
  else
    echo "    FAIL: $desc"
    echo "          expected permissionDecision=allow, got: $out"
    fail=$((fail + 1))
  fi
}

assert_passthrough() {
  local desc="$1"
  local payload="$2"
  local out
  out=$(echo "$payload" | bash "$SCRIPT")
  if [ -z "$out" ]; then
    echo "    PASS: $desc"
    pass=$((pass + 1))
  else
    echo "    FAIL: $desc"
    echo "          expected no output, got: $out"
    fail=$((fail + 1))
  fi
}

# Simulate the hook_event_name field for PermissionRequest
permission_request() {
  local tool="$1"
  local input_fragment="$2"
  echo "{\"hook_event_name\":\"PermissionRequest\",\"tool_name\":\"$tool\",$input_fragment}"
}

echo "  cache-permissions.sh — PreToolUse"

# --- WebFetch ---
assert_allows \
  "WebFetch to pokemondb.net" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://pokemondb.net/go/type"}}'

assert_allows \
  "WebFetch to pokemondb.net subdomain" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://img.pokemondb.net/sprites/home.png"}}'

assert_passthrough \
  "WebFetch to unrelated domain" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com"}}'

assert_passthrough \
  "WebFetch with empty URL" \
  '{"tool_name":"WebFetch","tool_input":{"url":""}}'

# --- Bash: python3 plugin scripts ---
assert_allows \
  "Bash python3 pokemon-gbl query_types.py" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 /Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/skills/type-chart/scripts/query_types.py fire water"}}'

assert_allows \
  "Bash python3 pokemon-gbl gen_question.py" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 /Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/skills/quiz/scripts/gen_question.py"}}'

assert_passthrough \
  "Bash python3 non-plugin script" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 /some/other/script.py"}}'

assert_passthrough \
  "Bash arbitrary python3 without plugin path" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 -c \"print(42)\""}}'

# --- Bash: mkdir/ls on .cache ---
assert_allows \
  "Bash mkdir -p .cache" \
  '{"tool_name":"Bash","tool_input":{"command":"mkdir -p /some/path/.cache"}}'

assert_allows \
  "Bash ls .cache file" \
  '{"tool_name":"Bash","tool_input":{"command":"ls /some/path/.cache/type_chart.json"}}'

assert_allows \
  "Bash ls .cache directory" \
  '{"tool_name":"Bash","tool_input":{"command":"ls /some/path/.cache/"}}'

assert_passthrough \
  "Bash rm on .cache path" \
  '{"tool_name":"Bash","tool_input":{"command":"rm -rf /some/path/.cache/type_chart.json"}}'

assert_passthrough \
  "Bash mkdir without .cache path" \
  '{"tool_name":"Bash","tool_input":{"command":"mkdir -p /some/other/dir"}}'

assert_passthrough \
  "Bash ls without .cache path" \
  '{"tool_name":"Bash","tool_input":{"command":"ls /some/other/dir"}}'

assert_passthrough \
  "Bash arbitrary command" \
  '{"tool_name":"Bash","tool_input":{"command":"curl https://example.com"}}'

# --- Read ---
assert_allows \
  "Read template from pokemon-gbl plugin dir" \
  '{"tool_name":"Read","tool_input":{"file_path":"/Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/skills/type-chart/templates/type_chart_template.json"}}'

assert_allows \
  "Read data file from pokemon-gbl plugin dir" \
  '{"tool_name":"Read","tool_input":{"file_path":"/Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/.cache/type_chart.json"}}'

assert_passthrough \
  "Read from unrelated path" \
  '{"tool_name":"Read","tool_input":{"file_path":"/some/other/file.json"}}'

# --- Write ---
assert_allows \
  "Write to .cache/ directory" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/.cache/type_chart.json","content":"{}"}}'

assert_passthrough \
  "Write to non-cache path" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/settings.json","content":"{}"}}'

assert_passthrough \
  "Write to path with .cache in filename only" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/not-a-cache-dir","content":"{}"}}'

# --- Other tools ---
assert_passthrough \
  "Edit tool passes through" \
  '{"tool_name":"Edit","tool_input":{"file_path":"/some/file","old_string":"a","new_string":"b"}}'

# --- PermissionRequest event (sensitive file dialogs) ---
echo ""
echo "  cache-permissions.sh — PermissionRequest"

assert_allows \
  "PermissionRequest: mkdir .cache (sensitive file guard)" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Bash","tool_input":{"command":"mkdir -p /Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/.cache"}}'

assert_allows \
  "PermissionRequest: Write type_chart.json (sensitive file guard)" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Write","tool_input":{"file_path":"/Users/bshoop/.claude/plugins/cache/shooperman-claude-plugins/pokemon-gbl/1.0.3/.cache/type_chart.json","content":"{}"}}'

assert_passthrough \
  "PermissionRequest: mkdir non-cache path passes through" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Bash","tool_input":{"command":"mkdir -p /some/other/dir"}}'

assert_passthrough \
  "PermissionRequest: Write non-cache path passes through" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Write","tool_input":{"file_path":"/some/path/settings.json","content":"{}"}}'

echo ""
echo "    $pass passed, $fail failed"

[ "$fail" -eq 0 ] || exit 1
