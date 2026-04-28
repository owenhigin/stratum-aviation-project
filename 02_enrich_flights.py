"""
Step 2: Enrich raw OpenSky flights with airport details.

OpenSky returns ICAO airport codes (e.g. 'KLAX') for departure and arrival.
This script joins those against a public airport database to add:
  - Airport name
  - City, country
  - Latitude, longitude

Uses OurAirports.com's free airports.csv (no API key needed).

Input: flights_all.csv from step 1
Output: flights_enriched.csv
"""

import pandas as pd
import requests
from pathlib import Path
from datetime import datetime, timezone

AIRPORTS_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
AIRPORTS_LOCAL = Path("airports.csv")


def get_airports_db() -> pd.DataFrame:
    if not AIRPORTS_LOCAL.exists():
        print("Downloading airports database from OurAirports.com...")
        r = requests.get(AIRPORTS_URL, timeout=60)
        r.raise_for_status()
        AIRPORTS_LOCAL.write_bytes(r.content)
    df = pd.read_csv(AIRPORTS_LOCAL)
    return df[["ident", "name", "municipality", "iso_country",
               "latitude_deg", "longitude_deg", "type"]]


def main():
    flights = pd.read_csv("flights_all.csv")
    print(f"Loaded {len(flights)} flights")

    # OpenSky's columns of interest
    # estDepartureAirport, estArrivalAirport: ICAO codes (sometimes None)
    # firstSeen, lastSeen: Unix timestamps in seconds
    # icao24: aircraft hex code

    # Convert timestamps
    flights["departure_time"] = pd.to_datetime(
        flights["firstSeen"], unit="s", utc=True)
    flights["arrival_time"] = pd.to_datetime(
        flights["lastSeen"], unit="s", utc=True)
    flights["flight_duration_min"] = (
        (flights["lastSeen"] - flights["firstSeen"]) / 60).round(1)
    flights["flight_date"] = flights["departure_time"].dt.date

    # Load airports
    airports = get_airports_db()
    airports.columns = ["icao", "airport_name", "city",
                        "country", "lat", "lon", "type"]

    # Merge departure
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

    # Merge arrival
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

    # Keep useful columns
    keep = [
        "tail_number", "company_name", "icao24",
        "flight_date", "departure_time", "arrival_time",
        "flight_duration_min",
        "estDepartureAirport", "dep_airport_name", "dep_city",
        "dep_country", "dep_lat", "dep_lon",
        "estArrivalAirport", "arr_airport_name", "arr_city",
        "arr_country", "arr_lat", "arr_lon",
    ]
    keep = [c for c in keep if c in flights.columns]
    flights[keep].to_csv("flights_enriched.csv", index=False)
    print(f"Wrote flights_enriched.csv ({len(flights)} rows)")

    # Quick sanity per company
    print("\nFlights per company:")
    print(flights.groupby("company_name").size().sort_values(ascending=False))

    print("\nTop 15 destinations across all companies:")
    print(flights["arr_city"].value_counts().head(15))


if __name__ == "__main__":
    main()
