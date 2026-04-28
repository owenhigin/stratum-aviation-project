"""
Step 1 (v4): Pull flight data with proper rate-limit handling.

Changes from v3:
  - Shorter default window (6 months) for testing
  - Reads X-Rate-Limit-Remaining and X-Rate-Limit-Retry-After-Seconds headers
  - HARD STOP on 429 instead of retry loop (preserves remaining credits)
  - Prints credit balance after each call so you can see what's happening
  - Single-aircraft test mode controlled by TEST_MODE flag

How OpenSky credits work:
  - Authenticated users get 4000 credits/day
  - The /flights/aircraft endpoint costs more than 1 credit when querying
    historical data (empirically observed: ~50 calls exhausts 4000 credits,
    so each call costs ~80 credits when querying days in the past)
  - Quota resets at midnight UTC (8 PM Eastern in winter / 7 PM in summer)

REQUIRED — set up an API Client first:
  1. Log in at https://opensky-network.org
  2. Account -> API Client -> Create new API Client
  3. Set OPENSKY_CLIENT_ID and OPENSKY_CLIENT_SECRET below or as env vars
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---- CONFIG ----
#FILL IN YOUR INFORMATION NOT MINE
CLIENT_ID = os.environ.get("OPENSKY_CLIENT_ID", "owenhigin@gmail.com-api-client")
CLIENT_SECRET = os.environ.get("OPENSKY_CLIENT_SECRET", "Nx4YMWTtyhV6yxSOTmbg6FcqiuEgbxTN")

# CUT WINDOW: 6 months for the test run.
# Once we know this works, we can expand to 12 months (with pooled accounts).
START_DATE = datetime(2024, 10, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 4, 1, tzinfo=timezone.utc)

# Test mode: only pull the first aircraft. Set to False after verifying.
TEST_MODE = False

# 2-day chunks (OpenSky's enforced limit)
CHUNK_DAYS = 2
REQUEST_DELAY = 0.5  # seconds between requests

AIRCRAFT_FILE = Path("Final_Company_Aircraft.xlsx")
RAW_DIR = Path("raw_flights")
RAW_DIR.mkdir(exist_ok=True)

TOKEN_URL = ("https://auth.opensky-network.org/auth/realms/opensky-network"
             "/protocol/openid-connect/token")
API_BASE = "https://opensky-network.org/api"


class QuotaExhausted(Exception):
    """Raised when the daily API quota is gone. Try again tomorrow."""
    pass


class OpenSkyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expires_at = 0
        self.last_remaining = None  # most recent X-Rate-Limit-Remaining

    def _fetch_token(self):
        print("  [auth] fetching new access token...")
        r = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=30,
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Token request failed: HTTP {r.status_code} - {r.text}\n\n"
                f"Check your CLIENT_ID and CLIENT_SECRET.")
        data = r.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 1800) - 300
        print("  [auth] token obtained")

    def _ensure_token(self):
        if self._token is None or time.time() >= self._token_expires_at:
            self._fetch_token()

    def get(self, path: str, params: dict = None) -> requests.Response:
        self._ensure_token()
        url = f"{API_BASE}{path}"
        r = requests.get(
            url,
            params=params or {},
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=60,
        )
        # Track remaining quota from response headers
        remaining = r.headers.get("X-Rate-Limit-Remaining")
        if remaining is not None:
            try:
                self.last_remaining = int(remaining)
            except ValueError:
                pass
        return r


def fetch_flights_for_aircraft(client: OpenSkyClient, icao24: str,
                               start: datetime, end: datetime) -> list:
    """Pull flights for one aircraft. Raises QuotaExhausted on 429."""
    all_flights = []
    chunk_start = start
    total_chunks = 0
    chunks_with_flights = 0

    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=CHUNK_DAYS), end)
        params = {
            "icao24": icao24.lower(),
            "begin": int(chunk_start.timestamp()),
            "end": int(chunk_end.timestamp()),
        }
        total_chunks += 1

        try:
            r = client.get("/flights/aircraft", params=params)

            if r.status_code == 200:
                flights = r.json()
                if flights:
                    all_flights.extend(flights)
                    chunks_with_flights += 1
                    rem = (f"  [credits left: {client.last_remaining}]"
                           if client.last_remaining is not None else "")
                    print(f"    {chunk_start.date()}: {len(flights)} "
                          f"flights{rem}")
            elif r.status_code == 404:
                pass  # no flights, common
            elif r.status_code == 429:
                retry_after = r.headers.get(
                    "X-Rate-Limit-Retry-After-Seconds", "unknown")
                print(f"\n  [QUOTA EXHAUSTED] HTTP 429")
                print(f"  X-Rate-Limit-Retry-After-Seconds: {retry_after}")
                if retry_after != "unknown":
                    try:
                        secs = int(retry_after)
                        hrs = secs / 3600
                        print(f"  -> wait approximately {hrs:.1f} hours "
                              f"before retrying")
                    except ValueError:
                        pass
                print(f"  -> stopping with {len(all_flights)} flights "
                      f"collected for this aircraft")
                raise QuotaExhausted()
            else:
                print(f"    {chunk_start.date()}: HTTP {r.status_code} - "
                      f"{r.text[:120]}")
        except QuotaExhausted:
            raise
        except Exception as e:
            print(f"    {chunk_start.date()}: error: {e}")

        chunk_start = chunk_end

        if total_chunks % 25 == 0:
            rem = (f", credits left: {client.last_remaining}"
                   if client.last_remaining is not None else "")
            print(f"    [progress] {total_chunks} chunks done, "
                  f"{len(all_flights)} flights so far{rem}")

        time.sleep(REQUEST_DELAY)

    print(f"  summary: {total_chunks} chunks, {chunks_with_flights} with "
          f"flights, {len(all_flights)} total flights")
    return all_flights


def main():
    if CLIENT_ID.startswith("PASTE_") or CLIENT_SECRET.startswith("PASTE_"):
        print("ERROR: Set CLIENT_ID and CLIENT_SECRET first")
        return

    df = pd.read_excel(AIRCRAFT_FILE)
    df["icao24"] = df["icao24"].astype(str).str.strip().str.upper()
    # Focal companies only
    FOCAL_COMPANIES = ["Liberty Media Corp", "Workday, Inc.", "CENTERPOINT ENERGY INC"]
    df = df[df["company_name"].isin(FOCAL_COMPANIES)].reset_index(drop=True)

    print(f"Filtered to {len(df)} focal aircraft:")
    for _, row in df.iterrows():
        print(f"  {row['company_name']}")
    if len(df) != 3:
        print(f"WARNING: expected 3 focal companies, got {len(df)}. Check names match spreadsheet exactly.")
        return

    if TEST_MODE:
        df = df.head(1)
        print(f"TEST MODE: only pulling first aircraft\n")
    else:
        print(f"Loaded {len(df)} aircraft from {AIRCRAFT_FILE}\n")

    print("Tail to ICAO24 mapping:")
    for _, row in df[["tail_number", "icao24", "company_name"]].iterrows():
        print(f"  {row['tail_number']:8s} -> {row['icao24']}  "
              f"({row['company_name']})")

    days_total = (END_DATE - START_DATE).days
    chunks_per_aircraft = days_total // CHUNK_DAYS + 1
    total_calls = chunks_per_aircraft * len(df)
    print(f"\nWindow: {START_DATE.date()} to {END_DATE.date()} "
          f"({days_total} days)")
    print(f"Approx. {chunks_per_aircraft} chunks/aircraft, "
          f"{total_calls} API calls\n")

    client = OpenSkyClient(CLIENT_ID, CLIENT_SECRET)

    for _, row in df.iterrows():
        tail = row["tail_number"]
        icao = row["icao24"]
        company = row["company_name"]
        out = RAW_DIR / f"{tail}.csv"

        if out.exists():
            existing = pd.read_csv(out)
            print(f"\n{tail} ({company}) - SKIP (already have "
                  f"{len(existing)} flights)")
            continue

        print(f"\n{tail} ({company}) - ICAO {icao}")
        try:
            flights = fetch_flights_for_aircraft(
                client, icao, START_DATE, END_DATE)
        except QuotaExhausted:
            print(f"\nDaily quota exhausted. Try again after midnight UTC.")
            print(f"Run the script again tomorrow - it will resume from "
                  f"where it stopped.")
            return

        if not flights:
            print(f"  no flights returned for {tail}")
            pd.DataFrame().to_csv(out, index=False)
            continue

        fdf = pd.DataFrame(flights)
        fdf["tail_number"] = tail
        fdf["company_name"] = company
        fdf.to_csv(out, index=False)
        print(f"  -> wrote {out} ({len(fdf)} flights)")

    # Combine
    print("\nCombining per-aircraft files...")
    parts = []
    for csv in sorted(RAW_DIR.glob("*.csv")):
        try:
            d = pd.read_csv(csv)
            if len(d) > 0:
                parts.append(d)
        except pd.errors.EmptyDataError:
            pass
    if parts:
        combined = pd.concat(parts, ignore_index=True)
        combined.to_csv("flights_all.csv", index=False)
        print(f"Wrote flights_all.csv ({len(combined)} flights)")
    else:
        print("No flights collected yet.")


if __name__ == "__main__":
    main()