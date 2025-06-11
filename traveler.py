import re
from datetime import date
from typing import Optional


class Traveller:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        birthday: date,
        gender: str,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        email: str,
        mobile_phone: str,
        driving_license_number: str,
    ):

        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = self.validate_zip_code(zip_code)
        self.city = self.validate_city(city)
        self.email = email
        self.mobile_phone = self.validate_mobile(mobile_phone)
        self.driving_license_number = self.validate_license(driving_license_number)

    @staticmethod
    def validate_zip_code(zip_code: str) -> str:
        if not re.match(r"^\d{4}[A-Z]{2}$", zip_code):
            raise ValueError("Zip code must be in the format DDDDXX.")
        return zip_code

    @staticmethod
    def validate_mobile(mobile: str) -> str:
        if not re.match(r"^\+31-6-\d{8}$", mobile) and not re.match(r"^\d{9}$", mobile):
            raise ValueError(
                "Mobile phone must be in the format '+31-6-DDDDDDDD' or 'DDDDDDDDD'."
            )
        return mobile

    @staticmethod
    def validate_license(license_number: str) -> str:
        if not re.match(r"^[Xx]?\d{8}$", license_number):
            raise ValueError(
                "Driving license number must be in the format 'XDDDDDDD' or 'DDDDDDDD'."
            )
        return license_number

    @staticmethod
    def validate_city(city: str) -> str:
        predefined_cities = [
            "Amsterdam",
            "Rotterdam",
            "Utrecht",
            "Eindhoven",
            "Groningen",
            "The Hague",
            "Maastricht",
            "Arnhem",
            "Leiden",
            "Tilburg",
        ]
        if city not in predefined_cities:
            raise ValueError(f"City must be one of: {', '.join(predefined_cities)}")
        return city
