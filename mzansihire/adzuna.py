"""
adzuna.py - fetches live South African jobs from the Adzuna API and keeps
them in our SQLite database, so we don't spend an API call on every click.

Jobs by Adzuna (https://www.adzuna.co.za). Adzuna's terms require this credit
to be shown in the app.
"""
import re

import pandas as pd
import requests

import db

COUNTRY = "za"
BASE_URL = "https://api.adzuna.com/v1/api/jobs"
PER_PAGE = 50                 # jobs per call
MAX_DAYS_OLD = 30             # only ask for adverts from the last 30 days
KEEP_DAYS = 45                # delete stored jobs older than this
REFRESH_COOLDOWN_HOURS = 6    # protects your free monthly call allowance

# Each query = 1 API call. Plus up to 3 from the user's career interests.
BASE_QUERIES = [
    "graduate", "junior", "entry level", "intern", "trainee", "assistant",
    "administrator", "developer", "analyst", "accountant", "marketing",
    "sales", "engineer", "customer service",
]


class AdzunaError(Exception):
    """An error with a message that is safe and friendly to show the user."""


def _strip_tags(text):
    """Adzuna sometimes wraps words in <strong> tags. Remove any HTML tags."""
    return re.sub(r"<[^>]+>", "", str(text or "")).strip()


def init_jobs():
    with db.get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS live_jobs (
                job_key TEXT PRIMARY KEY,
                title TEXT, company TEXT, location TEXT, province TEXT,
                category TEXT, description TEXT, created TEXT, apply_url TEXT,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_refresh_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                refreshed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                jobs_count INTEGER
            )
            """
        )


def normalize(result):
    """Turns one Adzuna result into a simple flat dict."""
    location = result.get("location") or {}
    area = location.get("area") or []
    return {
        "job_key": str(result.get("id", "")),
        "title": _strip_tags(result.get("title")),
        "company": _strip_tags((result.get("company") or {}).get("display_name")),
        "location": _strip_tags(location.get("display_name")),
        "province": area[1] if len(area) > 1 else "",
        "category": _strip_tags((result.get("category") or {}).get("label")),
        "description": _strip_tags(result.get("description")),
        "created": result.get("created") or "",
        "apply_url": result.get("redirect_url") or "",
    }


def fetch(app_id, app_key, query, page=1):
    """One API call. Never puts your keys into an error message."""
    url = f"{BASE_URL}/{COUNTRY}/search/{page}"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": PER_PAGE,
        "what": query,
        "max_days_old": MAX_DAYS_OLD,
        "sort_by": "date",
        "content-type": "application/json",
    }
    try:
        response = requests.get(
            url, params=params, headers={"Accept": "application/json"}, timeout=20
        )
    except requests.RequestException:
        raise AdzunaError("Couldn't reach Adzuna. Check your internet connection and try again.")

    if response.status_code in (401, 403):
        raise AdzunaError("Adzuna did not accept the keys. Check .streamlit/secrets.toml for typos.")
    if response.status_code == 429:
        raise AdzunaError("Adzuna says we've made too many requests. Please try again later.")
    if response.status_code != 200:
        raise AdzunaError(f"Adzuna returned an error (code {response.status_code}). Try again later.")
    try:
        data = response.json()
    except ValueError:
        raise AdzunaError("Adzuna sent a reply we couldn't read. Try again later.")
    return [normalize(r) for r in data.get("results", []) if r.get("id")]


def refresh(app_id, app_key, extra_queries=()):
    """Fetches jobs for all queries and saves them. Returns (count, warning)."""
    queries = list(dict.fromkeys(
        BASE_QUERIES + [q.strip() for q in extra_queries if q and q.strip()]
    ))
    collected = {}
    warning = ""
    for query in queries:
        try:
            rows = fetch(app_id, app_key, query)
        except AdzunaError as error:
            if not collected:
                raise              # nothing worked: show the error, stop spending calls
            warning = f"Stopped early: {error}"
            break
        for row in rows:
            collected[row["job_key"]] = row

    if not collected:
        raise AdzunaError("Adzuna returned no jobs. Try again later.")

    with db.get_conn() as conn:
        for row in collected.values():
            conn.execute(
                "INSERT OR REPLACE INTO live_jobs "
                "(job_key, title, company, location, province, category, description, created, apply_url) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (row["job_key"], row["title"], row["company"], row["location"],
                 row["province"], row["category"], row["description"],
                 row["created"], row["apply_url"]),
            )
        conn.execute(
            "DELETE FROM live_jobs WHERE created != '' "
            "AND substr(created, 1, 10) < date('now', ?)",
            (f"-{KEEP_DAYS} days",),
        )
        total = conn.execute("SELECT COUNT(*) FROM live_jobs").fetchone()[0]
        conn.execute("INSERT INTO job_refresh_log (jobs_count) VALUES (?)", (total,))
    return total, warning


def count_jobs():
    with db.get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM live_jobs").fetchone()[0]


def last_refresh():
    """When the jobs were last refreshed (UTC text), or None."""
    with db.get_conn() as conn:
        return conn.execute("SELECT MAX(refreshed_at) FROM job_refresh_log").fetchone()[0]


def hours_since_refresh():
    with db.get_conn() as conn:
        value = conn.execute(
            "SELECT (julianday('now') - julianday(MAX(refreshed_at))) * 24 FROM job_refresh_log"
        ).fetchone()[0]
    return value  # None if never refreshed


def load_jobs():
    """Stored jobs as a DataFrame with the same columns the recommender uses."""
    with db.get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT job_key, title, company, location, province, category, "
            "description, created, apply_url FROM live_jobs ORDER BY created DESC",
            conn,
        )
    return pd.DataFrame({
        "job_id": df["job_key"],
        "title": df["title"],
        "description": df["description"],
        "job_location": df["location"],
        "job_domain": df["category"],
        "level": "",
        "work_type": "",
        "remote_allowed": False,
        "company": df["company"],
        "apply_url": df["apply_url"],
        "province": df["province"],
        "created": df["created"],
    })
