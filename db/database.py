# db/database.py

import sqlite3
import os
from auth.password import hash_password

DB_NAME = "data/urban_mobility.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """
    )

    # Check if super_admin exists
    cur.execute(
        "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", ("super_admin",)
    )
    if not cur.fetchone():
        hashed_pw = hash_password("Admin_123?")
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("super_admin", hashed_pw, "super_admin"),
        )
        print("[INFO] Super Admin created with username: super_admin")

    conn.commit()
    conn.close()
