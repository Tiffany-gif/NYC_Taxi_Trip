import pandas as pd
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
RAW_FILE = os.path.join(BASE_DIR, "data/raw/train.csv")
CLEANED_DIR = os.path.join(BASE_DIR, "data/cleaned/")
CLEANED_FILE = os.path.join(CLEANED_DIR, "cleaned_trips.csv")
LOG_FILE = os.path.join(BASE_DIR, "data/logs/excluded_records.log")

# Load raw data
df = pd.read_csv(RAW_FILE)
log = open(LOG_FILE, "w")

# Remove duplicates
duplicates = df[df.duplicated()]
if not duplicates.empty:
    log.write("=== Removed duplicate rows ===\n")
    log.write(duplicates.to_string(index=False) + "\n\n")
df = df.drop_duplicates()

# Remove rows with missing critical columns
critical_cols = [
    "pickup_datetime", "dropoff_datetime",
    "pickup_longitude", "pickup_latitude",
    "dropoff_longitude", "dropoff_latitude",
    "trip_duration"
]
missing_rows = df[df[critical_cols].isnull().any(axis=1)]
if not missing_rows.empty:
    log.write("=== Removed rows with missing critical values ===\n")
    log.write(missing_rows.to_string(index=False) + "\n\n")
df = df.dropna(subset=critical_cols)

# Normalize timestamps and remove invalid dates
df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
df["dropoff_datetime"] = pd.to_datetime(
    df["dropoff_datetime"], errors="coerce")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c


df["trip_distance_km"] = haversine(
    df["pickup_latitude"], df["pickup_longitude"],
    df["dropoff_latitude"], df["dropoff_longitude"]
)

# Save cleaned data
df.to_csv(CLEANED_FILE, index=False)
log.close()

print(
    f"Data cleaning done. Cleaned dataset saved to {CLEANED_FILE} with {len(df)} rows.")
print(f"Excluded rows are logged in {LOG_FILE}")
