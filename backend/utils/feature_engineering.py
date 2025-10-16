import pandas as pd
import numpy as np
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
CLEANED_FILE = os.path.join(BASE_DIR, "data/cleaned/cleaned_trips.csv")
FEATURED_DIR = os.path.join(BASE_DIR, "data/cleaned/")
FEATURED_FILE = os.path.join(FEATURED_DIR, "featured_trips.csv")
LOG_FILE = os.path.join(BASE_DIR, "data/logs/excluded_records.log")


os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log_message(title, df):
    """Write removed rows to log file"""
    with open(LOG_FILE, "a") as log:
        log.write(f"=== {title} ===\n")
        log.write(df.to_string(index=False) + "\n\n")


def add_features(cleaned_file=CLEANED_FILE, featured_file=FEATURED_FILE):
    """Add derived features, handle outliers, and save featured dataset"""

    df = pd.read_csv(cleaned_file)

    if "trip_duration_min" not in df.columns:
        df["trip_duration_min"] = pd.to_numeric(
            df["trip_duration"], errors="coerce") / 60

    if "speed_kmh" not in df.columns:
        df["trip_distance_km"] = pd.to_numeric(
            df["trip_distance_km"], errors="coerce")
        duration_hours = pd.to_numeric(
            df["trip_duration_min"], errors="coerce") / 60
        duration_hours = duration_hours.replace(
            0, np.nan)  # avoid division by zero
        df["speed_kmh"] = df["trip_distance_km"] / duration_hours

    if "fare_amount" in df.columns:
        df["fare_amount"] = pd.to_numeric(df["fare_amount"], errors="coerce")
        df["fare_per_km"] = df["fare_amount"] / df["trip_distance_km"]
    else:
        df["fare_per_km"] = np.nan

    base_fare = 2.50
    cost_per_km = 4.00

    df["estimated_fare"] = base_fare + (df["trip_distance_km"] * cost_per_km)

    invalid_rows = pd.DataFrame()

    invalid_speed = df[(df["speed_kmh"] <= 0) | (df["speed_kmh"] > 150)]
    if not invalid_speed.empty:
        log_message("Removed unrealistic speeds", invalid_speed)
        invalid_rows = pd.concat([invalid_rows, invalid_speed])

    invalid_fare = df[df["fare_per_km"] <= 0]
    if not invalid_fare.empty:
        log_message("Removed invalid fare/km", invalid_fare)
        invalid_rows = pd.concat([invalid_rows, invalid_fare])

    df = df.drop(index=invalid_rows.index)

    os.makedirs(os.path.dirname(featured_file), exist_ok=True)

    df.to_csv(featured_file, index=False)

    print(
        f"Feature engineering done. Featured dataset saved to {featured_file}")
    print(f"Excluded rows are logged in {LOG_FILE}")

    return df


if __name__ == "__main__":
    add_features()
