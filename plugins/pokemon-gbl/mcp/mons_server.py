#!/usr/bin/env python3
"""MCP stdio server for querying mons.db."""

import json
import os
import sqlite3
import sys
from pathlib import Path

DB_PATH = os.environ.get(
    "MONS_DB_PATH",
    str(Path.home() / ".cache/pokemon-gbl/mons.db"),
)

TOOLS = [
    {
        "name": "list_mons",
        "description": "List pokemon from the personal collection with optional filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "shadow": {"type": "boolean", "description": "Filter by shadow status"},
                "purified": {"type": "boolean", "description": "Filter by purified status"},
                "max_rank": {"type": "integer", "description": "Only include mons at or below this GL rank"},
                "min_cp": {"type": "integer", "description": "Minimum CP"},
                "max_cp": {"type": "integer", "description": "Maximum CP"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset"},
            },
        },
    },
    {
        "name": "search_mons",
        "description": "Search for pokemon by name (partial match on species or raw_name).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Species or name to search for"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_mon",
        "description": "Get a specific pokemon by its database ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Database row ID"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "collection_summary",
        "description": "Return aggregate stats about the personal collection (total count, shadow count, top-ranked mons, etc.).",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def row_to_dict(row: sqlite3.Row) -> dict:
    d = {k: row[k] for k in row.keys()}
    raw = d.get("types")
    if raw:
        try:
            d["types"] = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            d["types"] = []
    else:
        d["types"] = []
    return d


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def handle_list_mons(args: dict) -> list:
    clauses, params = [], []

    if "shadow" in args:
        clauses.append("shadow = ?")
        params.append(1 if args["shadow"] else 0)
    if "purified" in args:
        clauses.append("purified = ?")
        params.append(1 if args["purified"] else 0)
    if "max_rank" in args:
        clauses.append("(gl_rank IS NOT NULL AND gl_rank <= ?)")
        params.append(args["max_rank"])
    if "min_cp" in args:
        clauses.append("(cp IS NOT NULL AND cp >= ?)")
        params.append(args["min_cp"])
    if "max_cp" in args:
        clauses.append("(cp IS NOT NULL AND cp <= ?)")
        params.append(args["max_cp"])

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    limit = int(args.get("limit", 50))
    offset = int(args.get("offset", 0))

    with db() as conn:
        rows = conn.execute(
            f"SELECT * FROM mons {where} ORDER BY gl_rank ASC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
    return [row_to_dict(r) for r in rows]


def handle_search_mons(args: dict) -> list:
    name = args["name"]
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM mons WHERE species LIKE ? OR raw_name LIKE ? ORDER BY gl_rank ASC",
            (f"%{name}%", f"%{name}%"),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


def handle_get_mon(args: dict) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM mons WHERE id = ?", (args["id"],)).fetchone()
    return row_to_dict(row) if row else None


def handle_collection_summary(_args: dict) -> dict:
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM mons").fetchone()[0]
        shadows = conn.execute("SELECT COUNT(*) FROM mons WHERE shadow=1").fetchone()[0]
        purified = conn.execute("SELECT COUNT(*) FROM mons WHERE purified=1").fetchone()[0]
        top10 = conn.execute(
            "SELECT raw_name, gl_rank, cp FROM mons WHERE gl_rank IS NOT NULL ORDER BY gl_rank ASC LIMIT 10"
        ).fetchall()
        no_rank = conn.execute("SELECT COUNT(*) FROM mons WHERE gl_rank IS NULL").fetchone()[0]
    return {
        "total": total,
        "shadow": shadows,
        "purified": purified,
        "no_rank": no_rank,
        "top_10_by_rank": [row_to_dict(r) for r in top10],
    }


HANDLERS = {
    "list_mons": handle_list_mons,
    "search_mons": handle_search_mons,
    "get_mon": handle_get_mon,
    "collection_summary": handle_collection_summary,
}


def send(msg: dict):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_request(req: dict) -> dict | None:
    rid = req.get("id")
    method = req.get("method", "")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mons-db", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = req.get("params", {}).get("name")
        args = req.get("params", {}).get("arguments", {})
        handler = HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
        try:
            result = handler(args)
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "error": {"code": -32603, "message": str(e)},
            }

    if method == "notifications/initialized":
        return None

    # Unknown method
    if rid is not None:
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle_request(req)
        if resp is not None:
            send(resp)


if __name__ == "__main__":
    main()
