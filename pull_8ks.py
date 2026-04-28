"""
Pull all 8-K filings for the 3 focal companies from SEC EDGAR.

Uses EDGAR's structured submissions API (free, no auth, fast).
Output: events_starter.csv with one row per 8-K filing in the window.

You then fill in: event_type, description, target_or_counterparty, target_location

The SEC requires a real User-Agent string. Put your name and email below.
"""

import requests
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

# ---- CONFIG ----
USER_AGENT = "Stratum Class Project Owen Higinbotham owh227@lehigh.edu"

# Study window
WINDOW_START = "2023-04-01"
WINDOW_END = "2025-04-01"

# 3 focal companies
COMPANIES = [
    {"name": "Liberty Media Corp", "cik": "1560385", "ticker": "FWONA"},
    {"name": "Workday Inc", "cik": "1327811", "ticker": "WDAY"},
    {"name": "CenterPoint Energy Inc", "cik": "1130310", "ticker": "CNP"},
]


def fetch_submissions(cik: str) -> dict:
    """Fetch the submissions JSON for one company."""
    cik_padded = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_8k_items(cik: str, accession: str) -> str:
    """
    Fetch the index page for a specific 8-K filing and extract item codes.
    The submissions JSON doesn't include item codes directly; they're on
    the filing's index page.
    """
    cik_int = str(int(cik))  # remove leading zeros
    accession_clean = accession.replace("-", "")
    url = (f"https://www.sec.gov/cgi-bin/browse-edgar?"
           f"action=getcompany&CIK={cik_int}"
           f"&type=8-K&dateb=&owner=include&count=40&action=getcompany")
    # Actually easier: items are in the "items" field of submissions JSON
    # for recent filings. We'll get them from there.
    return ""


def collect_8ks(company: dict) -> pd.DataFrame:
    """Collect all 8-K filings for one company within the window."""
    print(f"\nFetching submissions for {company['name']} (CIK {company['cik']})...")
    data = fetch_submissions(company["cik"])

    recent = data.get("filings", {}).get("recent", {})
    if not recent:
        print(f"  no recent filings found")
        return pd.DataFrame()

    # Build a dataframe from the parallel arrays in 'recent'
    df = pd.DataFrame({
        "form": recent.get("form", []),
        "filing_date": recent.get("filingDate", []),
        "report_date": recent.get("reportDate", []),
        "accession_number": recent.get("accessionNumber", []),
        "primary_document": recent.get("primaryDocument", []),
        "items": recent.get("items", []),
    })

    # Filter to 8-K only
    df = df[df["form"] == "8-K"].copy()

    # Filter to our window
    df = df[(df["filing_date"] >= WINDOW_START) &
            (df["filing_date"] < WINDOW_END)].copy()

    if len(df) == 0:
        print(f"  no 8-Ks in window {WINDOW_START} to {WINDOW_END}")
        return pd.DataFrame()

    # Build the source URL for each filing
    cik_int = str(int(company["cik"]))
    df["source_url"] = df.apply(
        lambda r: (f"https://www.sec.gov/Archives/edgar/data/{cik_int}/"
                   f"{r['accession_number'].replace('-', '')}/"
                   f"{r['primary_document']}"),
        axis=1
    )

    # Add company info
    df["company_name"] = company["name"]
    df["ticker"] = company["ticker"]
    df["cik"] = company["cik"]

    # Rename items column for clarity
    df = df.rename(columns={"items": "item_codes"})

    print(f"  found {len(df)} 8-K filings in window")
    return df


def main():
    if "owh227@lehigh.edu" not in USER_AGENT:
        print("WARNING: USER_AGENT may need your real email. SEC requires it.")

    all_filings = []
    for company in COMPANIES:
        df = collect_8ks(company)
        if len(df) > 0:
            all_filings.append(df)
        time.sleep(0.2)  # SEC fair use

    if not all_filings:
        print("No filings collected.")
        return

    combined = pd.concat(all_filings, ignore_index=True)

    # Add the columns YOU need to fill in (blank for now)
    combined["event_type"] = ""
    combined["description"] = ""
    combined["target_or_counterparty"] = ""
    combined["target_location"] = ""

    # Final column order
    output_cols = [
        "filing_date",
        "company_name",
        "ticker",
        "cik",
        "accession_number",
        "item_codes",
        "event_type",
        "description",
        "target_or_counterparty",
        "target_location",
        "source_url",
    ]
    combined = combined[output_cols]
    combined = combined.sort_values(["company_name", "filing_date"]).reset_index(drop=True)

    out = Path("events_starter.csv")
    combined.to_csv(out, index=False)
    print(f"\nWrote {out} ({len(combined)} filings)")

    print(f"\nSummary by company:")
    print(combined.groupby("company_name").size())

    print(f"\nMost common item codes:")
    item_counts = {}
    for items in combined["item_codes"].dropna():
        for item in str(items).split(","):
            item = item.strip()
            if item:
                item_counts[item] = item_counts.get(item, 0) + 1
    for item, count in sorted(item_counts.items(), key=lambda x: -x[1]):
        print(f"  {item}: {count}")

    print(f"\nFirst 5 rows:")
    print(combined.head().to_string())


if __name__ == "__main__":
    main()