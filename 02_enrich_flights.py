"""
Step 2: Enrich per-firm flight CSVs with airport details.

Reads all per-firm CSVs from raw_flights/ (e.g. N543GL.csv, N765M.csv),
enriches each with airport name, city, and coordinates from OurAirports,
and writes <tail>_cleaned.csv alongside the original in raw_flights/.

Uses OurAirports.com's free airports.csv (no API key needed).
"""

import pandas as pd
import requests
import re
from pathlib import Path
from datetime import datetime, timezone

AIRPORTS_URL   = "https://davidmegginson.github.io/ourairports-data/airports.csv"
AIRPORTS_LOCAL = Path("airports.csv")
RAW_DIR        = Path("raw_flights")

MONTHLY_PATTERN = re.compile(r"_\d{4}-\d{2}$")


def get_airports_db():
    if not AIRPORTS_LOCAL.exists():
        print("Downloading airports database from OurAirports.com...")
        r = requests.get(AIRPORTS_URL, timeout=60)
        r.raise_for_status()
        AIRPORTS_LOCAL.write_bytes(r.content)
    df = pd.read_csv(AIRPORTS_LOCAL)
    return df[["ident", "name", "municipality", "iso_country",
               "latitude_deg", "longitude_deg", "type"]]


def enrich(flights, airports):
    flights["departure_time"] = pd.to_datetime(
        flights["firstSeen"], unit="s", utc=True)
    flights["arrival_time"] = pd.to_datetime(
        flights["lastSeen"], unit="s", utc=True)
    flights["flight_duration_min"] = (
        (flights["lastSeen"] - flights["firstSeen"]) / 60).round(1)
    flights["flight_date"] = flights["departure_time"].dt.date

    airports.columns = ["icao", "airport_name", "city",
                        "country", "lat", "lon", "type"]

    flights = flights.merge(
        airports.rename(columns={
            "icao": "estDepartureAirport",
            "airport_name": "dep_airport_name",
            "city": "dep_city",
            "country": "dep_country",
            "lat": "dep_lat",
            "lon": "dep_lon",
            "type": "dep_type",
        }),
        on="estDepartureAirport", how="left",
    )
    flights = flights.merge(
        airports.rename(columns={
            "icao": "estArrivalAirport",
            "airport_name": "arr_airport_name",
            "city": "arr_city",
            "country": "arr_country",
            "lat": "arr_lat",
            "lon": "arr_lon",
            "type": "arr_type",
        }),
        on="estArrivalAirport", how="left",
    )

    keep = [
        "tail_number", "company_name", "icao24",
        "flight_date", "departure_time", "arrival_time",
        "flight_duration_min",
        "estDepartureAirport", "dep_airport_name", "dep_city",
        "dep_country", "dep_lat", "dep_lon",
        "estArrivalAirport", "arr_airport_name", "arr_city",
        "arr_country", "arr_lat", "arr_lon",
    ]
    return flights[[c for c in keep if c in flights.columns]]


def main():
    # Find all per-firm CSVs — skip monthly files and already-cleaned files
    firm_csvs = [
        f for f in sorted(RAW_DIR.glob("N*.csv"))
        if not f.stem.endswith("_cleaned")
        and not MONTHLY_PATTERN.search(f.stem)
    ]

    if not firm_csvs:
        print("No per-firm CSVs found in raw_flights/")
        return

    airports = get_airports_db()

    for csv in firm_csvs:
        tail = csv.stem
        out  = RAW_DIR / f"{tail}_cleaned.csv"

        if out.exists():
            print(f"{tail}: already cleaned — skipping")
            continue

        flights = pd.read_csv(csv)
        if flights.empty:
            print(f"{tail}: empty — skipping")
            continue

        cleaned = enrich(flights, airports.copy())
        cleaned.to_csv(out, index=False)
        print(f"{tail}: {len(cleaned)} flights -> {out}")

        print(f"  Top destinations:")
        print(cleaned["arr_city"].value_counts().head(5).to_string())
        print()


if __name__ == "__main__":
    main()
