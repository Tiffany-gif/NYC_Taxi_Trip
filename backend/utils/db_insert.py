import os
from typing import Optional, List, Tuple

import numpy as np
import pandas as pd
import mysql.connector

from backend.config.db_connection import get_db_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE_DIR, "data/cleaned")
CLEANED_FILE_DEFAULT = os.path.join(CLEANED_DIR, "cleaned_trips.csv")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def insert_dataframe(df: pd.DataFrame) -> int:
    """Insert a dataframe of trips into the database. Returns number of rows inserted."""
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Database connection failed")

    try:
        cursor = conn.cursor()

        vendors = df['vendor_id'].dropna().unique()
        for vendor in vendors:
            cursor.execute("INSERT IGNORE INTO vendors (vendor_id) VALUES (%s)", (vendor,))

        insert_trip_query = (
            "INSERT INTO trips ("
            "vendor_id, pickup_datetime, dropoff_datetime, passenger_count, "
            "pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, "
            "store_and_fwd_flag, trip_duration, trip_distance_km, trip_duration_min, "
            "speed_kmh, fare_per_km"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        rows_inserted = 0
        for _, row in df.iterrows():
            trip_distance = haversine(
                row['pickup_latitude'], row['pickup_longitude'],
                row['dropoff_latitude'], row['dropoff_longitude']
            )
            trip_duration_min = row['trip_duration'] / 60
            speed_kmh = trip_distance / (trip_duration_min / 60) if trip_duration_min > 0 else 0
            fare_per_km = row['fare_amount'] / trip_distance if trip_distance > 0 else 0

            cursor.execute(
                insert_trip_query,
                (
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
                    fare_per_km,
                ),
            )
            rows_inserted += 1

        conn.commit()
        return rows_inserted
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def insert_from_csv(csv_path: Optional[str] = None) -> int:
    """Load CSV and insert into DB. CSV path defaults to cleaned file."""
    path = csv_path or CLEANED_FILE_DEFAULT
    df = pd.read_csv(path)
    return insert_dataframe(df)


def insert_all_from_cleaned() -> int:
    """Insert all CSV files found in data/cleaned. Returns total rows inserted."""
    if not os.path.isdir(CLEANED_DIR):
        raise FileNotFoundError(f"Cleaned directory not found: {CLEANED_DIR}")

    total = 0
    for name in os.listdir(CLEANED_DIR):
        if not name.lower().endswith('.csv'):
            continue
        csv_path = os.path.join(CLEANED_DIR, name)
        df = pd.read_csv(csv_path)
        total += insert_dataframe(df)
    return total


def _compute_features_chunk(df: pd.DataFrame) -> pd.DataFrame:
    required = [
        'pickup_latitude','pickup_longitude','dropoff_latitude','dropoff_longitude',
        'trip_duration','fare_amount','passenger_count','vendor_id',
        'pickup_datetime','dropoff_datetime'
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    lat1 = df['pickup_latitude'].astype(float)
    lon1 = df['pickup_longitude'].astype(float)
    lat2 = df['dropoff_latitude'].astype(float)
    lon2 = df['dropoff_longitude'].astype(float)

    distances = haversine(lat1, lon1, lat2, lon2)
    duration_min = df['trip_duration'].astype(float) / 60.0
    with np.errstate(divide='ignore', invalid='ignore'):
        speed = np.where(duration_min > 0, distances / (duration_min / 60.0), 0.0)
        fare_per_km = np.where(distances > 0, df['fare_amount'].astype(float) / distances, 0.0)

    out = pd.DataFrame({
        'vendor_id': df['vendor_id'],
        'pickup_datetime': df['pickup_datetime'],
        'dropoff_datetime': df['dropoff_datetime'],
        'passenger_count': df['passenger_count'].astype(int),
        'pickup_longitude': lon1.astype(float),
        'pickup_latitude': lat1.astype(float),
        'dropoff_longitude': lon2.astype(float),
        'dropoff_latitude': lat2.astype(float),
        'store_and_fwd_flag': df.get('store_and_fwd_flag', 'N'),
        'trip_duration': df['trip_duration'].astype(float),
        'trip_distance_km': distances,
        'trip_duration_min': duration_min,
        'speed_kmh': speed,
        'fare_per_km': fare_per_km,
    })

    # Ensure flag is single-char 'Y'/'N'
    out['store_and_fwd_flag'] = out['store_and_fwd_flag'].fillna('N').astype(str).str.upper().str[:1]
    out['store_and_fwd_flag'] = out['store_and_fwd_flag'].where(out['store_and_fwd_flag'].isin(['Y','N']), 'N')
    return out


def insert_from_csv_chunked(csv_path: str, chunksize: int = 50000, batch_size: int = 1000) -> int:
    """Chunked CSV loader for large files. Returns total rows inserted."""
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Database connection failed")

    total_inserted = 0
    try:
        cursor = conn.cursor()

        insert_trip_query = (
            "INSERT INTO trips ("
            "vendor_id, pickup_datetime, dropoff_datetime, passenger_count, "
            "pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, "
            "store_and_fwd_flag, trip_duration, trip_distance_km, trip_duration_min, "
            "speed_kmh, fare_per_km"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        for chunk in pd.read_csv(csv_path, chunksize=chunksize):
            # Upsert vendors for this chunk
            if 'vendor_id' in chunk.columns:
                vendors = chunk['vendor_id'].dropna().unique().tolist()
                for v in vendors:
                    cursor.execute("INSERT IGNORE INTO vendors (vendor_id) VALUES (%s)", (v,))

            prepared = _compute_features_chunk(chunk)

            # Batch executemany for speed
            rows = list(
                zip(
                    prepared['vendor_id'],
                    prepared['pickup_datetime'],
                    prepared['dropoff_datetime'],
                    prepared['passenger_count'].astype(int),
                    prepared['pickup_longitude'].astype(float),
                    prepared['pickup_latitude'].astype(float),
                    prepared['dropoff_longitude'].astype(float),
                    prepared['dropoff_latitude'].astype(float),
                    prepared['store_and_fwd_flag'],
                    prepared['trip_duration'].astype(float),
                    prepared['trip_distance_km'].astype(float),
                    prepared['trip_duration_min'].astype(float),
                    prepared['speed_kmh'].astype(float),
                    prepared['fare_per_km'].astype(float),
                )
            )

            if not rows:
                continue

            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                cursor.executemany(insert_trip_query, batch)
                total_inserted += len(batch)

            conn.commit()

        return total_inserted
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


if __name__ == "__main__":
    count = insert_from_csv()
    print(f"Inserted {count} rows")
