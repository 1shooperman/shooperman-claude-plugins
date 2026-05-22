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

echo "  cache-permissions.sh"

# WebFetch — approved domains
assert_allows \
  "WebFetch to pokemondb.net" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://pokemondb.net/go/type"}}'

assert_allows \
  "WebFetch to pokemondb.net subdomain" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://img.pokemondb.net/sprites/home.png"}}'

# WebFetch — blocked domains
assert_passthrough \
  "WebFetch to unrelated domain" \
  '{"tool_name":"WebFetch","tool_input":{"url":"https://example.com"}}'

assert_passthrough \
  "WebFetch with empty URL" \
  '{"tool_name":"WebFetch","tool_input":{"url":""}}'

# Bash — approved cache operations
assert_allows \
  "Bash mkdir -p .cache" \
  '{"tool_name":"Bash","tool_input":{"command":"mkdir -p /some/path/.cache"}}'

assert_allows \
  "Bash ls .cache file" \
  '{"tool_name":"Bash","tool_input":{"command":"ls /some/path/.cache/type_chart.json"}}'

assert_allows \
  "Bash ls .cache directory" \
  '{"tool_name":"Bash","tool_input":{"command":"ls /some/path/.cache/"}}'

# Bash — blocked operations
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

# Write — approved cache paths
assert_allows \
  "Write to .cache/ directory" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/.cache/type_chart.json","content":"{}"}}'

# Write — blocked paths
assert_passthrough \
  "Write to non-cache path" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/settings.json","content":"{}"}}'

assert_passthrough \
  "Write to path with .cache in filename (not directory)" \
  '{"tool_name":"Write","tool_input":{"file_path":"/some/path/not-a-cache-dir","content":"{}"}}'

# Other tools — always pass through
assert_passthrough \
  "Read tool passes through" \
  '{"tool_name":"Read","tool_input":{"file_path":"/some/file"}}'

assert_passthrough \
  "Edit tool passes through" \
  '{"tool_name":"Edit","tool_input":{"file_path":"/some/file","old_string":"a","new_string":"b"}}'

echo ""
echo "    $pass passed, $fail failed"

[ "$fail" -eq 0 ] || exit 1
