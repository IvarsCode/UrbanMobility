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
                print("1. Update password")
                print("2. Display Users")
                print("3. Search for scooter")
                print("4. Logout")
                choice = input("Select an option: ").strip()
                if choice == "1":
                    self.update_password()
                elif choice == "2":
                    self.display_users()
                elif choice == "3":
                    self.search_scooter()
                elif choice == "4":
                    print("Logging out...")
                    self.logOut()
                    break
                else:
                    print("Invalid choice.")
    

    def search_scooter(self):
        print("=== Search for Scooter ===")
        print("1. search on Brand")
        print("2. search on Model")
        print("3. search on Serial Number")
        print("4. search on ID")
        search_choice = input("Select search option: ").strip()

        if search_choice == "1":
            brand = input("Enter scooter brand: ").strip()
            self._search_scooter("brand", brand)
        elif search_choice == "2":
            model = input("Enter scooter model: ").strip()
            self._search_scooter("model", model)
        elif search_choice == "3":
            serial_number = input("Enter scooter serial number: ").strip()
            self._search_scooter("serial_number", serial_number)
        elif search_choice == "4":
            scooter_id = input("Enter scooter ID: ").strip()
            self._search_scooter("id", scooter_id)
        else:
            print("Invalid search option.")

    def _search_scooter(self, column, value):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM scooters WHERE {column}=?",
                (value,)
            )
            scooter = cursor.fetchone()

            if scooter:
                print(f"Scooter found:"
                    f"\nID = {scooter[0]}"
                    f"\nBrand = {scooter[1]}"
                    f"\nModel = {scooter[2]}"
                    f"\nSerial Number = {scooter[3]}"
                    f"\nTop Speed = {scooter[4]} km/h"
                    f"\nBattery Capacity = {scooter[5]} Wh"
                    f"\nState of Charge = {scooter[6]}%"
                    f"\nTarget Range SoC = [{scooter[7]}%, {scooter[8]}%]"
                    f"\nLocation (lat,long)= ({scooter[9]}, {scooter[10]})"
                    f"\nOut of Service = {scooter[11]}"
                    f"\nMileage = {scooter[12]} km"
                    f"\nLast Maintenance Date = {scooter[13]}"
                    f"\nIn Service Date = {scooter[14]}")
            else:
                print("Scooter not found.")


    def update_password(self):
        print("=== Update Password ===")
        username = input("Enter your username: ").strip()
        old_password = input_password("Enter your old password: ").strip()
        new_password = input_password("Enter your new password: ").strip()
        confirm_new_password = input_password("Confirm your new password: ").strip()

        if new_password != confirm_new_password:
            print("New passwords do not match.")
            return

        hashed_old_password = hash_password(old_password)
        hashed_new_password = hash_password(new_password)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username=? AND password=?",
                (username, hashed_old_password)
            )
            user_id = cursor.fetchone()

            if user_id:
                cursor.execute(
                    "UPDATE users SET password=? WHERE id=?",
                    (hashed_new_password, user_id[0])
                )
                conn.commit()
                print("Password updated successfully.")
            else:
                print("Invalid username or old password.")
        
    def logOut(self):
        print("=== Urban Mobility Logout ===")
        username = input("Enter your username to logout: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET isLoggedIn = 0 WHERE username = ?",
                (username,)
            )
            conn.commit()
            print(f"\nUser '{username}' logged out successfully.")

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

    def add_user(self):
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