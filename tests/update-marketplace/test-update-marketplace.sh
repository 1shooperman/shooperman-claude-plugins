#!/bin/bash
# Tests for plugins/update-marketplace/scripts/update-marketplace.sh
set -euo pipefail

SCRIPT="$(cd "$(dirname "$0")/../.." && pwd)/plugins/update-marketplace/scripts/update-marketplace.sh"

pass=0
fail=0

# Runs the script with a mock claude that captures calls.
# Args: test description, mock plugin list output, expected_calls (newline-separated)
run_test() {
  local desc="$1"
  local list_output="$2"
  local expected_calls="$3"

  local tmpdir
  tmpdir=$(mktemp -d)
  local calls_file="$tmpdir/calls"
  touch "$calls_file"

  # Mock claude binary
  cat > "$tmpdir/claude" <<EOF
#!/bin/bash
echo "\$*" >> "$calls_file"
if [[ "\$*" == "plugin list" ]]; then
  cat <<'LIST'
$list_output
LIST
fi
EOF
  chmod +x "$tmpdir/claude"

  PATH="$tmpdir:$PATH" bash "$SCRIPT" > /dev/null 2>&1
  local actual
  actual=$(cat "$calls_file")

  if [ "$actual" = "$expected_calls" ]; then
    echo "    PASS: $desc"
    pass=$((pass + 1))
  else
    echo "    FAIL: $desc"
    echo "          expected calls:"
    echo "$expected_calls" | sed 's/^/            /'
    echo "          actual calls:"
    echo "$actual" | sed 's/^/            /'
    fail=$((fail + 1))
  fi

  rm -rf "$tmpdir"
}

echo "  update-marketplace.sh"

LIST_TWO_PLUGINS="  ❯ pokemon-gbl@shooperman-claude-plugins
    Version: 1.1.5
  ❯ update-marketplace@shooperman-claude-plugins
    Version: 0.1.1
  ❯ other-plugin@other-marketplace
    Version: 2.0.0"

LIST_ONE_PLUGIN="  ❯ pokemon-gbl@shooperman-claude-plugins
    Version: 1.1.5
  ❯ other-plugin@other-marketplace
    Version: 2.0.0"

LIST_NO_PLUGINS="  ❯ other-plugin@other-marketplace
    Version: 2.0.0"

run_test \
  "updates marketplace then each plugin" \
  "$LIST_TWO_PLUGINS" \
  "plugin list
plugin marketplace update shooperman-claude-plugins
plugin update pokemon-gbl@shooperman-claude-plugins
plugin update update-marketplace@shooperman-claude-plugins"

run_test \
  "updates single plugin" \
  "$LIST_ONE_PLUGIN" \
  "plugin list
plugin marketplace update shooperman-claude-plugins
plugin update pokemon-gbl@shooperman-claude-plugins"

run_test \
  "no plugins — still updates marketplace" \
  "$LIST_NO_PLUGINS" \
  "plugin list
plugin marketplace update shooperman-claude-plugins"

echo ""
echo "    $pass passed, $fail failed"

[ "$fail" -eq 0 ] || exit 1
