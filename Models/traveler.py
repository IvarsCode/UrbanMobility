from datetime import datetime
import re
from db.database import get_connection
from ui.terminal import clear_terminal


class Traveller:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        email: str,
        mobile_phone: str,
        driving_license_number: str,
    ):
        # Validation
        if not re.fullmatch(r"\d{4}[A-Z]{2}", zip_code):
            raise ValueError("Zip code must be in the format 1234AB.")
        if not re.fullmatch(r"06\d{8}", mobile_phone):
            raise ValueError("Mobile phone must start with 06 and be 10 digits long.")
        if not re.fullmatch(r"[A-Z0-9]{8,12}", driving_license_number):
            raise ValueError(
                "Driving license number must be 8–12 alphanumeric characters."
            )
        if len(street_name) < 2:
            raise ValueError("Street name must be at least 2 characters.")
        if not re.fullmatch(r"\d+[A-Za-z]?", house_number):
            raise ValueError(
                "House number must be numeric, optionally with a letter (e.g., 12A)."
            )
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format.")
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Birthday must be in format YYYY-MM-DD.")

        # Assign
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email = email
        self.mobile_phone = mobile_phone
        self.driving_license_number = driving_license_number

    def add_to_db(self):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO travellers (
                    first_name, last_name, birthday, gender, street_name,
                    house_number, zip_code, city, email, mobile_phone, driving_license_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.first_name,
                    self.last_name,
                    self.birthday,
                    self.gender,
                    self.street_name,
                    self.house_number,
                    self.zip_code,
                    self.city,
                    self.email,
                    self.mobile_phone,
                    self.driving_license_number,
                ),
            )
            conn.commit()
            print("[SUCCESS] Traveller added to database.")

    @staticmethod
    def update_traveller():
        print("=== Update Traveller ===")
        traveller_id = input("Enter traveller ID to update: ").strip()

        # Map of allowed columns and their validation rules
        fields = {
            "first_name": {
                "pattern": r"[A-Za-z\-]{2,}",
                "error": "Must be at least 2 letters.",
            },
            "last_name": {
                "pattern": r"[A-Za-z\-]{2,}",
                "error": "Must be at least 2 letters.",
            },
            "birthday": {"validator": validate_date},
            "gender": {"pattern": r"[MFO]", "error": "Must be M, F, or O."},
            "street_name": {
                "pattern": r".{2,}",
                "error": "Street name must be at least 2 characters.",
            },
            "house_number": {
                "pattern": r"\d+[A-Za-z]?",
                "error": "Must be numeric, optionally with a letter.",
            },
            "zip_code": {
                "pattern": r"\d{4}[A-Z]{2}",
                "error": "Must be in format 1234AB.",
            },
            "city": {"pattern": r".{2,}", "error": "Must be at least 2 characters."},
            "email": {
                "pattern": r"[^@]+@[^@]+\.[^@]+",
                "error": "Invalid email address.",
            },
            "mobile_phone": {
                "pattern": r"06\d{8}",
                "error": "Must start with 06 and be 10 digits.",
            },
            "driving_license_number": {
                "pattern": r"[A-Z0-9]{8,12}",
                "error": "Must be 8–12 alphanumeric characters.",
            },
        }

        print("Available fields to update:")
        for i, field in enumerate(fields.keys(), 1):
            print(f"{i}. {field}")

        field_choice = input("Enter the field name to update: ").strip()
        if field_choice not in fields:
            print("[ERROR] Invalid field.")
            return

        field = fields[field_choice]
        pattern = field.get("pattern")
        error_msg = field.get("error", "Invalid input.")
        validator = field.get("validator")

        new_value = get_valid_input(
            f"Enter new value for {field_choice}: ", pattern, error_msg, validator
        )

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE travellers SET {field_choice} = ? WHERE id = ?",
                (new_value, traveller_id),
            )
            conn.commit()
            print(f"[SUCCESS] Traveller's {field_choice} updated.")

    @staticmethod
    def delete_traveller():
        print("=== Delete Traveller ===")
        traveller_id = input("Enter traveller ID to delete: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM travellers WHERE id = ?", (traveller_id,))
            conn.commit()
            print("[SUCCESS] Traveller deleted.")

    @staticmethod
    def search_traveller():
        print("=== Search Traveller ===")
        print("1. By ID")
        print("2. By Name")
        choice = input("Choose option: ").strip()

        with get_connection() as conn:
            cursor = conn.cursor()
            if choice == "1":
                traveller_id = input("Enter ID: ").strip()
                cursor.execute("SELECT * FROM travellers WHERE id = ?", (traveller_id,))
            elif choice == "2":
                name = input("Enter first or last name: ").strip()
                cursor.execute(
                    "SELECT * FROM travellers WHERE first_name LIKE ? OR last_name LIKE ?",
                    (f"%{name}%", f"%{name}%"),
                )
            else:
                print("[ERROR] Invalid option.")
                return

            result = cursor.fetchall()
            if result:
                for t in result:
                    Traveller.print_info(t)
            else:
                print("[INFO] No traveller found.")

    @staticmethod
    def print_info(traveller_data: tuple):
        print(
            f"\nTraveller ID: {traveller_data[0]}"
            f"\nFirst Name: {traveller_data[1]}"
            f"\nLast Name: {traveller_data[2]}"
            f"\nBirthday: {traveller_data[3]}"
            f"\nGender: {traveller_data[4]}"
            f"\nStreet Name: {traveller_data[5]}"
            f"\nHouse Number: {traveller_data[6]}"
            f"\nZip Code: {traveller_data[7]}"
            f"\nCity: {traveller_data[8]}"
            f"\nEmail: {traveller_data[9]}"
            f"\nMobile Phone: {traveller_data[10]}"
            f"\nDriving License #: {traveller_data[11]}"
        )

    @staticmethod
    def get_all_travellers():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM travellers")
            return cursor.fetchall()


