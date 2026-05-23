#!/bin/bash
set -euo pipefail

CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S %Z')
printf '{"systemMessage": "Current system time: %s"}\n' "$CURRENT_TIME"
