CREATE DATABASE IF NOT EXISTS trip_data;
USE trip_data;

CREATE TABLE vendors (
    vendor_id VARCHAR(10) PRIMARY KEY,
    vendor_name VARCHAR(100)
);

CREATE TABLE trips (
   trip_id INT AUTO_INCREMENT PRIMARY KEY,
    
    vendor_id VARCHAR(10) NOT NULL,
    
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    
    passenger_count INT NOT NULL CHECK (passenger_count >= 1),
    
    pickup_longitude FLOAT NOT NULL CHECK (pickup_longitude BETWEEN -180 AND 180) COMMENT 'Longitude in degrees',
    pickup_latitude FLOAT NOT NULL CHECK (pickup_latitude BETWEEN -90 AND 90) COMMENT 'Latitude in degrees',
    
    dropoff_longitude FLOAT NOT NULL CHECK (dropoff_longitude BETWEEN -180 AND 180),
    dropoff_latitude FLOAT NOT NULL CHECK (dropoff_latitude BETWEEN -90 AND 90),
    
    store_and_fwd_flag CHAR(1) DEFAULT 'N' CHECK (store_and_fwd_flag IN ('Y','N')),
    
    trip_duration INT NOT NULL CHECK (trip_duration > 0),
    trip_distance_km FLOAT NOT NULL CHECK (trip_distance_km >= 0),
    trip_duration_min FLOAT NOT NULL CHECK (trip_duration_min > 0),
    speed_kmh FLOAT NOT NULL,
    fare_per_km FLOAT CHECK (fare_per_km >= 0),

    CONSTRAINT fk_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

CREATE INDEX idx_pickup_datetime ON trips (pickup_datetime);
CREATE INDEX idx_dropoff_datetime ON trips (dropoff_datetime);
CREATE INDEX idx_passenger_count ON trips (passenger_count);
CREATE INDEX idx_speed_kmh ON trips (speed_kmh);
CREATE INDEX idx_vendor_time ON trips (vendor_id, pickup_datetime);
CREATE INDEX idx_pickup_coords ON trips (pickup_latitude, pickup_longitude);
CREATE INDEX idx_dropoff_coords ON trips (dropoff_latitude, dropoff_longitude);
