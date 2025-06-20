import re


def validate_username(username):
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_\'\.]{7,9}$"
    return re.match(pattern, username) is not None


def validate_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,30}$"
    return re.match(pattern, password) is not None


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone):

    pattern = r"^\+31-6-\d{8}$"
    return re.match(pattern, phone) is not None


def validate_zip_code(zip_code):
    pattern = r"^\d{4}[A-Z]{2}$"
    return re.match(pattern, zip_code) is not None


def validate_driving_license(license_number):
    pattern = r"^[A-Z]{2}\d{7}$|^[A-Z]\d{8}$"
    not None


def validate_gps_coordinates(latitude, longitude):
    pattern = r"^-?\d{1,2}\.\d{5}$"
    return (
        re.match(pattern, str(latitude)) is not None
        and re.match(pattern, str(longitude)) is not None
    )
