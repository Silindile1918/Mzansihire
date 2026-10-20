import os
import re
import sqlite3
import bcrypt

DB_PATH = "data/mzansihire.db"


def get_conn():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the users table if it doesn't exist yet."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash BLOB NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def create_user(full_name: str, email: str, password: str):
    """Returns (success, message)."""
    email = email.strip().lower()
    if not full_name.strip():
        return False, "Please enter your full name."
    if not valid_email(email):
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name.strip(), email, hashed),
            )
        return True, "Account created! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def verify_user(email: str, password: str):
    """Returns the user as a dict if the login is correct, otherwise None."""
    email = email.strip().lower()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, full_name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if row and bcrypt.checkpw(password.encode("utf-8"), row[3]):
        return {"id": row[0], "full_name": row[1], "email": row[2]}
    return None


def init_profiles():
    """Create the profiles table if it doesn't exist yet."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY,
                skills TEXT,
                qualification TEXT,
                experience_level TEXT,
                career_interests TEXT,
                preferred_location TEXT,
                about TEXT,
                picture BLOB,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )


PROFILE_FIELDS = [
    "skills", "qualification", "experience_level",
    "career_interests", "preferred_location", "about", "picture",
]


def get_profile(user_id: int):
    """Returns the profile as a dict, or None if the user hasn't saved one yet."""
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {', '.join(PROFILE_FIELDS)} FROM profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return dict(zip(PROFILE_FIELDS, row)) if row else None


def save_profile(user_id: int, data: dict, picture_bytes=None):
    """Saves (or updates) a profile. If no new picture is given, keeps the old one."""
    existing = get_profile(user_id)
    picture = picture_bytes
    if picture is None and existing:
        picture = existing["picture"]

    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO profiles
            (user_id, skills, qualification, experience_level,
             career_interests, preferred_location, about, picture, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                user_id,
                data["skills"],
                data["qualification"],
                data["experience_level"],
                data["career_interests"],
                data["preferred_location"],
                data["about"],
                picture,
            ),
        )