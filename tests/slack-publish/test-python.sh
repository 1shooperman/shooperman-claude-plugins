#!/bin/bash
# Lint and test the slack-publish Python script.
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/../../plugins/slack-publish" && pwd)"

if ! command -v ruff &>/dev/null; then
  echo "SKIP: ruff not installed (pip install ruff)" >&2
  exit 0
fi

if ! command -v pytest &>/dev/null; then
  echo "SKIP: pytest not installed (pip install pytest)" >&2
  exit 0
fi

echo "  lint: ruff check"
ruff check "$PLUGIN_DIR/skills/publish/scripts/publish_markdown_to_slack.py"

echo "  test: pytest"
pytest "$PLUGIN_DIR/tests" -q --tb=short
