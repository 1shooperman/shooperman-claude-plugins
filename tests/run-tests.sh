#!/bin/bash
# Test harness: discovers and runs all test-*.sh files under tests/
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TESTS_DIR="$REPO_ROOT/tests"

pass=0
fail=0
errors=()

run_test_file() {
  local file="$1"
  local rel="${file#"$REPO_ROOT/"}"
  echo "  $rel"
  if bash "$file"; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    errors+=("$rel")
  fi
}

echo "=== pokemon-gbl hook tests ==="
while IFS= read -r -d '' f; do
  run_test_file "$f"
done < <(find "$TESTS_DIR" -name "test-*.sh" -print0 | sort -z)

echo ""
echo "Results: $pass passed, $fail failed"

if [ ${#errors[@]} -gt 0 ]; then
  echo ""
  echo "Failed:"
  for e in "${errors[@]}"; do
    echo "  - $e"
  done
  exit 1
fi
