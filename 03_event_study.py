"""
Step 4: Stock price collection + event study analysis.

This script:
  1. Pulls daily closing prices for the 3 focal firms + S&P 500 from yfinance
  2. Computes daily returns
  3. For each event in events.csv (where include == 'Y'):
     - Estimates a market model over [-250, -30] trading days
     - Computes abnormal returns over [-1, +1]
     - Computes CAR = sum of ARs in event window
  4. Builds flight-activity features in [-30, 0] window
  5. Joins everything into one analysis-ready table

Output:
  prices.csv                 daily prices and returns for all firms + market
  event_study_results.csv    one row per event with CAR + flight features

Usage:
  python 03_event_study.py

This script is also imported by analysis.py for the Streamlit dashboard.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta

# ---- CONFIG ----
# Map company names to tickers (must match what's in events.csv)
TICKER_MAP = {
    "Newell Brands Inc":          "NWL",
    "Macy's Inc":                 "M",
    "CenterPoint Energy Inc":     "CNP",
    "Great Southern Bancorp Inc": "GSBC",
    "Murphy USA Inc":             "MUSA",
    "Workday Inc":                "WDAY",
}
# Excluded: JWN (Nordstrom went private March 2025, Yahoo Finance purged history)
#           SKX (Skechers — yfinance returning 404, unresolvable data issue)

# Pull a wide window so we have estimation-window data for every event
PRICE_START = "2023-09-01"
PRICE_END = "2025-04-15"

MARKET_TICKER = "^GSPC"

# Event-study windows (in trading days)
EST_WINDOW_START = -250
EST_WINDOW_END = -30
EVENT_WINDOW_START = -1
EVENT_WINDOW_END = 1

# Pre-event flight window (in calendar days)
FLIGHT_WINDOW_30D = 30
FLIGHT_WINDOW_7D = 7


def pull_prices() -> pd.DataFrame:
    """Pull daily closing prices for all focal firms + market."""
    tickers = list(TICKER_MAP.values()) + [MARKET_TICKER]
    print(f"Pulling prices for {tickers} from {PRICE_START} to {PRICE_END}...")
    data = yf.download(tickers, start=PRICE_START, end=PRICE_END,
                       auto_adjust=False, progress=False)
    # yfinance returns multi-index columns (field, ticker); we want adjusted close
    prices = data["Adj Close"].copy()
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    print(f"  pulled {len(prices)} trading days x {len(prices.columns)} tickers")
    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute daily simple returns."""
    return prices.pct_change().dropna(how="all")


def market_model_car(returns: pd.DataFrame, ticker: str, event_date: pd.Timestamp,
                     market_ticker: str = MARKET_TICKER) -> dict:
    """
    Estimate market model on [-250, -30] and compute CAR over [-1, +1].

    Returns dict with: alpha, beta, ar_minus1, ar_0, ar_plus1, car_3day,
                       n_estimation_days, valid (bool).
    """
    if ticker not in returns.columns or market_ticker not in returns.columns:
        return {"valid": False, "reason": f"ticker {ticker} not in price data"}

    # Get position of event date in returns index
    # Use nearest trading day on or after event_date
    valid_dates = returns.index[returns.index >= event_date]
    if len(valid_dates) == 0:
        return {"valid": False, "reason": "event date after data range"}

    event_trading_date = valid_dates[0]
    event_idx = returns.index.get_loc(event_trading_date)

    # Estimation window indices
    est_start_idx = event_idx + EST_WINDOW_START
    est_end_idx = event_idx + EST_WINDOW_END
    if est_start_idx < 0:
        return {"valid": False,
                "reason": f"insufficient pre-event data ({est_start_idx})"}

    # Slice estimation and event windows
    est_returns = returns.iloc[est_start_idx:est_end_idx]
    event_returns = returns.iloc[
        event_idx + EVENT_WINDOW_START : event_idx + EVENT_WINDOW_END + 1
    ]

    firm_est = est_returns[ticker].dropna()
    mkt_est = est_returns[market_ticker].dropna()
    common = firm_est.index.intersection(mkt_est.index)
    firm_est = firm_est.loc[common]
    mkt_est = mkt_est.loc[common]

    if len(firm_est) < 30:
        return {"valid": False,
                "reason": f"only {len(firm_est)} estimation days available"}

    # OLS: firm_return = alpha + beta * market_return
    cov = np.cov(firm_est.values, mkt_est.values, ddof=1)
    beta = cov[0, 1] / cov[1, 1]
    alpha = firm_est.mean() - beta * mkt_est.mean()

    # Abnormal returns in event window
    firm_event = event_returns[ticker]
    mkt_event = event_returns[market_ticker]
    expected = alpha + beta * mkt_event
    ar = firm_event - expected

    return {
        "valid": True,
        "event_trading_date": event_trading_date,
        "alpha": alpha,
        "beta": beta,
        "n_estimation_days": len(firm_est),
        "ar_minus1": ar.iloc[0] if len(ar) >= 1 else np.nan,
        "ar_0": ar.iloc[1] if len(ar) >= 2 else np.nan,
        "ar_plus1": ar.iloc[2] if len(ar) >= 3 else np.nan,
        "car_3day": ar.sum(),
    }


