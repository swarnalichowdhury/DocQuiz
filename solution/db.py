import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "docquiz.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database file (created on first use)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the two tables if they don't exist yet."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                topic TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL REFERENCES questions(id),
                selected TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                answered_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def clear_quiz() -> None:
    """Wipe questions and answers — called when a new PDF is uploaded."""
    with get_connection() as conn:
        conn.execute("DELETE FROM answers")
        conn.execute("DELETE FROM questions")


def save_questions(questions: list[dict]) -> int:
    """Insert generated questions into the DB. Returns how many were saved.

    Each dict has the shape the LLM returns: question, options (dict),
    correct_answer, explanation, difficulty, topic. The options dict is
    stored as JSON text — same trick as the API: objects at home, text in
    the database.
    """
    with get_connection() as conn:
        for q in questions:
            conn.execute(
                """INSERT INTO questions
                   (question, options_json, correct_answer, explanation, difficulty, topic)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    q["question"],
                    json.dumps(q["options"]),
                    q["correct_answer"],
                    q["explanation"],
                    q["difficulty"],
                    q["topic"],
                ),
            )
    return len(questions)


def get_all_questions() -> list[dict]:
    """Return every question as a dict, options parsed back from JSON."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM questions").fetchall()
    return [_row_to_question(r) for r in rows]


def get_question(question_id: int) -> dict | None:
    """Return one question by id, or None if it doesn't exist."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM questions WHERE id = ?", (question_id,)
        ).fetchone()
    return _row_to_question(row) if row else None


def get_unanswered_questions() -> list[dict]:
    """Questions that don't yet have a row in the answers table."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM questions
            WHERE id NOT IN (SELECT question_id FROM answers)
        """).fetchall()
    return [_row_to_question(r) for r in rows]


def record_answer(question_id: int, selected: str, is_correct: bool) -> None:
    """Store one answered question — this is the app's memory of you."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO answers (question_id, selected, is_correct) VALUES (?, ?, ?)",
            (question_id, selected, int(is_correct)),
        )


def get_topic_stats() -> dict[str, dict]:
    """Per-topic accuracy: {topic: {"correct": n, "total": n}}.

    This is what the adaptive engine reads to find your weak spots.
    """
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT q.topic,
                   SUM(a.is_correct) AS correct,
                   COUNT(*) AS total
            FROM answers a JOIN questions q ON q.id = a.question_id
            GROUP BY q.topic
        """).fetchall()
    return {r["topic"]: {"correct": r["correct"], "total": r["total"]} for r in rows}


def _row_to_question(row: sqlite3.Row) -> dict:
    q = dict(row)
    q["options"] = json.loads(q.pop("options_json"))
    return q
