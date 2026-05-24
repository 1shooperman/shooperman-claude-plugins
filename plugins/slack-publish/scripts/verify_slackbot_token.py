#!/usr/bin/env python3
"""Exit 0 if SLACK_BOT_TOKEN is available, 1 otherwise."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def find_token() -> str | None:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if token:
        return token

    cwd = Path.cwd()
    for candidate in [cwd / ".env", cwd / ".env.local"]:
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("SLACK_BOT_TOKEN="):
                value = line.split("=", 1)[1].strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                    value = value[1:-1]
                if value:
                    return value
    return None


def main() -> int:
    return 0 if find_token() else 1


if __name__ == "__main__":
    sys.exit(main())
