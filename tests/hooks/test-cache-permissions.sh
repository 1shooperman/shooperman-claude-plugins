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

assert_decision_allow() {
  local desc="$1"
  local payload="$2"
  local out
  out=$(echo "$payload" | bash "$SCRIPT")
  if echo "$out" | grep -q '"decision":"allow"'; then
    echo "    PASS: $desc"
    pass=$((pass + 1))
  else
    echo "    FAIL: $desc"
    echo "          expected decision=allow, got: $out"
    fail=$((fail + 1))
  fi
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
  '{"tool_name":"Bash","tool_input":{"command":"python3 /some/path/pokemon-gbl/1.0.3/skills/type-chart/scripts/query_types.py fire water"}}'

assert_allows \
  "Bash python3 pokemon-gbl gen_question.py" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 /some/path/pokemon-gbl/1.0.3/skills/quiz/scripts/gen_question.py"}}'

assert_allows \
  "Bash python3 with CLAUDE_PLUGIN_ROOT env prefix" \
  '{"tool_name":"Bash","tool_input":{"command":"CLAUDE_PLUGIN_ROOT=\"/some/path/pokemon-gbl/1.0.3\" python3 /some/path/pokemon-gbl/1.0.3/skills/type-chart/scripts/query_types.py water ice"}}'

assert_passthrough \
  "Bash python3 non-plugin script" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 /some/other/script.py"}}'

assert_passthrough \
  "Bash arbitrary python3 without plugin path" \
  '{"tool_name":"Bash","tool_input":{"command":"python3 -c \"print(42)\""}}'

assert_allows \
  "Bash mkdir for pokemon-gbl cache" \
  '{"tool_name":"Bash","tool_input":{"command":"mkdir -p ~/.cache/pokemon-gbl"}}'

assert_allows \
  "Bash compound ls+wc verification of cache" \
  '{"tool_name":"Bash","tool_input":{"command":"ls -lah ~/.cache/pokemon-gbl/ && wc -l ~/.cache/pokemon-gbl/type_chart.json"}}'

assert_passthrough \
  "Bash rm on pokemon-gbl cache blocked" \
  '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/.cache/pokemon-gbl/type_chart.json"}}'

assert_passthrough \
  "Bash arbitrary command" \
  '{"tool_name":"Bash","tool_input":{"command":"curl https://example.com"}}'

# --- Read ---
assert_allows \
  "Read template from pokemon-gbl plugin dir" \
  '{"tool_name":"Read","tool_input":{"file_path":"/some/path/pokemon-gbl/1.0.3/skills/type-chart/templates/type_chart_template.json"}}'

assert_allows \
  "Read cache file from ~/.cache/pokemon-gbl" \
  '{"tool_name":"Read","tool_input":{"file_path":"/home/user/.cache/pokemon-gbl/type_chart.json"}}'

assert_passthrough \
  "Read from unrelated path" \
  '{"tool_name":"Read","tool_input":{"file_path":"/some/other/file.json"}}'

# --- Other tools pass through ---
assert_allows \
  "Write to ~/.cache/pokemon-gbl/ approved" \
  '{"tool_name":"Write","tool_input":{"file_path":"/home/user/.cache/pokemon-gbl/type_chart.json","content":"{}"}}'

assert_allows \
  "Write via relative path to .cache/pokemon-gbl/" \
  '{"tool_name":"Write","tool_input":{"file_path":"../../.cache/pokemon-gbl/type_chart.json","content":"{}"}}'

assert_passthrough \
  "Write to unrelated path blocked" \
  '{"tool_name":"Write","tool_input":{"file_path":"/home/user/.cache/other/file.json","content":"{}"}}'

assert_passthrough \
  "Edit tool passes through" \
  '{"tool_name":"Edit","tool_input":{"file_path":"/some/file","old_string":"a","new_string":"b"}}'

# --- PermissionRequest event ---
echo ""
echo "  cache-permissions.sh — PermissionRequest"

assert_decision_allow \
  "PermissionRequest: python3 pokemon-gbl script" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Bash","tool_input":{"command":"python3 /some/path/pokemon-gbl/1.0.3/skills/type-chart/scripts/query_types.py fire water"}}'

assert_passthrough \
  "PermissionRequest: unrelated Bash passes through" \
  '{"hook_event_name":"PermissionRequest","tool_name":"Bash","tool_input":{"command":"mkdir -p /some/other/dir"}}'

echo ""
echo "    $pass passed, $fail failed"

[ "$fail" -eq 0 ] || exit 1
