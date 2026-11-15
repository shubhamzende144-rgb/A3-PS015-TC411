"""Local SQLite history. WAL mode. The only place diagnostic history is kept."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS diagnostic_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    mode TEXT NOT NULL,
    scenario_id TEXT,
    finding TEXT NOT NULL,
    verdict TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    kind TEXT NOT NULL,
    detail TEXT NOT NULL,
    run_id INTEGER,
    FOREIGN KEY(run_id) REFERENCES diagnostic_runs(id)
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def save_run(self, result: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO diagnostic_runs (mode, scenario_id, finding, verdict, summary, payload) VALUES (?,?,?,?,?,?)",
            (
                result.get("mode", "lab"),
                result.get("id"),
                result.get("finding", "NONE"),
                result.get("verdict", "inconclusive"),
                result.get("technical") or result.get("outcomeDetail") or "",
                json.dumps(result),
            ),
        )
        self._conn.commit()
        run_id = int(cur.lastrowid)
        self._maybe_incident(run_id, result)
        return run_id

    def _maybe_incident(self, run_id: int, result: dict) -> None:
        finding = result.get("finding")
        if finding in (None, "NO_FAULT", "NONE"):
            return
        rows = self._conn.execute(
            "SELECT finding FROM diagnostic_runs ORDER BY id DESC LIMIT 2"
        ).fetchall()
        if len(rows) == 2 and rows[0]["finding"] == rows[1]["finding"] == finding:
            self._conn.execute(
                "INSERT INTO incidents (kind, detail, run_id) VALUES (?,?,?)",
                (finding, f"The same finding repeated: {finding}.", run_id),
            )
            self._conn.commit()

    def runs(self, limit: int = 100) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, created_at, mode, scenario_id, finding, verdict, summary FROM diagnostic_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def run(self, run_id: int) -> dict | None:
        row = self._conn.execute("SELECT payload FROM diagnostic_runs WHERE id = ?", (run_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def incidents(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT id, created_at, kind, detail, run_id FROM incidents ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def set_setting(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._conn.commit()

    def setting(self, key: str, default: str = "") -> str:
        row = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
