import sqlite3
from datetime import datetime
from db.database import get_connection
from auth.password import input_password
from auth.passwordHash import hash_password

class User:
    def __init__(
        self, id: int, 
        userName: str, 
        passwordHash: str, 
        role: str
        ):
        self.id = id
        self.userName = userName
        self.passwordHash = passwordHash
        self.role = role

    def add_user(self):
        
        username = input("Enter username: ").strip()
        password = input_password("Enter password: ").strip()
        confirm_password = input_password("Confirm password: ").strip()

        if password != confirm_password:
            print("Passwords do not match.")
            return
        match self.role:
            case "super_administrator":
                print("=== Adding new user ===")
                print("\nRole of the new user:")
                print("1. service engineer")
                print("2. system administrator")
                role_choice = input("Enter number (1 or 2): ").strip()

                role_map = {
                    "1": "service_engineer",
                    "2": "system_administrator"
                }
                role = role_map.get(role_choice)

                if not role:
                    print("invalid role selected.")
                    return
            case "system_administrator":
                print("=== Adding new service engineer ===")
                role = "service_engineer"
            case "service_engineer":
                print("You are unauthorized to add a user")
                return
        
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                #print(f"username: {username} ({type(username)})")
                # Check if username exists
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    print("Username already exists.")
                    return

                hashed_password = hash_password(password)

                # Insert into users table
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)
                ''', (username, hashed_password, role))
                #print(f"2 username: {username} ({type(username)})")
                # get userId
                cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
                user_id_row = cursor.fetchone()
                if user_id_row is None:
                    print("User not found after insert — unexpected.")
                    return

                user_id = user_id_row[0]
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
            print("=== User display ===")
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