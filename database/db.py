import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        url TEXT,
        prediction TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# USER FUNCTIONS
# -----------------------------

def register_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, password),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password),
    )

    user = cursor.fetchone()
    conn.close()

    return user


# -----------------------------
# PREDICTION HISTORY
# -----------------------------

def add_scan_history(user_email, url, prediction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions(user_email,url,prediction)
        VALUES(?,?,?)
        """,
        (user_email, url, prediction),
    )

    conn.commit()
    conn.close()


def get_history(user_email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM predictions
        WHERE user_email=?
        ORDER BY created_at DESC
        """,
        (user_email,),
    )

    history = cursor.fetchall()
    conn.close()

    return history


# -----------------------------
# PROFILE
# -----------------------------

def get_user_stats(user_email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM predictions WHERE user_email=?",
        (user_email,),
    )

    total_scans = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE user_email=? AND prediction='Phishing'
        """,
        (user_email,),
    )

    phishing = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        WHERE user_email=? AND prediction='Legitimate'
        """,
        (user_email,),
    )

    legitimate = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total_scans,
        "phishing": phishing,
        "legitimate": legitimate,
    }