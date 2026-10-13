import os
import json
import sqlite3
import pandas as pd

# start from an empty database every time, so the script can be re-run
os.makedirs("database", exist_ok=True)
if os.path.exists("database/taxi.db"):
    os.remove("database/taxi.db")

conn = sqlite3.connect("database/taxi.db")
conn.executescript(open("database/schema.sql").read())

# zones: lookup csv + boundaries from geojson
zones = pd.read_csv("data/taxi_zone_lookup.csv", keep_default_na=False)
zones = zones.replace("N/A", "Unknown")
geometry = {}
for f in json.load(open("data/zones.geojson"))["features"]:
    geometry[f["properties"]["LocationID"]] = json.dumps(f["geometry"])
zones["geometry"] = zones["LocationID"].map(geometry)
zones.columns = ["location_id", "borough", "zone_name", "service_zone", "geometry"]
zones.to_sql("zones", conn, if_exists="append", index=False)

# small lookup tables
rate_codes = [(1, "Standard"), (2, "JFK"), (3, "Newark"), (4, "Nassau or Westchester"),
              (5, "Negotiated"), (6, "Group ride"), (99, "Unknown")]
payment_types = [(0, "Flex fare"), (1, "Credit card"), (2, "Cash"), (3, "No charge"),
                 (4, "Dispute"), (5, "Unknown"), (6, "Voided")]
conn.executemany("INSERT INTO rate_codes VALUES (?, ?)", rate_codes)
conn.executemany("INSERT INTO payment_types VALUES (?, ?)", payment_types)

# trips
trips = pd.read_parquet("data/clean_trips.parquet")
trips.to_sql("trips", conn, if_exists="append", index=False, chunksize=50000)
conn.commit()
print("zones loaded:", conn.execute("SELECT COUNT(*) FROM zones").fetchone()[0])
print("trips loaded:", conn.execute("SELECT COUNT(*) FROM trips").fetchone()[0])
conn.close()
