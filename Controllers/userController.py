import sqlite3
from datetime import datetime
from Models.db import get_connection
from Utils.passwordHandling import input_password, hash_password


class UserController:
    def login(self):
        print("=== Urban Mobility Login ===")
        username = input("Username: ")
        password = input_password("Password: ")

        hashedPassword = hash_password(password)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role FROM users WHERE username=? AND password=?",
                (username, hashedPassword)
            )
            result = cursor.fetchone()

            if result:
                role = result[0]
                cursor.execute(
                    "UPDATE users SET isLoggedIn = 1 WHERE username = ?",
                    (username,)
                )
                conn.commit()

                print(f"\n✅ Login successful! Logged in as {role} ({username})")
                return {"username": username, "role": role}
            else:
                print("\n❌ Login failed. Invalid username or password.")
                return None

    def add_user(self):
        try:
            username = input("Enter username: ").strip()
            password = input_password("Enter password: ").strip()
            confirm_password = input_password("Confirm password: ").strip()

            if password != confirm_password:
                print("❌ Passwords do not match.")
                return

            print("\nSelect role:")
            print("1. ServiceEngineer")
            print("2. SystemAdministrator")
            print("3. SuperAdministrator")
            role_choice = input("Enter number (1-3): ").strip()

            role_map = {
                "1": "ServiceEngineer",
                "2": "SystemAdministrator",
                "3": "SuperAdministrator"
            }
            role = role_map.get(role_choice)

            if not role:
                print("❌ Invalid role selected.")
                return

            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()

            with get_connection() as conn:
                cursor = conn.cursor()

                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    print("❌ Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute('''
                    INSERT INTO users (username, password, role) VALUES (?, ?, ?)
                ''', (username, hashed_password, role))

                user_id = cursor.lastrowid
                reg_date = datetime.now().strftime("%Y-%m-%d")

                # Insert into profiles table
                cursor.execute('''
                    INSERT INTO profiles (user_id, first_name, last_name, registration_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, first_name, last_name, reg_date))

                conn.commit()
                print(f"\n✅ User '{username}' added successfully with role '{role}'.\n")

        except sqlite3.Error as e:
            print("❌ Database error:", e)
        except KeyboardInterrupt:
            print("\n❗ Operation cancelled by user.")