"""
Step 1a: Pull one month of flight data for a single company.

Configure the section below, then run once per month per OpenSky account.
Each run saves per-aircraft monthly CSVs to raw_flights/.
When all months are complete, run 01b_combine.py to merge into flights_all.csv.
"""

import time
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ================================================================
# CONFIG — update these for every run
# ================================================================
CLIENT_ID     = "  "
CLIENT_SECRET = "  "

COMPANY       = "Macy's"          # partial name match, case-insensitive

START_DATE    = datetime(2024,  10, 1, tzinfo=timezone.utc)
END_DATE      = datetime(2025,  4,  1, tzinfo=timezone.utc)
# ================================================================

CHUNK_DAYS    = 2
REQUEST_DELAY = 0.5
AIRCRAFT_FILE = Path("Final_Company_Aircraft.xlsx")
RAW_DIR       = Path("raw_flights")
RAW_DIR.mkdir(exist_ok=True)

MONTH_LABEL = START_DATE.strftime("%Y-%m")

TOKEN_URL = ("https://auth.opensky-network.org/auth/realms/opensky-network"
             "/protocol/openid-connect/token")
API_BASE  = "https://opensky-network.org/api"


class QuotaExhausted(Exception):
    pass


class OpenSkyClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token = None
        self._token_expires_at = 0
        self.last_remaining = None

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

    def get(self, path, params=None):
        self._ensure_token()
        r = requests.get(
            f"{API_BASE}{path}",
            params=params or {},
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=60,
        )
        remaining = r.headers.get("X-Rate-Limit-Remaining")
        if remaining is not None:
            try:
                self.last_remaining = int(remaining)
            except ValueError:
                pass
        return r


def fetch_flights(client, icao24, start, end):
    all_flights = []
    chunk_start = start
    total_chunks = 0
    chunks_with_flights = 0

    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=CHUNK_DAYS), end)
        params = {
            "icao24": icao24.lower(),
            "begin":  int(chunk_start.timestamp()),
            "end":    int(chunk_end.timestamp()),
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
                    print(f"    {chunk_start.date()}: {len(flights)} flights{rem}")
            elif r.status_code == 404:
                pass
            elif r.status_code == 429:
                retry_after = r.headers.get("X-Rate-Limit-Retry-After-Seconds", "unknown")
                print(f"\n  [QUOTA EXHAUSTED] HTTP 429")
                if retry_after != "unknown":
                    try:
                        print(f"  -> wait approximately {int(retry_after) / 3600:.1f} hours before retrying")
                    except ValueError:
                        pass
                raise QuotaExhausted()
            else:
                print(f"    {chunk_start.date()}: HTTP {r.status_code} - {r.text[:120]}")
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

    print(f"  summary: {total_chunks} chunks, {chunks_with_flights} with flights, "
          f"{len(all_flights)} total flights")
    return all_flights


def main():
    if CLIENT_ID.startswith("PASTE_") or CLIENT_SECRET.startswith("PASTE_"):
        print("ERROR: Set CLIENT_ID and CLIENT_SECRET in the CONFIG section above.")
        return

    df = pd.read_excel(AIRCRAFT_FILE)
    df["icao24"] = df["icao24"].astype(str).str.strip().str.upper()
    df = df[df["company_name"].str.contains(COMPANY, case=False, na=False)]

    if df.empty:
        print(f"ERROR: No aircraft found matching '{COMPANY}'")
        print("\nAvailable companies:")
        for name in pd.read_excel(AIRCRAFT_FILE)["company_name"].unique():
            print(f"  {name}")
        return

    print(f"Company:  {COMPANY}")
    print(f"Window:   {START_DATE.date()} to {END_DATE.date()}")
    print(f"Saving to: raw_flights/<tail>_{MONTH_LABEL}.csv\n")
    print("Aircraft matched:")
    for _, row in df[["tail_number", "icao24", "company_name"]].iterrows():
        print(f"  {row['tail_number']:8s} -> {row['icao24']}  ({row['company_name']})")

    days_total = (END_DATE - START_DATE).days
    chunks_per = days_total // CHUNK_DAYS + 1
    print(f"\n~{chunks_per} chunks/aircraft, ~{chunks_per * len(df)} total API calls\n")

    client = OpenSkyClient(CLIENT_ID, CLIENT_SECRET)

    for _, row in df.iterrows():
        tail    = row["tail_number"]
        icao    = row["icao24"]
        company = row["company_name"]
        out     = RAW_DIR / f"{tail}_{MONTH_LABEL}.csv"

        if out.exists():
            try:
                existing = pd.read_csv(out)
                print(f"{tail} [{MONTH_LABEL}] - SKIP (already have {len(existing)} flights)")
                continue
            except pd.errors.EmptyDataError:
                print(f"{tail} [{MONTH_LABEL}] - empty file found, re-running")
                out.unlink()

        print(f"\n{tail} ({company}) [{MONTH_LABEL}] - ICAO {icao}")
        try:
            flights = fetch_flights(client, icao, START_DATE, END_DATE)
        except QuotaExhausted:
            print(f"\nQuota exhausted. Re-run tomorrow — already-saved months will be skipped.")
            return

        fdf = pd.DataFrame(flights) if flights else pd.DataFrame()
        if not fdf.empty:
            fdf["tail_number"]  = tail
            fdf["company_name"] = company
        fdf.to_csv(out, index=False)

        if flights:
            print(f"  -> saved {out} ({len(fdf)} flights)")
        else:
            print(f"  no flights found — saved empty file so this month is skipped next run")

    print("\nAll done. Run 01b_combine.py when all months are complete.")


if __name__ == "__main__":
    main()
