#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"

FINDINGS=0
EXIT_CODE=0

flag() {
  local severity="$1"; shift
  echo "[$severity] $*"
  FINDINGS=$((FINDINGS + 1))
  if [[ "$severity" == "ERROR" ]]; then
    EXIT_CODE=1
  fi
}

# Scan all markdown files under plugins/ for allowed-tools declarations
while IFS= read -r file; do
  # Extract allowed-tools line from YAML frontmatter only (between first --- pair)
  tools_line=$(awk '/^---/{f=!f; next} f && /^allowed-tools:/' "$file" | head -1)
  [[ -z "$tools_line" ]] && continue

  rel="${file#"$REPO_ROOT"/}"

  # Bare Bash (no constraint) — allows any shell command
  if echo "$tools_line" | grep -qE '\bBash\b[^(]|Bash\s*\]|Bash\s*,'; then
    flag ERROR "$rel: bare 'Bash' grants unrestricted shell access"
  fi

  # Bare WebFetch (no domain) — allows fetching any URL
  if echo "$tools_line" | grep -qE '\bWebFetch\b[^(]|WebFetch\s*\]|WebFetch\s*,'; then
    flag WARN "$rel: bare 'WebFetch' allows fetching any domain"
  fi

  # Bash(*) — constraint is just a wildcard, matches any command
  if echo "$tools_line" | grep -qE 'Bash\(\s*\*\s*\)'; then
    flag ERROR "$rel: Bash(*) is effectively unrestricted"
  fi

  # Wildcard-only Agent/Skill — e.g. Agent(*) or allowed-tools: [*]
  if echo "$tools_line" | grep -qE '\[\s*\*\s*\]|Agent\(\s*\*\s*\)|Skill\(\s*\*\s*\)'; then
    flag ERROR "$rel: wildcard '*' grants access to all tools/agents"
  fi

done < <(find "$PLUGINS_DIR" -name "*.md" -type f)

echo ""
echo "SAST complete. Findings: $FINDINGS"
exit "$EXIT_CODE"
