PRAGMA foreign_keys = ON;


-- create table for the taxi data

-- zones table contains the taxi zones
CREATE TABLE zones (
    location_id INTEGER PRIMARY KEY,
    borough TEXT,
    zone_name TEXT,
    service_zone TEXT,
    geometry TEXT
);
-- table for rate codes
CREATE TABLE rate_codes (
    rate_code_id INTEGER PRIMARY KEY,
    description TEXT
);

-- table for payment types

CREATE TABLE payment_types (
    payment_type_id INTEGER PRIMARY KEY,
    description TEXT
);

-- table for trips

CREATE TABLE trips(
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    pickup_ts TEXT NOT NULL,
    dropoff_ts TEXT NOT NULL,
    passenger_count INTEGER,
    trip_distance REAL NOT NULL,
    rate_code_id INTEGER REFERENCES
    rate_codes(rate_code_id),
    pu_zone_id INTEGER REFERENCES
    zones(location_id),
    do_zone_id INTEGER REFERENCES
    zones(location_id),
    payment_type_id INTEGER REFERENCES
    payment_types(payment_type_id),
    fare_amount REAL NOT NULL,
    tip_amount REAL,
    tolls_amount REAL,
    total_amount REAL,
    duration_min REAL,
    avg_speed_mph REAL,
    fare_per_mile REAL,
    pickup_hour INTEGER
);
--  indexes for the trips table
CREATE INDEX idx_trips_pickup_ts ON trips(pickup_ts);
CREATE INDEX idx_trips_pu_zone ON trips(pu_zone_id);
CREATE INDEX idx_trips_do_zone ON trips(do_zone_id);
CREATE INDEX idx_trips_fare ON trips(fare_amount);
CREATE INDEX idx_trips_distance ON trips(trip_distance);

