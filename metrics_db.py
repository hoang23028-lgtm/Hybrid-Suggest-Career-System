from kbs.metrics_db import *  # noqa: F401,F403

"""
SQLite metrics storage for step 7 (continuous updates).

This module provides a minimal, backwards-compatible schema migration layer
on top of the existing `model_metrics.db` shipped in the repo.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


DEFAULT_DB_PATH = Path(__file__).parent / "model_metrics.db"


@dataclass(frozen=True)
class MetricsRow:
    block: str
    system: str  # "ml" | "hybrid" | "kbs"
    accuracy: float
    precision: float
    recall: float
    f1: float
    num_samples: int
    run_id: str
    timestamp: str
    details: Optional[dict[str, Any]] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON")
    return con


def ensure_schema(con: sqlite3.Connection) -> None:
    """
    Ensure required columns exist.

    Existing tables in repo:
      - metrics(id, timestamp, block, accuracy, precision, recall, f1, num_samples)
      - alerts(...)
      - predictions(...)
    """
    cur = con.cursor()

    # Create baseline table if DB is empty (fresh environments).
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          block TEXT NOT NULL,
          accuracy REAL,
          precision REAL,
          recall REAL,
          f1 REAL,
          num_samples INTEGER
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          level TEXT,
          block TEXT,
          message TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          block TEXT NOT NULL,
          predicted_major TEXT,
          actual_major TEXT,
          score REAL,
          correct BOOLEAN
        )
        """
    )

    # Lightweight migrations (idempotent).
    cur.execute("PRAGMA table_info(metrics)")
    cols = {r[1] for r in cur.fetchall()}

    if "system" not in cols:
        cur.execute("ALTER TABLE metrics ADD COLUMN system TEXT NOT NULL DEFAULT 'ml'")
    if "run_id" not in cols:
        cur.execute("ALTER TABLE metrics ADD COLUMN run_id TEXT")
    if "details_json" not in cols:
        cur.execute("ALTER TABLE metrics ADD COLUMN details_json TEXT")

    con.commit()


def insert_metrics(con: sqlite3.Connection, row: MetricsRow) -> None:
    ensure_schema(con)
    details_json = json.dumps(row.details, ensure_ascii=False) if row.details else None
    con.execute(
        """
        INSERT INTO metrics (timestamp, block, system, accuracy, precision, recall, f1, num_samples, run_id, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row.timestamp,
            row.block,
            row.system,
            float(row.accuracy) if row.accuracy is not None else None,
            float(row.precision) if row.precision is not None else None,
            float(row.recall) if row.recall is not None else None,
            float(row.f1) if row.f1 is not None else None,
            int(row.num_samples) if row.num_samples is not None else None,
            row.run_id,
            details_json,
        ),
    )
    con.commit()


def log_alert(con: sqlite3.Connection, level: str, block: str, message: str) -> None:
    ensure_schema(con)
    con.execute(
        "INSERT INTO alerts (timestamp, level, block, message) VALUES (?, ?, ?, ?)",
        (_utc_now_iso(), level, block, message),
    )
    con.commit()


def fetch_recent_metrics(
    con: sqlite3.Connection, *, block: str, system: str, limit: int = 10
) -> list[dict[str, Any]]:
    """
    Fetch most recent metric rows for a given block+system.

    Returns dicts with keys: timestamp, accuracy, precision, recall, f1, num_samples, run_id.
    """
    ensure_schema(con)
    cur = con.cursor()
    cur.execute(
        """
        SELECT timestamp, accuracy, precision, recall, f1, num_samples, run_id
        FROM metrics
        WHERE block = ? AND system = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (block, system, int(limit)),
    )
    rows = []
    for ts, acc, prec, rec, f1, n, run_id in cur.fetchall():
        rows.append(
            {
                "timestamp": ts,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1": f1,
                "num_samples": n,
                "run_id": run_id,
            }
        )
    return rows


def alert_if_degraded(
    con: sqlite3.Connection,
    *,
    block: str,
    system: str,
    new_accuracy: float,
    baseline_window: int = 5,
    degrade_threshold_abs: float = 0.02,
) -> None:
    """
    Compare `new_accuracy` vs rolling mean of recent `baseline_window` runs (excluding current run)
    and log an alert if degraded by more than `degrade_threshold_abs`.
    """
    recent = fetch_recent_metrics(con, block=block, system=system, limit=baseline_window + 1)
    # recent[0] will often be current run if caller inserted first; exclude run_id checks in caller.
    if len(recent) < 2:
        return

    # Drop the most recent row (assumed current insertion).
    baseline_rows = recent[1 : baseline_window + 1]
    baseline_accs = [r["accuracy"] for r in baseline_rows if isinstance(r["accuracy"], (int, float))]
    if len(baseline_accs) < max(1, baseline_window // 2):
        return

    baseline_mean = sum(baseline_accs) / len(baseline_accs)
    delta = float(new_accuracy) - float(baseline_mean)
    if delta <= -abs(degrade_threshold_abs):
        log_alert(
            con,
            level="warning",
            block=block,
            message=(
                f"{system.upper()} accuracy degraded: new={new_accuracy:.4f}, "
                f"baseline_mean(last {len(baseline_accs)})={baseline_mean:.4f}, "
                f"delta={delta:.4f}"
            ),
        )


def new_run_id(prefix: str = "run") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}"

