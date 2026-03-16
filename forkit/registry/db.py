"""
forkit.registry.db
──────────────────
SQLite index layer for the local registry.

The source of truth is always the JSON files on disk.
SQLite provides fast querying without a server process.
The DB is always rebuildable from the JSON store via LocalRegistry.rebuild_index().

Schema
──────
  passports (
    id            TEXT PRIMARY KEY,
    passport_type TEXT NOT NULL,
    name          TEXT NOT NULL,
    version       TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'draft',
    creator_name  TEXT,
    creator_org   TEXT,
    tags          TEXT,          -- JSON array
    created_at    TEXT,
    updated_at    TEXT,
    json_path     TEXT NOT NULL  -- relative path to the JSON file
  )
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


_DDL = """
CREATE TABLE IF NOT EXISTS passports (
    id            TEXT PRIMARY KEY,
    passport_type TEXT NOT NULL,
    name          TEXT NOT NULL,
    version       TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'draft',
    creator_name  TEXT,
    creator_org   TEXT,
    tags          TEXT,
    created_at    TEXT,
    updated_at    TEXT,
    json_path     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_type   ON passports(passport_type);
CREATE INDEX IF NOT EXISTS idx_name   ON passports(name);
CREATE INDEX IF NOT EXISTS idx_status ON passports(status);
"""


class RegistryDB:
    """Thin context-manager wrapper around a SQLite passport index."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self) -> "RegistryDB":
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)
        self._conn.commit()
        return self

    def __exit__(self, *_: Any) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Not connected. Use 'with RegistryDB(...) as db:'")
        return self._conn

    # ── Write ──────────────────────────────────────────────────────────────────

    def upsert(self, record: dict[str, Any], json_path: str) -> None:
        creator = record.get("creator") or {}
        self.conn.execute(
            """
            INSERT INTO passports
                (id, passport_type, name, version, status,
                 creator_name, creator_org, tags, created_at, updated_at, json_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name         = excluded.name,
                version      = excluded.version,
                status       = excluded.status,
                creator_name = excluded.creator_name,
                creator_org  = excluded.creator_org,
                tags         = excluded.tags,
                updated_at   = excluded.updated_at,
                json_path    = excluded.json_path
            """,
            (
                record["id"],
                record.get("passport_type", "unknown"),
                record["name"],
                record["version"],
                record.get("status", "draft"),
                creator.get("name") if isinstance(creator, dict) else getattr(creator, "name", None),
                creator.get("organization") if isinstance(creator, dict) else getattr(creator, "organization", None),
                json.dumps(record.get("tags", [])),
                record.get("created_at"),
                record.get("updated_at"),
                json_path,
            ),
        )
        self.conn.commit()

    def delete(self, passport_id: str) -> bool:
        cur = self.conn.execute(
            "DELETE FROM passports WHERE id = ?", (passport_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    # ── Read ───────────────────────────────────────────────────────────────────

    def get(self, passport_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM passports WHERE id = ?", (passport_id,)
        ).fetchone()
        return dict(row) if row else None

    def list_all(
        self,
        passport_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        query  = "SELECT * FROM passports WHERE 1=1"
        params: list[Any] = []
        if passport_type:
            query += " AND passport_type = ?"
            params.append(passport_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY updated_at DESC"
        return [dict(r) for r in self.conn.execute(query, params).fetchall()]

    def search(self, query: str) -> list[dict[str, Any]]:
        """LIKE search over name, creator_name, creator_org."""
        p = f"%{query}%"
        rows = self.conn.execute(
            """
            SELECT * FROM passports
            WHERE name         LIKE ?
               OR creator_name LIKE ?
               OR creator_org  LIKE ?
            ORDER BY updated_at DESC
            """,
            (p, p, p),
        ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT passport_type, COUNT(*) AS n FROM passports GROUP BY passport_type"
        ).fetchall()
        return {r["passport_type"]: r["n"] for r in rows}

    def rebuild_from_records(
        self,
        records: list[tuple[dict[str, Any], str]],
    ) -> None:
        """Wipe and rebuild the index from (passport_dict, relative_json_path) pairs."""
        self.conn.execute("DELETE FROM passports")
        self.conn.commit()
        for record, path in records:
            self.upsert(record, path)
