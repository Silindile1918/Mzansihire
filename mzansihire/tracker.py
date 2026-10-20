"""
tracker.py - saved jobs and applications for each user.

Works with ANY job source: each job is identified by a 'job_key'
(the CSV job_id now, the Adzuna job id later).
"""
import db


def init_tracker():
    """Create the saved_jobs table if it doesn't exist yet."""
    with db.get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_jobs (
                user_id INTEGER NOT NULL,
                job_key TEXT NOT NULL,
                title TEXT,
                company TEXT,
                location TEXT,
                apply_url TEXT,
                status TEXT NOT NULL DEFAULT 'saved',
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                applied_at TEXT,
                PRIMARY KEY (user_id, job_key)
            )
            """
        )


def save_job(user_id, job_key, title, company="", location="", apply_url=""):
    with db.get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO saved_jobs "
            "(user_id, job_key, title, company, location, apply_url) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, str(job_key), title, company, location, apply_url),
        )


def mark_applied(user_id, job_key):
    with db.get_conn() as conn:
        conn.execute(
            "UPDATE saved_jobs SET status = 'applied', applied_at = CURRENT_TIMESTAMP "
            "WHERE user_id = ? AND job_key = ?",
            (user_id, str(job_key)),
        )


def remove_job(user_id, job_key):
    with db.get_conn() as conn:
        conn.execute(
            "DELETE FROM saved_jobs WHERE user_id = ? AND job_key = ?",
            (user_id, str(job_key)),
        )


def get_status_map(user_id):
    """{job_key: 'saved' or 'applied'} for quick look-ups on the job cards."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT job_key, status FROM saved_jobs WHERE user_id = ?", (user_id,)
        ).fetchall()
    return {key: status for key, status in rows}


def get_jobs(user_id, status):
    """Full rows for one status, newest first."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT job_key, title, company, location, apply_url, saved_at, applied_at "
            "FROM saved_jobs WHERE user_id = ? AND status = ? "
            "ORDER BY COALESCE(applied_at, saved_at) DESC",
            (user_id, status),
        ).fetchall()
    cols = ["job_key", "title", "company", "location", "apply_url", "saved_at", "applied_at"]
    return [dict(zip(cols, r)) for r in rows]
