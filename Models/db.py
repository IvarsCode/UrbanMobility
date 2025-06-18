import sqlite3
from datetime import datetime

def get_connection():
    return sqlite3.connect("urban_mobility.db")

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('ServiceEngineer', 'SystemAdministrator', 'SuperAdministrator')),
            isLoggedIn BOOLEAN NOT NULL DEFAULT 0 
        )
        ''')

        # Profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')

        # Scooters table
        cursor.execute('''
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
        ''')

        # Travellers table
        cursor.execute('''
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
        ''')

        # Logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            log_time TEXT NOT NULL,
            username TEXT,
            activity TEXT NOT NULL,
            additional_info TEXT,
            suspicious INTEGER NOT NULL DEFAULT 0
        )
        ''')

        # Backups table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            restore_code TEXT,
            assigned_to TEXT,
            used INTEGER DEFAULT 0
        )
        ''')

        conn.commit()