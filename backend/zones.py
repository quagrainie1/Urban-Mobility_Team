import os
import json
import shapefile
from pyproj import Transformer

SHP = "data/taxi_zones.shp"
OUT = "data/zones.geojson"

#state plane -> lat/lon
to_wgs84 =Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)

def read_polygons(path):
    sf = shapefile.Reader(path)
    polys = {} 

    for rec, shp in zip(sf.records(), sf.shapes()):
        zid = rec["LocationID"]
        #print(zid, len(shp.parts))
        if zid not in polys:
            polys[zid] = []

        pts = shp.points
        bounds = list(shp.parts) + [len(pts)]
        for a, b in zip(bounds, bounds[1:]):
            xs, ys = zip(*pts[a:b])  
            lons, lats = to_wgs84.transform(xs, ys)
            ring = []
            for lon, lat in zip(lons, lats):
                ring.append([round(lon, 5), round(lat, 5)])
            polys[zid].append([ring])

    return polys


def main():
    polys = read_polygons(SHP)

    features =  []
    for zid, rings in polys.items():
        features.append({
            "type": "Feature",
            "properties": {"LocationID": zid},
            "geometry": {"type": "MultiPolygon", "coordinates": rings}
        })

    with open(OUT, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)

    print("zones:", len(features))

if __name__ == "__main__":
    main()