def get_valid_input(prompt, pattern=None, error_msg=None, validator=None):
    while True:
        value = input(prompt).strip()
        if pattern and not re.fullmatch(pattern, value):
            print(f"[ERROR] {error_msg}")
            continue
        if validator:
            try:
                validator(value)
            except ValueError as ve:
                print(f"[ERROR] {ve}")
                continue
        return value


def validate_date(date_str):
    datetime.strptime(date_str, "%Y-%m-%d")  # Will raise ValueError if invalid


def manage_traveller():
    while True:
        clear_terminal()
        print("\n=== Manage Travellers ===")
        print("1. Add Traveller")
        print("2. Update Traveller")
        print("3. Delete Traveller")
        print("4. Search Traveller")
        print("5. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            try:
                first_name = get_valid_input(
                    "First name: ",
                    r"[A-Za-z\-]{2,}",
                    "First name must be at least 2 letters.",
                )
                last_name = get_valid_input(
                    "Last name: ",
                    r"[A-Za-z\-]{2,}",
                    "Last name must be at least 2 letters.",
                )
                gender = get_valid_input(
                    "Gender (M/F/O): ", r"[MFO]", "Gender must be M, F, or O."
                )
                birthday = get_valid_input(
                    "Birthday (YYYY-MM-DD): ", validator=validate_date
                )
                zip_code = get_valid_input(
                    "Zip Code (e.g., 1234AB): ",
                    r"\d{4}[A-Z]{2}",
                    "Format must be 1234AB.",
                )
                city = get_valid_input(
                    "City: ", r".{2,}", "City name must be at least 2 characters."
                )
                street_name = get_valid_input(
                    "Street Name: ",
                    r".{2,}",
                    "Street name must be at least 2 characters.",
                )
                house_number = get_valid_input(
                    "House Number: ",
                    r"\d+[A-Za-z]?",
                    "Must be numeric, optionally with a letter.",
                )

                mobile_phone = get_valid_input(
                    "Mobile Phone (06XXXXXXXX): ",
                    r"06\d{8}",
                    "Must start with 06 and be 10 digits.",
                )
                email = get_valid_input(
                    "Email: ", r"[^@]+@[^@]+\.[^@]+", "Invalid email address format."
                )

                driving_license_number = get_valid_input(
                    "Driving License Number: ",
                    r"[A-Z0-9]{8,12}",
                    "Must be 8–12 alphanumeric characters.",
                )

                t = Traveller(
                    first_name,
                    last_name,
                    birthday,
                    gender,
                    street_name,
                    house_number,
                    zip_code,
                    city,
                    email,
                    mobile_phone,
                    driving_license_number,
                )
                t.add_to_db()

            except Exception as e:
                print(f"[ERROR] {e}")

        elif choice == "2":
            clear_terminal()
            Traveller.update_traveller()
            

        elif choice == "3":
            clear_terminal()
            Traveller.delete_traveller()

        elif choice == "4":
            clear_terminal()
            Traveller.search_traveller()

        elif choice == "5":
            clear_terminal()
            print("Exiting...")
            break
        else:
            clear_terminal()
            print("[ERROR] Invalid choice. Please try again.")
