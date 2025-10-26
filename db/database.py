# db/database.py

import sqlite3
import os
from auth.passwordHash import hash_password
from Utils.encryption import Encryptor

encryptor = Encryptor()

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

    # Profiles table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        registration_date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
    )

    # Scooters table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS scooters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        serial_number TEXT UNIQUE NOT NULL,
        top_speed INTEGER NOT NULL,
        battery_capacity INTEGER NOT NULL,
        soc REAL NOT NULL,
        target_range_min REAL NOT NULL,
        target_range_max REAL NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        out_of_service INTEGER NOT NULL DEFAULT 0,
        mileage INTEGER DEFAULT 0,
        last_maintenance TEXT,
        in_service_date TEXT NOT NULL
    )
    """
    )

    # Travellers table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthday TEXT NOT NULL,
        gender TEXT NOT NULL,
        street_name TEXT NOT NULL,
        house_number TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        city TEXT NOT NULL,
        email TEXT NOT NULL,
        mobile_phone TEXT NOT NULL,
        driving_license_number TEXT NOT NULL
    )
    """
    )

    # Logs table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT NOT NULL,
        log_time TEXT NOT NULL,
        username TEXT,
        activity TEXT NOT NULL,
        additional_info TEXT,
        suspicious INTEGER NOT NULL DEFAULT 0
    )
    """
    )

    # Backups table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        restore_code TEXT,
        assigned_to TEXT,
        used INTEGER DEFAULT 0
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
            (
                encryptor.encrypt_text("super_admin").decode(),  # encrypt username
                hashed_pw,  # keep password hashed
                encryptor.encrypt_text("super_administrator").decode(),
            ),
        )
        print("[INFO] Super Admin created with username: super_admin")

    conn.commit()
    conn.close()
