import os
import pandas as pd

# 1. load the trip file and the zone lookup
trips = pd.read_parquet("data/yellow_tripdata.parquet")
lookup = pd.read_csv("data/taxi_zone_lookup.csv", keep_default_na=False)

# 2. keep the columns we need and rename them to match the database
trips = trips[["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
               "trip_distance", "RatecodeID", "PULocationID", "DOLocationID", "payment_type",
               "fare_amount", "tip_amount", "tolls_amount", "total_amount"]]
trips.columns = ["vendor_id", "pickup_ts", "dropoff_ts", "passenger_count",
                 "trip_distance", "rate_code_id", "pu_zone_id", "do_zone_id", "payment_type_id",
                 "fare_amount", "tip_amount", "tolls_amount", "total_amount"]

excluded = []  # every removed row is kept here with the reason


def remove_rows(mask, reason):
    global trips
    bad = trips[mask].copy()
    bad["reason"] = reason
    excluded.append(bad)
    trips = trips[~mask].copy()
    print(reason + ":", len(bad))


# 3. missing values and duplicates
remove_rows(trips[["pickup_ts", "dropoff_ts", "trip_distance", "pu_zone_id",
                   "do_zone_id", "fare_amount"]].isnull().any(axis=1), "missing value")
remove_rows(trips.duplicated(), "duplicate row")

# 4. timestamps: same format, and only the month the file is for
trips["pickup_ts"] = pd.to_datetime(trips["pickup_ts"])
trips["dropoff_ts"] = pd.to_datetime(trips["dropoff_ts"])
main_month = trips["pickup_ts"].dt.to_period("M").mode()[0]
remove_rows(trips["pickup_ts"].dt.to_period("M") != main_month, "pickup outside the file month")

# 5. outliers
trips["duration_min"] = (trips["dropoff_ts"] - trips["pickup_ts"]).dt.total_seconds() / 60
remove_rows((trips["duration_min"] < 1) | (trips["duration_min"] > 180), "duration under 1 or over 180 min")
remove_rows((trips["trip_distance"] <= 0) | (trips["trip_distance"] > 100), "distance 0 or over 100 miles")
remove_rows((trips["fare_amount"] <= 0) | (trips["fare_amount"] > 500), "fare 0 or negative, or over 500")
trips["avg_speed_mph"] = trips["trip_distance"] / (trips["duration_min"] / 60)
remove_rows(trips["avg_speed_mph"] > 80, "average speed over 80 mph")
remove_rows(~trips["pu_zone_id"].isin(lookup["LocationID"]) |
            ~trips["do_zone_id"].isin(lookup["LocationID"]), "zone id not in lookup")

# 6. standardise categories (assumptions: unknown passengers = 1, unknown codes = 99 / 5)
trips["passenger_count"] = trips["passenger_count"].fillna(1)
trips.loc[trips["passenger_count"] == 0, "passenger_count"] = 1
trips["passenger_count"] = trips["passenger_count"].astype(int)
trips.loc[~trips["rate_code_id"].isin([1, 2, 3, 4, 5, 6]), "rate_code_id"] = 99
trips["rate_code_id"] = trips["rate_code_id"].astype(int)
trips.loc[~trips["payment_type_id"].isin([0, 1, 2, 3, 4, 5, 6]), "payment_type_id"] = 5
trips["payment_type_id"] = trips["payment_type_id"].astype(int)
trips["vendor_id"] = trips["vendor_id"].fillna(0).astype(int)

# 7. more derived features (duration_min and avg_speed_mph were made above)
trips["fare_per_mile"] = (trips["fare_amount"] / trips["trip_distance"]).round(2)
trips["pickup_hour"] = trips["pickup_ts"].dt.hour

# 8. save
trips["pickup_ts"] = trips["pickup_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
trips["dropoff_ts"] = trips["dropoff_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
trips["duration_min"] = trips["duration_min"].round(2)
trips["avg_speed_mph"] = trips["avg_speed_mph"].round(2)
os.makedirs("logs", exist_ok=True)
trips.to_parquet("data/clean_trips.parquet", index=False)
pd.concat(excluded).to_csv("logs/excluded_records.csv", index=False)
print("rows kept:", len(trips))
