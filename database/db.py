import sqlite3
import os

from utils.helper import hash_password, verify_password

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT,
        prediction TEXT,
        probability REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USERS ---------------- #

def register_user(username, email, password):
    """Create a new user. Passwords are hashed (SHA-256 + static salt, see
    utils.helper.hash_password) before being written to the database — the
    plaintext password is never stored."""
    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    try:
        cur.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, hashed),
        )
        conn.commit()
        conn.close()
        return True, "Registration Successful."

    except sqlite3.IntegrityError as e:
        conn.close()
        # UNIQUE constraint violates on either username or email — figure out which
        if "username" in str(e):
            return False, "That username is already taken."
        return False, "Email already exists."


def verify_user(email, password):
    """Look up a user by email and check the supplied password against the
    stored hash. Returns the user row on success, or None on failure."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()

    if user and verify_password(password, user["password"]):
        return user
    return None


# ---------------- HISTORY ---------------- #

def add_scan_history(user_id, url, prediction, probability):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO predictions(user_id,url,prediction,probability)
        VALUES(?,?,?,?)
        """,
        (user_id, url, prediction, probability),
    )

    conn.commit()
    conn.close()


def get_history(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return rows


def get_user_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM predictions WHERE user_id=?",
        (user_id,),
    )
    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE user_id=? AND prediction='Phishing'
        """,
        (user_id,),
    )
    phishing = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE user_id=? AND prediction='Legitimate'
        """,
        (user_id,),
    )
    safe = cur.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "phishing": phishing,
        "safe": safe,
    }
