"""
Step 1b: Combine monthly CSVs from raw_flights/ into per-firm files.

Run this after all monthly 01a pulls are complete.

For each tail number, merges all monthly files (e.g. N780LM_2024-11.csv,
N780LM_2024-12.csv) into one file (e.g. N780LM.csv) in raw_flights/.
Also writes flights_all.csv combining all firms for 02_enrich_flights.py.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("raw_flights")


def main():
    # Grab monthly files from raw_flights/ and any subfolders
    monthly_csvs = sorted(RAW_DIR.rglob("*_????-??.csv"))
    if not monthly_csvs:
        print("No monthly CSV files found in raw_flights/")
        return

    # Group by tail number (everything before the _YYYY-MM suffix)
    by_tail = {}
    for csv in monthly_csvs:
        tail = csv.stem.rsplit("_", 1)[0]
        by_tail.setdefault(tail, []).append(csv)

    print(f"Found {len(monthly_csvs)} monthly files across {len(by_tail)} aircraft:\n")

    all_parts = []

    for tail, files in sorted(by_tail.items()):
        parts = []
        for f in sorted(files):
            try:
                df = pd.read_csv(f)
                if len(df) > 0:
                    parts.append(df)
                    print(f"  {f.name}: {len(df)} flights")
                else:
                    print(f"  {f.name}: empty — skipped")
            except pd.errors.EmptyDataError:
                print(f"  {f.name}: empty — skipped")

        if not parts:
            print(f"  -> {tail}: no flights across any month, skipping\n")
            continue

        firm_df = pd.concat(parts, ignore_index=True)

        before = len(firm_df)
        firm_df = firm_df.drop_duplicates(subset=["icao24", "firstSeen"])
        dupes = before - len(firm_df)

        out = Path(f"{tail}.csv")
        firm_df.to_csv(out, index=False)

        msg = f"  -> wrote {out} ({len(firm_df)} flights)"
        if dupes:
            msg += f", removed {dupes} duplicates"
        print(msg + "\n")

        all_parts.append(firm_df)

    if not all_parts:
        print("No flight data found across any firm. Nothing to combine.")
        return

    combined = pd.concat(all_parts, ignore_index=True)
    combined.to_csv("flights_all.csv", index=False)
    print(f"Wrote flights_all.csv ({len(combined)} total flights) — ready for 02_enrich_flights.py")

    print("\nFlights per company:")
    print(combined.groupby("company_name").size().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
