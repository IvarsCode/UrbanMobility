import sqlite3
from datetime import datetime
from Models.db import get_connection
from Utils.passwordHandling import input_password, hash_password


class UserController:
    
    def show_menu(self, user):
        if user["role"] == "SystemAdministrator":
            while True:
                print("\n--- System Administrator Menu ---")
                print("1. Add User")
                print("2. Display Users")
                print("3. Logout")
                choice = input("Select an option: ").strip()
                if choice == "1":
                    self.add_user()
                elif choice == "2":
                    self.display_users()
                elif choice == "3":
                    print("Logging out...")
                    break
                else:
                    print("Invalid choice.")
        elif user["role"] == "ServiceEngineer":
            while True:
                print("\n--- Service Engineer Menu ---")
                print("1. Display Users")
                print("2. Logout")
                choice = input("Select an option: ").strip()
                if choice == "1":
                    self.display_users()
                elif choice == "2":
                    print("Logging out...")
                    break
                else:
                    print("Invalid choice.")
    
    
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

                print(f"\nLogin successful! Logged in as {role} ({username})")
                return {"username": username, "role": role}
            else:
                print("\nLogin failed. Invalid username or password.")
                return None

    def add_user(self, addServiceEngineer=False, addSystemAdministrator=False):
        try:
            username = input("Enter username: ").strip()
            password = input_password("Enter password: ").strip()
            confirm_password = input_password("Confirm password: ").strip()

            if password != confirm_password:
                print("Passwords do not match.")
                return

            print("\nSelect role:")
            print("1. ServiceEngineer")
            print("2. SystemAdministrator")
            role_choice = input("Enter number (1 or 2): ").strip()

            role_map = {
                "1": "ServiceEngineer",
                "2": "SystemAdministrator"
            }
            role = role_map.get(role_choice)

            if not role:
                print("nvalid role selected.")
                return

            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()

            with get_connection() as conn:
                cursor = conn.cursor()

                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    print("Username already exists.")
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
                print(f"\nUser '{username}' added successfully with role '{role}'.\n")

        except sqlite3.Error as e:
            print("Database error:", e)

    def display_users(self):
        
        try:
            start = input("Enter starting index (0 for beginning): ").strip()
            if not start.isdigit():
                print("Invalid input. Must be a non-negative number.")
                return

            offset = int(start)

            with get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT username, role FROM users LIMIT 100 OFFSET ?",
                    (offset,)
                )
                users = cursor.fetchall()

                if not users:
                    print("\nNo users found from this starting point.")
                    return

                print(f"\n=== Users List (From {offset} to {offset + len(users) - 1}) ===")
                for username, role in users:
                    print(f"Username: {username} | Role: {role}")

        except Exception as e:
            print("Error fetching users:", e)
    

    def addServiceEngineer(self):
        print("Adding Service Engineer...")
        pass    