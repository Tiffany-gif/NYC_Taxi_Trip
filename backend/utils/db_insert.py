import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_FILE = os.path.join(BASE_DIR, "data/cleaned/cleaned_trips.csv")

DB_CONFIG = {
    'user': 'root',
    'password': '1mysqlS2025!',
    'host': 'localhost',
    'database': 'trip_data',
    'raise_on_warnings': True
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to database")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit(1)

df = pd.read_csv(CLEANED_FILE)

vendors = df['vendor_id'].dropna().unique()
for vendor in vendors:
    try:
        cursor.execute("INSERT IGNORE INTO vendors (vendor_id) VALUES (%s)", (vendor,))
    except mysql.connector.Error as err:
        print(f"Error inserting vendor {vendor}: {err}")


insert_trip_query = """
INSERT INTO trips (
    vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
    pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude,
    store_and_fwd_flag, trip_duration, trip_distance_km, trip_duration_min,
    speed_kmh, fare_per_km
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for idx, row in df.iterrows():
    try:
        trip_distance = haversine(
            row['pickup_latitude'], row['pickup_longitude'],
            row['dropoff_latitude'], row['dropoff_longitude']
        )
        trip_duration_min = row['trip_duration'] / 60
        speed_kmh = trip_distance / (trip_duration_min / 60) if trip_duration_min > 0 else 0
        fare_per_km = row['fare_amount'] / trip_distance if trip_distance > 0 else 0

        cursor.execute(insert_trip_query, (
            row['vendor_id'],
            row['pickup_datetime'],
            row['dropoff_datetime'],
            int(row['passenger_count']),
            float(row['pickup_longitude']),
            float(row['pickup_latitude']),
            float(row['dropoff_longitude']),
            float(row['dropoff_latitude']),
            row.get('store_and_fwd_flag', 'N'),
            float(row['trip_duration']),
            trip_distance,
            trip_duration_min,
            speed_kmh,
            fare_per_km
        ))
    except mysql.connector.Error as err:
        print(f"Error inserting trip id {idx}: {err}")

conn.commit()
cursor.close()
conn.close()
print("Data inserted successfully!")

