"""
Step 4: Regression analysis and dashboard data preparation.

Run after 03_event_study.py. Reads event_study_results.csv, prices.csv,
and per-firm cleaned flight CSVs, then writes dashboard-ready CSVs to
dashboard/ for analysis.py (Streamlit).

Outputs (all in dashboard/):
  regression_results.csv   OLS coefficients across 3 model specs
  binned_summary.csv       mean CAR by pre-event flight count
  flight_map_data.csv      pre-event flights with lat/lon + event CAR
  firm_profiles.csv        per-firm summary statistics
  flight_timeline.csv      daily flight counts + returns around events
  signal_summary.csv       above-baseline hit-rate analysis
  hub_analysis.csv         financial hub flights vs CAR
  dark_period.csv          zero-flight events and their outcomes
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from datetime import timedelta
from pathlib import Path

DASHBOARD_DIR = Path("dashboard")
DASHBOARD_DIR.mkdir(exist_ok=True)

CLEANED_DIR = Path("raw_flights/Clean Data")

# Update when adding firms — must match company_name in cleaned CSVs
TICKER_MAP = {
    "Newell Brands Inc":          "NWL",
    "Macy's Inc":                 "M",
    "CenterPoint Energy Inc":     "CNP",
    "Great Southern Bancorp Inc": "GSBC",
    "Murphy USA Inc":             "MUSA",
    "Workday Inc":                "WDAY",
}

FINANCIAL_HUBS = {
    "new york", "manhattan", "newark", "chicago", "london",
    "san francisco", "los angeles", "boston", "washington",
    "houston", "dallas", "atlanta", "charlotte", "philadelphia",
    "seattle", "miami", "denver", "minneapolis",
}

# Maps raw FAA/OpenSky company names to the canonical names used in events.csv
FLIGHT_NAME_MAP = {
    "NEWELL BRANDS INC.":           "Newell Brands Inc",
    "Macy's, Inc.":                 "Macy's Inc",
    "CENTERPOINT ENERGY INC":       "CenterPoint Energy Inc",
    "GREAT SOUTHERN BANCORP, INC.": "Great Southern Bancorp Inc",
    "Murphy USA Inc.":              "Murphy USA Inc",
    "Workday, Inc.":                "Workday Inc",
}


def load_flights():
    parts = [pd.read_csv(f) for f in sorted(CLEANED_DIR.glob("*_cleaned.csv"))
             if pd.read_csv(f, nrows=1).shape[0] > 0]
    if not parts:
        return pd.DataFrame()
    flights = pd.concat(parts, ignore_index=True)
    flights["flight_date"] = pd.to_datetime(flights["flight_date"])
    flights["company_name"] = flights["company_name"].map(
        lambda x: FLIGHT_NAME_MAP.get(x, x)
    )
    return flights


def run_regressions(events):
    df = events.dropna(subset=["car_3day", "flight_count_30d"]).copy()
    if len(df) < 5:
        print("  WARNING: too few events for regression")
        return pd.DataFrame()

    # Create dummies before building specs (cast to float for statsmodels compatibility)
    if "event_type" in df.columns and df["event_type"].nunique() > 1:
        dummies = pd.get_dummies(df["event_type"], prefix="et", drop_first=True).astype(float)
        df = pd.concat([df, dummies], axis=1)
    if "company_name" in df.columns and df["company_name"].nunique() > 1:
        dummies = pd.get_dummies(df["company_name"], prefix="firm", drop_first=True).astype(float)
        df = pd.concat([df, dummies], axis=1)

    et_cols   = [c for c in df.columns if c.startswith("et_")]
    firm_cols = [c for c in df.columns if c.startswith("firm_")]

    specs = [
        ("Model 1", ["flight_count_30d"]),
        ("Model 2", ["flight_count_30d", "flight_count_7d"]),
        ("Model 3", ["flight_count_30d", "flight_count_7d"] + et_cols + firm_cols),
    ]

    y = df["car_3day"]
    rows = []
    for model_name, xvars in specs:
        avail = [v for v in xvars if v in df.columns]
        if not avail:
            continue
        X = sm.add_constant(df[avail].fillna(0))
        try:
            res = sm.OLS(y, X).fit(cov_type="HC3")
            for var in avail:
                rows.append({
                    "variable":  var,
                    "model":     model_name,
                    "coef":      res.params.get(var, np.nan),
                    "tstat":     res.tvalues.get(var, np.nan),
                    "pval":      res.pvalues.get(var, np.nan),
                    "r_squared": res.rsquared,
                    "n":         int(res.nobs),
                })
        except Exception as e:
            print(f"  {model_name} failed: {e}")

    return pd.DataFrame(rows)


def build_binned_summary(events):
    df = events.dropna(subset=["car_3day", "flight_count_30d"]).copy()
    df["flight_bin"] = df["flight_count_30d"].clip(upper=5).astype(int)
    df["positive_car"] = (df["car_3day"] > 0).astype(int)

    rows = []
    all_types = ["All"] + list(df["event_type"].dropna().unique())
    for event_type in all_types:
        subset = df if event_type == "All" else df[df["event_type"] == event_type]
        for b, grp in subset.groupby("flight_bin"):
            rows.append({
                "flight_bin":   f"{b}+" if b == 5 else str(b),
                "event_type":   event_type,
                "n_events":     len(grp),
                "mean_car":     grp["car_3day"].mean(),
                "median_car":   grp["car_3day"].median(),
                "pct_positive": grp["positive_car"].mean() * 100,
            })
    return pd.DataFrame(rows)


def build_flight_map_data(events, flights):
    if flights.empty:
        return pd.DataFrame()
    rows = []
    for _, ev in events.dropna(subset=["car_3day"]).iterrows():
        company    = ev["company_name"]
        event_date = pd.to_datetime(ev["filing_date"])
        pre = flights[
            (flights["company_name"] == company) &
            (flights["flight_date"] >= event_date - timedelta(days=30)) &
            (flights["flight_date"] < event_date)
        ]
        for _, f in pre.iterrows():
            rows.append({
                "company_name": company,
                "event_date":   event_date.date(),
                "event_type":   ev.get("event_type", ""),
                "car_3day":     ev["car_3day"],
                "flight_date":  f["flight_date"].date(),
                "days_before":  (event_date - f["flight_date"]).days,
                "dep_city":     f.get("dep_city", ""),
                "dep_lat":      f.get("dep_lat"),
                "dep_lon":      f.get("dep_lon"),
                "arr_city":     f.get("arr_city", ""),
                "arr_lat":      f.get("arr_lat"),
                "arr_lon":      f.get("arr_lon"),
            })
    return pd.DataFrame(rows)


def build_firm_profiles(events, flights):
    rows = []
    for company, grp in events.groupby("company_name"):
        valid = grp.dropna(subset=["car_3day"])
        fm    = valid["flight_count_30d"].mean()
        fs    = valid["flight_count_30d"].std() if len(valid) > 1 else np.nan
        rows.append({
            "company_name":       company,
            "ticker":             TICKER_MAP.get(company, ""),
            "n_events":           len(valid),
            "mean_car":           valid["car_3day"].mean(),
            "pct_positive_car":   (valid["car_3day"] > 0).mean() * 100,
            "avg_flights_30d":    fm,
            "avg_flights_7d":     valid["flight_count_7d"].mean(),
            "consistency_score":  round(1 - fs / fm, 2) if fm and fm > 0 else np.nan,
            "pct_above_baseline": (valid["flight_count_above_baseline"] > 0).mean() * 100
                                  if "flight_count_above_baseline" in valid.columns else np.nan,
        })
    return pd.DataFrame(rows)


def build_flight_timeline(events, flights, prices):
    if flights.empty:
        return pd.DataFrame()
    rows = []
    for _, ev in events.dropna(subset=["car_3day"]).iterrows():
        company    = ev["company_name"]
        ticker     = TICKER_MAP.get(company, "")
        event_date = pd.to_datetime(ev["filing_date"])
        event_key  = f"{company} | {event_date.date()} | {ev.get('event_type','')}"

        for days_before in range(30, -2, -1):
            day = event_date - timedelta(days=days_before)
            n_flights = len(flights[
                (flights["company_name"] == company) &
                (flights["flight_date"].dt.date == day.date())
            ])
            stock_return = np.nan
            if ticker and prices is not None and ticker in prices.columns:
                ts = pd.Timestamp(day.date())
                if ts in prices.index:
                    stock_return = prices.loc[ts, ticker]

            rows.append({
                "event_key":       event_key,
                "company_name":    company,
                "event_type":      ev.get("event_type", ""),
                "filing_date":     event_date.date(),
                "car_3day":        ev["car_3day"],
                "days_before":     days_before,
                "date":            day.date(),
                "flight_count":    n_flights,
                "stock_return":    stock_return,
            })
    return pd.DataFrame(rows)


def build_signal_summary(events):
    df = events.dropna(subset=["car_3day", "flight_count_above_baseline"]).copy()
    df["above_baseline"] = df["flight_count_above_baseline"] > 0
    df["positive_car"]   = df["car_3day"] > 0

    rows = []
    for et in ["All"] + list(df["event_type"].dropna().unique()):
        sub   = df if et == "All" else df[df["event_type"] == et]
        above = sub[sub["above_baseline"]]
        below = sub[~sub["above_baseline"]]
        rows.append({
            "event_type":              et,
            "n_above_baseline":        len(above),
            "pct_positive_when_above": above["positive_car"].mean() * 100 if len(above) else np.nan,
            "n_below_baseline":        len(below),
            "pct_positive_when_below": below["positive_car"].mean() * 100 if len(below) else np.nan,
            "hit_rate_lift_pp":        (above["positive_car"].mean() -
                                        below["positive_car"].mean()) * 100
                                       if len(above) and len(below) else np.nan,
        })
    return pd.DataFrame(rows)


def build_hub_analysis(events, flights):
    if flights.empty:
        return pd.DataFrame()
    rows = []
    for _, ev in events.dropna(subset=["car_3day"]).iterrows():
        company    = ev["company_name"]
        event_date = pd.to_datetime(ev["filing_date"])
        pre = flights[
            (flights["company_name"] == company) &
            (flights["flight_date"] >= event_date - timedelta(days=30)) &
            (flights["flight_date"] < event_date)
        ]
        hub_flights = pre[pre["arr_city"].str.lower().isin(FINANCIAL_HUBS)] if len(pre) else pre
        rows.append({
            "company_name":   company,
            "event_type":     ev.get("event_type", ""),
            "filing_date":    ev["filing_date"],
            "car_3day":       ev["car_3day"],
            "total_flights":  len(pre),
            "hub_flights":    len(hub_flights),
            "pct_hub":        len(hub_flights) / len(pre) * 100 if len(pre) else 0,
            "flew_to_hub":    int(len(hub_flights) > 0),
        })
    return pd.DataFrame(rows)


def build_dark_period(events):
    df = events.dropna(subset=["car_3day", "flight_count_30d"]).copy()
    df["is_dark"]     = df["flight_count_30d"] == 0
    df["positive_car"] = df["car_3day"] > 0

    rows = []
    for label, mask in [("Dark (0 flights)", df["is_dark"]),
                         ("Active (1+ flights)", ~df["is_dark"])]:
        sub = df[mask]
        rows.append({
            "period_type":     label,
            "n_events":        len(sub),
            "mean_car":        sub["car_3day"].mean() if len(sub) else np.nan,
            "pct_negative_car": (sub["car_3day"] < 0).mean() * 100 if len(sub) else np.nan,
        })
    return pd.DataFrame(rows)


def main():
    print("Loading data...")
    if not Path("event_study_results.csv").exists():
        print("ERROR: event_study_results.csv not found. Run 03_event_study.py first.")
        return

    events = pd.read_csv("event_study_results.csv")
    if "valid" in events.columns:
        events = events[events["valid"] == True].copy()
    events["filing_date"] = pd.to_datetime(events["filing_date"])
    print(f"  {len(events)} valid events")

    flights = load_flights()
    print(f"  {len(flights)} flights" if not flights.empty else "  No flight data found")

    prices = None
    if Path("prices.csv").exists():
        prices = pd.read_csv("prices.csv", index_col=0, parse_dates=True).pct_change()
        print(f"  prices loaded: {prices.shape}")

    outputs = {
        "regression_results.csv": lambda: run_regressions(events),
        "binned_summary.csv":     lambda: build_binned_summary(events),
        "flight_map_data.csv":    lambda: build_flight_map_data(events, flights),
        "firm_profiles.csv":      lambda: build_firm_profiles(events, flights),
        "flight_timeline.csv":    lambda: build_flight_timeline(events, flights, prices),
        "signal_summary.csv":     lambda: build_signal_summary(events),
        "hub_analysis.csv":       lambda: build_hub_analysis(events, flights),
        "dark_period.csv":        lambda: build_dark_period(events),
    }

    print()
    for fname, fn in outputs.items():
        print(f"Building {fname}...")
        df = fn()
        df.to_csv(DASHBOARD_DIR / fname, index=False)
        print(f"  -> {len(df)} rows")

    print(f"\nAll outputs written to {DASHBOARD_DIR}/")
    print("Run:  streamlit run analysis.py")


if __name__ == "__main__":
    main()
