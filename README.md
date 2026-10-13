# Urban Mobility – NYC Taxi Dashboard (Team)

## Data pipeline (Person 1)

### 1. Install
```
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install pandas pyarrow pyshp pyproj
```

### 2. Put the data in `data/`
The zone files are already in the repo. The trip file is too big for Git, so download it yourself:

| File | Where it comes from | Save it as |
|---|---|---|
| Yellow taxi trips, January 2019 | NYC TLC Trip Record Data page | `data/yellow_tripdata.parquet` |
| Taxi zone lookup | NYC TLC Trip Record Data page (already in repo) | `data/taxi_zone_lookup.csv` |
| Taxi zone shapefile | NYC TLC Trip Record Data page (already in repo) | `data/taxi_zones.shp`, `.shx`, `.dbf`, `.prj` |

If you downloaded the trips as a CSV, convert it once:
```
python -c "import pandas as pd; pd.read_csv('data/yellow_tripdata_2019-01.csv', low_memory=False).to_parquet('data/yellow_tripdata.parquet', index=False)"
```

### 3. Run the three scripts (from the project folder, in this order)
```
python backend/zones.py      # shapefile -> data/zones.geojson
python backend/clean.py      # cleans trips -> data/clean_trips.parquet + logs/excluded_records.csv
python backend/load_db.py    # builds database/taxi.db (needs database/schema.sql)
```
`load_db.py` deletes and rebuilds `database/taxi.db` each time, so it is safe to run again.

### Cleaning rules
Every removed row is saved in `logs/excluded_records.csv` with a `reason` column.

| Rule | Why |
|---|---|
| Missing pickup/dropoff time, distance, zone or fare | the trip can't be used without them |
| Exact duplicate rows | same trip recorded twice |
| Pickup not in the file's month | wrong dates (e.g. 2008, 2088) in the raw file |
| Duration under 1 min or over 3 hours | meter tests / meter left running |
| Distance 0 or over 100 miles | no movement, or GPS/meter errors |
| Fare 0 or less, or over $500 | refunds, voids and typos |
| Average speed over 80 mph | not physically possible in NYC |
| Zone id not in the lookup table | can't be shown on the map |

Assumptions: missing or 0 passengers counted as 1; unknown rate code set to 99; unknown payment type set to 5 (Unknown); "N/A" borough/zone shown as "Unknown".

Derived columns: `duration_min`, `avg_speed_mph`, `fare_per_mile`, `pickup_hour`.
