#!/bin/bash
# Tests for plugins/pokemon-gbl/hooks/scripts/session-time.sh
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/../.." && pwd)/plugins/pokemon-gbl/hooks/scripts/session-time.sh"

pass=0
fail=0

assert() {
  local desc="$1"
  local result="$2"
  if [ "$result" = "ok" ]; then
    echo "    PASS: $desc"
    pass=$((pass + 1))
  else
    echo "    FAIL: $desc ($result)"
    fail=$((fail + 1))
  fi
}

echo "  session-time.sh"

# Clean up any stale lock for this test run
LOCK_FILE="/tmp/claude-session-time-$$.lock"
rm -f "$LOCK_FILE"

out=$(bash "$SCRIPT")

# Output is valid JSON
if echo "$out" | jq . > /dev/null 2>&1; then
  assert "output is valid JSON" "ok"
else
  assert "output is valid JSON" "not valid JSON: $out"
fi

# systemMessage key present
if echo "$out" | jq -e '.systemMessage' > /dev/null 2>&1; then
  assert "systemMessage key present" "ok"
else
  assert "systemMessage key present" "missing"
fi

# systemMessage contains a plausible timestamp (4-digit year)
msg=$(echo "$out" | jq -r '.systemMessage')
if echo "$msg" | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
  assert "systemMessage contains YYYY-MM-DD timestamp" "ok"
else
  assert "systemMessage contains YYYY-MM-DD timestamp" "not found in: $msg"
fi

# Script exits 0
bash "$SCRIPT" > /dev/null
assert "script exits 0" "ok"

# Deduplication: second call in same session (same PPID lock) produces no output
LOCK_FILE="/tmp/claude-session-time-$$.lock"
touch "$LOCK_FILE"
second_out=$(bash "$SCRIPT")
if [ -z "$second_out" ]; then
  assert "second call in same session produces no output" "ok"
else
  assert "second call in same session produces no output" "got output: $second_out"
fi
rm -f "$LOCK_FILE"

# Deduplication: all three plugin copies are identical (same fix applied everywhere)
SCRIPTS=(
  "$(cd "$(dirname "$0")/../.." && pwd)/plugins/custom-plugin-tools/hooks/scripts/session-time.sh"
  "$(cd "$(dirname "$0")/../.." && pwd)/plugins/fitness-coach/hooks/scripts/session-time.sh"
  "$(cd "$(dirname "$0")/../.." && pwd)/plugins/pokemon-gbl/hooks/scripts/session-time.sh"
)
all_same="ok"
for s in "${SCRIPTS[@]}"; do
  if ! diff -q "$SCRIPT" "$s" > /dev/null 2>&1; then
    all_same="$s differs"
    break
  fi
done
assert "all three plugin session-time.sh scripts are identical" "$all_same"

echo ""
echo "    $pass passed, $fail failed"

[ "$fail" -eq 0 ] || exit 1
