"""
Pull all 8-K filings for all 10 sample companies from SEC EDGAR.

Uses EDGAR's structured submissions API (free, no auth, fast).
Output: events_starter.csv with one row per 8-K filing in the window.

Columns pre-filled by this script:
    filing_date, company_name, ticker, cik, accession_number,
    item_codes, source_url

Columns left blank for manual classification:
    event_type, description, target_or_counterparty, target_location,
    include, skip_reason

Order in output: focal three first (Liberty Media, Newell Brands, Workday),
then the other seven, sorted by company then filing_date.

The SEC requires a real User-Agent string. Put your name and email below.
"""

import requests
import pandas as pd
import time
from pathlib import Path

# ---- CONFIG ----
USER_AGENT = "Stratum Class Project Owen Higinbotham owh227@lehigh.edu"

# Study window
WINDOW_START = "2024-10-01"
WINDOW_END = "2025-04-01"

# Companies in the order they should appear in the output:
# focal three first (Liberty Media, Newell Brands, Workday), then the other seven.
# CIKs verified from SEC EDGAR.
COMPANIES = [
    # Focal three
    {"name": "Liberty Media Corp",         "cik": "1560385",  "ticker": "FWONA"},
    {"name": "Newell Brands Inc",          "cik": "814453",   "ticker": "NWL"},
    {"name": "Workday Inc",                "cik": "1327811",  "ticker": "WDAY"},
    # Other seven (alphabetical by ticker for sanity)
    {"name": "CenterPoint Energy Inc",     "cik": "1130310",  "ticker": "CNP"},
    {"name": "Great Southern Bancorp Inc", "cik": "854560",   "ticker": "GSBC"},
    {"name": "Life Time Group Holdings",   "cik": "1869198",  "ticker": "LTH"},
    {"name": "Macy's Inc",                 "cik": "794367",   "ticker": "M"},
    {"name": "Murphy USA Inc",             "cik": "1573516",  "ticker": "MUSA"},
    {"name": "Nordstrom Inc",              "cik": "72333",    "ticker": "JWN"},
    {"name": "Skechers USA Inc",           "cik": "1065837",  "ticker": "SKX"},
]

# Final column order
OUTPUT_COLS = [
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
    "include",
    "skip_reason",
    "source_url",
]


def fetch_submissions(cik: str) -> dict:
    """Fetch the submissions JSON for one company."""
    cik_padded = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    return r.json()


def collect_8ks(company: dict, sort_index: int) -> pd.DataFrame:
    """Collect all 8-K filings for one company within the window.

    sort_index is used to preserve the requested company ordering in the
    final output (focal three first, then others).
    """
    print(f"\nFetching submissions for {company['name']} (CIK {company['cik']})...")
    try:
        data = fetch_submissions(company["cik"])
    except requests.HTTPError as e:
        print(f"  ERROR: HTTP {e.response.status_code} - skipping")
        return pd.DataFrame()
    except Exception as e:
        print(f"  ERROR: {e} - skipping")
        return pd.DataFrame()

    recent = data.get("filings", {}).get("recent", {})
    if not recent:
        print(f"  no recent filings found")
        return pd.DataFrame()

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

    # Filter to window
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

    # Add metadata
    df["company_name"] = company["name"]
    df["ticker"] = company["ticker"]
    df["cik"] = company["cik"]
    df["_company_sort"] = sort_index

    # Rename items
    df = df.rename(columns={"items": "item_codes"})

    print(f"  found {len(df)} 8-K filings in window")
    return df


def main():
    if "PASTE_" in USER_AGENT or "@" not in USER_AGENT:
        print("WARNING: USER_AGENT may need a real email. SEC requires it.")

    all_filings = []
    for sort_idx, company in enumerate(COMPANIES):
        df = collect_8ks(company, sort_idx)
        if len(df) > 0:
            all_filings.append(df)
        time.sleep(0.2)  # SEC fair use

    if not all_filings:
        print("\nNo filings collected for any company.")
        return

    combined = pd.concat(all_filings, ignore_index=True)

    # Add blank columns for manual classification
    for col in ["event_type", "description", "target_or_counterparty",
                "target_location", "include", "skip_reason"]:
        combined[col] = ""

    # Sort: company in requested order, then filing_date ascending within each
    combined = combined.sort_values(
        ["_company_sort", "filing_date"]
    ).reset_index(drop=True)
    combined = combined.drop(columns=["_company_sort", "form",
                                       "report_date", "primary_document"])

    # Final column order
    combined = combined[OUTPUT_COLS]

    out = Path("events_starter.csv")
    combined.to_csv(out, index=False)
    print(f"\n{'='*60}")
    print(f"Wrote {out} ({len(combined)} filings)")
    print(f"{'='*60}\n")

    print("Filings per company (in output order):")
    counts = combined.groupby("company_name", sort=False).size()
    for company, n in counts.items():
        print(f"  {company:35s}  {n:3d} filings")

    print(f"\nMost common item codes:")
    item_counts = {}
    for items in combined["item_codes"].dropna():
        for item in str(items).split(","):
            item = item.strip()
            if item:
                item_counts[item] = item_counts.get(item, 0) + 1
    for item, count in sorted(item_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {item}: {count}")

    print(f"\nFirst 5 rows of output:")
    print(combined.head().to_string())


if __name__ == "__main__":
    main()
