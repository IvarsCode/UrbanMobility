import sqlite3
from datetime import datetime
from Models.db import get_connection
from Models.traveler import Traveller


class TravellerController:
    def add_traveler(self):
        def prompt_validated(prompt_msg, validation_func, error_msg):
            while True:
                try:
                    value = input(prompt_msg).strip()
                    return validation_func(value)
                except ValueError as ve:
                    print(f"❌ {error_msg}: {ve}")
                except KeyboardInterrupt:
                    print("\n❗ Operation cancelled by user.")
                    return None

        try:
            print("=== Add New Traveller ===")
            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()

            def parse_birthday(b):
                return datetime.strptime(b, "%Y-%m-%d").date()

            birthday = prompt_validated(
                "Enter birthday (YYYY-MM-DD): ", parse_birthday, "Invalid date format"
            )
            if birthday is None:
                return

            gender = input("Enter gender (Male/Female): ").strip()
            street_name = input("Enter street name: ").strip()
            house_number = input("Enter house number: ").strip()

            zip_code = prompt_validated(
                "Enter zip code (e.g., 1234AB): ",
                Traveller.validate_zip_code,
                "Invalid zip code format",
            )
            if zip_code is None:
                return

            city = prompt_validated(
                "Enter city: ", Traveller.validate_city, "City not in predefined list"
            )
            if city is None:
                return

            email = input("Enter email: ").strip()

            mobile = prompt_validated(
                "Enter mobile number: ",
                Traveller.validate_mobile,
                "Invalid mobile number",
            )
            if mobile is None:
                return

            license_num = prompt_validated(
                "Enter driving license number: ",
                Traveller.validate_license,
                "Invalid license number format",
            )
            if license_num is None:
                return

            traveller = Traveller(
                first_name,
                last_name,
                birthday,
                gender,
                street_name,
                house_number,
                zip_code,
                city,
                email,
                mobile,
                license_num,
            )

            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO travellers (
                        first_name, last_name, birthday, gender, street_name,
                        house_number, zip_code, city, email, mobile_phone,
                        driving_license_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        traveller.first_name,
                        traveller.last_name,
                        traveller.birthday,
                        traveller.gender,
                        traveller.street_name,
                        traveller.house_number,
                        traveller.zip_code,
                        traveller.city,
                        traveller.email,
                        traveller.mobile_phone,
                        traveller.driving_license_number,
                    ),
                )
                conn.commit()
                print("✅ Traveller added successfully.")

        except KeyboardInterrupt:
            print("\n❗ Operation cancelled by user.")
        except Exception as e:
            print("❌ Error:", e)
