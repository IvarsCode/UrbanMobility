import sqlite3
import random
from Models.db import get_connection
from datetime import datetime, timedelta

# Connect
with get_connection() as conn:
    cursor = conn.cursor()

# Generate a random serial number (10–17 alphanumeric)
def generate_serial():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=random.randint(10, 17)))

# Generate a random date within a range
def random_date(start_days_ago, end_days_ago):
    days_ago = random.randint(start_days_ago, end_days_ago)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime('%Y-%m-%d')

# Generate a single scooter record
def generate_scooter():
    brand = random.choice(["Xiaomi", "Segway", "Ninebot", "Razor", "Bird"])
    model = brand[:3].upper() + str(random.randint(100, 999))
    serial_number = generate_serial()
    top_speed = random.randint(20, 45)  # km/h
    battery_capacity = random.randint(250, 600)  # Wh
    soc = round(random.uniform(5.0, 100.0), 1)
    target_range_min = round(random.uniform(10.0, 30.0), 1)
    target_range_max = round(random.uniform(50.0, 90.0), 1)
    latitude = round(random.uniform(-90.0, 90.0), 6)
    longitude = round(random.uniform(-180.0, 180.0), 6)
    out_of_service = random.choice([0, 1])
    mileage = round(random.uniform(100.0, 10000.0), 1)
    last_maintenance = random_date(0, 180)
    in_service_date = random_date(180, 1000)

    return (
        brand, model, serial_number, top_speed, battery_capacity, soc,
        target_range_min, target_range_max, latitude, longitude,
        out_of_service, mileage, last_maintenance, in_service_date
    )

# Insert multiple dummy scooters
def insert_dummy_scooters(n=20):
    for _ in range(n):
        scooter = generate_scooter()
        cursor.execute("""
            INSERT INTO scooters (
                brand, model, serial_number, top_speed, battery_capacity, soc,
                target_range_min, target_range_max, latitude, longitude,
                out_of_service, mileage, last_maintenance, in_service_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, scooter)
    conn.commit()
    print(f"{n} dummy scooter records inserted.")

# Run to run
insert_dummy_scooters(50) 