def build_flight_features(flights: pd.DataFrame, company: str,
                          event_date: pd.Timestamp,
                          target_location: str = "") -> dict:
    """
    Build pre-event flight features in the [-30, 0] window.

    flights expected columns: tail_number, company_name, flight_date,
                              arr_city, arr_lat, arr_lon
    """
    if flights is None or len(flights) == 0:
        return {f: np.nan for f in [
            "flight_count_30d", "flight_count_7d", "unique_destinations_30d",
            "flights_to_target_region", "flight_count_above_baseline"
        ]}

    def _norm(s):
        import re
        return re.sub(r"[^A-Z0-9 ]", "", str(s).upper()).strip()
    target_norm = _norm(company)
    fdf = flights[flights["company_name"].apply(_norm) == target_norm].copy()
    fdf["flight_date"] = pd.to_datetime(fdf["flight_date"])

    # Window slices
    window_30 = fdf[
        (fdf["flight_date"] >= event_date - timedelta(days=FLIGHT_WINDOW_30D)) &
        (fdf["flight_date"] < event_date)
    ]
    window_7 = fdf[
        (fdf["flight_date"] >= event_date - timedelta(days=FLIGHT_WINDOW_7D)) &
        (fdf["flight_date"] < event_date)
    ]

    flight_count_30d = len(window_30)
    flight_count_7d = len(window_7)
    unique_destinations_30d = window_30["arr_city"].nunique() if len(window_30) else 0

    # Target region match (string match on city — simple but works for vignettes)
    flights_to_target_region = 0
    if target_location and isinstance(target_location, str) and len(window_30):
        target_city = target_location.split(",")[0].strip().lower()
        if target_city:
            matches = window_30["arr_city"].str.lower().str.contains(
                target_city, na=False)
            flights_to_target_region = int(matches.any())

    # Baseline: average 30-day flight count across the firm's full series
    baseline = len(fdf) / max(1, (fdf["flight_date"].max() -
                                  fdf["flight_date"].min()).days) * 30 \
        if len(fdf) > 1 else 0
    flight_count_above_baseline = flight_count_30d - baseline

    return {
        "flight_count_30d": flight_count_30d,
        "flight_count_7d": flight_count_7d,
        "unique_destinations_30d": unique_destinations_30d,
        "flights_to_target_region": flights_to_target_region,
        "flight_count_above_baseline": flight_count_above_baseline,
    }


def main():
    # Load events
    events_path = Path("events.csv")
    if not events_path.exists():
        print(f"ERROR: {events_path} not found. Run pull_8ks.py and finish "
              f"manual classification first.")
        return

    events = pd.read_csv(events_path)
    if "include" in events.columns:
        events = events[events["include"] == "Y"].copy()
    print(f"Loaded {len(events)} retained events from {events_path}")

    events["filing_date"] = pd.to_datetime(events["filing_date"], dayfirst=False)

    # Load all cleaned flight CSVs automatically
    clean_dir = Path("raw_flights/Clean Data")
    parts = [pd.read_csv(f) for f in sorted(clean_dir.glob("*_cleaned.csv"))
             if f.stat().st_size > 0] if clean_dir.exists() else []
    flights = pd.concat(parts, ignore_index=True) if parts else None
    if flights is not None:
        print(f"Loaded {len(flights)} flights across {flights['company_name'].nunique()} firms")
    else:
        print("WARNING: No cleaned flight files found. Flight features will be NaN.")

    # Pull prices and compute returns
    prices = pull_prices()
    prices.to_csv("prices.csv")
    returns = compute_returns(prices)
    print(f"Computed daily returns: {returns.shape}")

    # Run event study for each event
    results = []
    for _, row in events.iterrows():
        company = row["company_name"]
        ticker = TICKER_MAP.get(company)
        if ticker is None:
            print(f"  skip: no ticker mapping for {company}")
            continue

        car_result = market_model_car(returns, ticker, row["filing_date"])
        flight_features = build_flight_features(
            flights, company, row["filing_date"],
            row.get("target_location", "")
        )

        result = {
            "filing_date": row["filing_date"],
            "company_name": company,
            "ticker": ticker,
            "event_type": row.get("event_type", ""),
            "description": row.get("description", ""),
            "target_location": row.get("target_location", ""),
            **car_result,
            **flight_features,
        }
        results.append(result)

    out = pd.DataFrame(results)
    out.to_csv("event_study_results.csv", index=False)
    print(f"\nWrote event_study_results.csv ({len(out)} rows)")

    # Summary
    valid = out[out["valid"] == True].copy() if "valid" in out.columns else out
    if len(valid) > 0:
        print(f"\n{'='*60}")
        print(f"Event Study Summary")
        print(f"{'='*60}")
        print(f"\nValid events: {len(valid)}")
        print(f"\nMean CAR[-1,+1] by event type:")
        for et, sub in valid.groupby("event_type"):
            if len(sub) >= 2:
                mean_car = sub["car_3day"].mean()
                std_car = sub["car_3day"].std()
                t_stat = mean_car / (std_car / np.sqrt(len(sub))) if std_car > 0 else np.nan
                print(f"  {et:25s}  N={len(sub):3d}  "
                      f"mean={mean_car:+.4f}  t={t_stat:+.2f}")

        if flights is not None:
            print(f"\nFlight feature summary (where available):")
            for col in ["flight_count_30d", "flight_count_7d",
                        "flights_to_target_region"]:
                if col in valid.columns:
                    print(f"  {col:30s}  mean={valid[col].mean():.2f}  "
                          f"max={valid[col].max():.0f}")


if __name__ == "__main__":
    main()
