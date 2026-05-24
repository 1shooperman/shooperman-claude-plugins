#!/bin/bash
# Lint and test the pokemon-gbl Python scripts.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/../../plugins/pokemon-gbl" && pwd)"
SCRIPTS_DIR="$PLUGIN_DIR/skills/ingest-mons/scripts"

if ! command -v ruff &>/dev/null; then
  echo "SKIP: ruff not installed (pip install ruff)" >&2
  exit 0
fi

if ! command -v pytest &>/dev/null; then
  echo "SKIP: pytest not installed (pip install pytest)" >&2
  exit 0
fi

echo "  lint: ruff check"
ruff check "$SCRIPTS_DIR/ingest.py" "$SCRIPTS_DIR/fetch_move_data.py" "$SCRIPTS_DIR/enrich.py"

echo "  test: pytest"
pytest "$PLUGIN_DIR/tests" -q --tb=short
