#!/bin/bash
set -euo pipefail

# setup 0: activate claudenv from .claudenvrc if present
# CLAUDENVRC=".claudenvrc"
# if [[ -f "$CLAUDENVRC" ]]; then
#     CLAUDENV_NAME="$(cat "$CLAUDENVRC" | tr -d '[:space:]')"
#     if [[ -n "$CLAUDENV_NAME" ]]; then
#         claudenv "$CLAUDENV_NAME"
#     fi
# fi

MARKETPLACE_NAME="shooperman-claude-plugins"

# setup 2: get plugin names
PLUGINS=()
while IFS= read -r line; do
  [[ -n "$line" ]] && PLUGINS+=("$line")
done < <(claude plugin list | grep "$MARKETPLACE_NAME" | sed 's/^[^a-zA-Z]*//' | sed "s/@$MARKETPLACE_NAME//" || true)

echo "Updating $MARKETPLACE_NAME"
claude plugin marketplace update "$MARKETPLACE_NAME"

for plugin in "${PLUGINS[@]+"${PLUGINS[@]}"}"; do
    echo "Updating $plugin"
    claude plugin update "$plugin@$MARKETPLACE_NAME"
done

echo "Run /reload-plugins to pick up any updates"
exit 0
