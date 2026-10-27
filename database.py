"""
database.py
===========
All SQL lives in this file. Everything else just calls these functions.

Security note: every query uses "?" placeholders (parameterized queries), so
user text is never pasted into SQL. That prevents SQL injection.

Every function accepts an optional `db_path`, which lets the tests use a
temporary database instead of your real practice history.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "practice.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id   TEXT    NOT NULL,
    question_text TEXT    NOT NULL,
    topic         TEXT    NOT NULL,
    difficulty    TEXT    NOT NULL,
    answer        TEXT    NOT NULL,
    score         REAL    NOT NULL,
    feedback_json TEXT    NOT NULL,
    session_id    TEXT,
    created_at    TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id);
"""


@contextmanager
def get_connection(db_path=None):
    """Open a connection, commit on success, roll back on error, always close."""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # rows behave like dictionaries
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path=None):
    """Create the table if it does not exist yet (safe to call repeatedly)."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)


def _row_to_dict(row):
    data = dict(row)
    try:
        data["feedback"] = json.loads(data.pop("feedback_json"))
    except (TypeError, ValueError):
        data["feedback"] = {}
    return data


def save_attempt(question, answer, result, session_id=None, db_path=None, created_at=None):
    """
    Store one attempt and return its new id. Earlier attempts are never
    overwritten: every call adds a new row.

    question : dict from question_bank
    result   : EvaluationResult (or an equivalent dict)
    """
    result_dict = result.to_dict() if hasattr(result, "to_dict") else dict(result)
    timestamp = created_at or datetime.now().isoformat(timespec="seconds")
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """INSERT INTO attempts
               (question_id, question_text, topic, difficulty, answer, score,
                feedback_json, session_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                question["id"],
                question["question"],
                question["topic"],
                question["difficulty"],
                answer,
                float(result_dict["total_score"]),
                json.dumps(result_dict),
                session_id,
                timestamp,
            ),
        )
        return cursor.lastrowid


def get_all_attempts(db_path=None):
    """All attempts, newest first."""
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM attempts ORDER BY created_at DESC, id DESC").fetchall()
    return [_row_to_dict(row) for row in rows]


def get_attempt(attempt_id, db_path=None):
    """One attempt by id, or None."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_attempts_for_question(question_id, db_path=None):
    """All attempts for one question, oldest first (so you can see progress)."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM attempts WHERE question_id = ? ORDER BY created_at ASC, id ASC",
            (question_id,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def count_attempts(db_path=None):
    with get_connection(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
