import json
import sqlite3
from flask import Flask, request, jsonify
from algo import top_k_routes


app = Flask(__name__, static_folder="../frontend", static_url_path="")
DB = "database/taxi.db"

def query(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return[dict(row) for row in rows]

@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/api/summary")
def summary():
    rows = query("SELECT COUNT(*) AS trips, AVG(fare_amount) AS avg_fare, "
                 "AVG(trip_distance) AS avg_distance, AVG(duration_min) AS avg_duration FROM trips")
    return jsonify(rows[0])

@app.route("/api/hourly")
def hourly():
    return jsonify(query("SELECT pickup_hour AS hour, COUNT(*) AS trips FROM trips "
                         "GROUP BY pickup_hour ORDER BY pickup_hour"))

@app.route("/api/zones")
def zones():
    rows = query("SELECT z.zone_name, z.borough, z.geometry, COUNT(t.trip_id) AS trips "
                 "FROM zones z LEFT JOIN trips t ON t.pu_zone_id = z.location_id "
                 "GROUP BY z.location_id")
    features = []
    for r in rows:
         if r["geometry"]:
            features.append({"type": "Feature",
                             "properties": {"zone": r["zone_name"], "borough": r["borough"], "trips": r["trips"]},
                             "geometry": json.loads(r["geometry"])})
    return jsonify({"type": "FeatureCollection", "features": features})

@app.route("/api/top-routes")
def top_routes():
    conn = sqlite3.connect(DB)
    pairs = conn.execute("SELECT pu_zone_id,do_zone_id FROM trips")
    top = top_k_routes(pairs, 10)
    conn.close()
    names = {}
    for z in query("SELECT location_id, zone_name FROM zones"):
        names[z["location_id"]] = z["zone_name"]
    result = []
    for (pu, do), count in top:
        result.append({"pickup": names[pu], "dropoff": names[do], "trips":count})
    return jsonify(result)

@app.route("/api/trips")
def trips():
    args = request.args
    sql = ("SELECT t.trip_id, t.pickup_ts, z1.zone_name AS pickup_zone, z2.zone_name AS dropoff_zone, "
           "t.trip_distance, t.duration_min, t.avg_speed_mph, t.fare_amount, t.fare_per_mile "
           "FROM trips t JOIN zones z1 ON z1.location_id = t.pu_zone_id "
           "JOIN zones z2 ON z2.location_id = t.do_zone_id WHERE 1=1")
    params = []
    if args.get("start"):
        sql+= " AND t.pickup_ts >= ?"
        params.append(args.get("start"))
    if args.get("end"):
        sql+= " AND t.pickup_ts <= ?"
        params.append(args.get("end") + " 23:59:59")
    if args.get("min_distance"):
        sql+= " AND t.trip_distance >= ?"
        params.append(args.get("min_distance"))
    if args.get("max_distance"):
        sql+= " AND t.trip_distance <= ?"
        params.append(args.get("max_distance"))
    if args.get("min_fare"):
        sql+= " AND t.fare_amount >= ?"
        params.append(args.get("min_fare"))
    if args.get("max_fare"):
        sql+= " AND t.fare_amount <= ?"
        params.append(args.get("max_fare"))
    if args.get("borough"):
        sql+= " AND z1.borough = ?"
        params.append(args.get("borough"))
    jsonify(query(sql, params))

    sort = args.get("sort", "pickup_ts")
    if sort not in ["pickup_ts", "trip_distance","duration_min","fare_amount"]:
        sort = "pickup_ts"
    order = "ASC" if args.get("order") == "asc" else "DESC"
    page = int(args.get("page", 1))
    sql += " ORDER BY t." + sort + " " + order + " LIMIT 25 OFFSET ?"
    params.append((page - 1) * 25)
    return jsonify(query(sql, params))


if __name__ == "__main__":
    app.run(debug=True)