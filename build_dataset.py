"""Build an auditable Power BI extract from the USGS Earthquake Catalog.

Run: python build_dataset.py
"""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import statistics
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
PARAMS = {
    "format": "csv",
    "starttime": "2024-01-01",
    "endtime": "2026-01-01",
    "minmagnitude": "5",
    "eventtype": "earthquake",
    "orderby": "time-asc",
}
BASE = "https://earthquake.usgs.gov/fdsnws/event/1/"
QUERY_URL = BASE + "query?" + urllib.parse.urlencode(PARAMS)
COUNT_URL = BASE + "count?" + urllib.parse.urlencode({k: v for k, v in PARAMS.items() if k not in ("format", "orderby")})


def band_magnitude(value):
    if value >= 7:
        return "M7+"
    if value >= 6:
        return "M6-6.9"
    return "M5-5.9"


def band_depth(value):
    if value < 70:
        return "Shallow (<70 km)"
    if value < 300:
        return "Intermediate (70-299 km)"
    return "Deep (300+ km)"


def build():
    with urllib.request.urlopen(QUERY_URL, timeout=60) as response:
        source = response.read()
    (ROOT / "usgs_source.csv").write_bytes(source)
    with urllib.request.urlopen(COUNT_URL, timeout=30) as response:
        api_count = int(response.read().decode().strip())

    rows = list(csv.DictReader(source.decode("utf-8-sig").splitlines()))
    assert len(rows) == api_count, (len(rows), api_count)
    assert len({r["id"] for r in rows}) == len(rows), "Duplicate event IDs"

    curated = []
    for r in rows:
        dt = datetime.fromisoformat(r["time"].replace("Z", "+00:00"))
        mag = float(r["mag"])
        depth = float(r["depth"])
        lat = float(r["latitude"])
        lon = float(r["longitude"])
        assert datetime(2024, 1, 1, tzinfo=timezone.utc) <= dt < datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert r["type"] == "earthquake" and mag >= 5
        assert -90 <= lat <= 90 and -180 <= lon <= 180
        curated.append({
            "event_id": r["id"],
            "event_time_utc": r["time"],
            "event_date": dt.date().isoformat(),
            "year": dt.year,
            "month_start": dt.strftime("%Y-%m-01"),
            "month_label": dt.strftime("%Y-%m"),
            "latitude": lat,
            "longitude": lon,
            "magnitude": mag,
            "magnitude_band": band_magnitude(mag),
            "depth_km": depth,
            "depth_band": band_depth(depth),
            "place": r["place"],
            "magnitude_type": r["magType"],
            "status": r["status"],
            "hemisphere": "Northern" if lat >= 0 else "Southern",
        })

    fields = list(curated[0])
    with (ROOT / "earthquakes_2024_2025_m5plus.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(curated)

    years = Counter(r["year"] for r in curated)
    mag_bands = Counter(r["magnitude_band"] for r in curated)
    depth_bands = Counter(r["depth_band"] for r in curated)
    strongest = max(curated, key=lambda r: r["magnitude"])
    summary = {
        "source_url": QUERY_URL,
        "count_url": COUNT_URL,
        "api_count": api_count,
        "curated_count": len(curated),
        "unique_event_ids": len({r["event_id"] for r in curated}),
        "missing_place_count": sum(not r["place"] for r in curated),
        "status_counts": dict(Counter(r["status"] for r in curated)),
        "magnitude_type_counts": dict(Counter(r["magnitude_type"] for r in curated)),
        "year_counts": dict(sorted(years.items())),
        "magnitude_band_counts": dict(mag_bands),
        "depth_band_counts": dict(depth_bands),
        "m6plus_count": sum(r["magnitude"] >= 6 for r in curated),
        "m7plus_count": sum(r["magnitude"] >= 7 for r in curated),
        "median_depth_km": round(statistics.median(r["depth_km"] for r in curated), 1),
        "strongest_event": {k: strongest[k] for k in ("event_id", "event_time_utc", "magnitude", "place", "depth_km")},
        "min_date": min(r["event_date"] for r in curated),
        "max_date": max(r["event_date"] for r in curated),
        "negative_depth_count": sum(r["depth_km"] < 0 for r in curated),
    }
    (ROOT / "validation_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    build()
