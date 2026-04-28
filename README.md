# Stratum Aviation Event Study

**FIN 377: Data Science for Finance — Lehigh University**

Owen Higinbotham, Harry Keen, Ford Campbell — Advised by Prof. Donald Bowen

---

## What this project is

We test whether pre-announcement flight activity of corporate aircraft predicts the magnitude of stock price reactions to material corporate events. The design combines the Yermack (2014) "Tailspotting" flight-tracking framework with a standard market-model event study: we use flight features in the [-30, 0] window before each 8-K filing as predictors of cumulative abnormal returns over the [-1, +1] event window.

This is a replication and adaptation of Yermack (2014) and Bushee, Gerakos & Lee (2018), with a methodological pivot to mid-cap firms whose aircraft remain verifiable through public records (mega-cap CEO aircraft are increasingly shielded under 49 U.S.C. § 44114 and the 2024 FAA Reauthorization Act).

## Sample

10 verified U.S. corporate aircraft, mid-cap firms, all confirmed through FAA Aircraft Registry + SEC DEF 14A + OpenSky operator metadata cross-check. See `Final_Company_Aircraft.xlsx` for the full table.

3 focal firms for cross-sectional analysis: **Liberty Media (FWONA)**, **Workday (WDAY)**, **CenterPoint Energy (CNP)** — chosen for sector diversity and non-trivial 8-K activity in the window.

**Study window**: October 1, 2024 – April 1, 2025 (6 months).

## Pipeline

The project runs as four scripts producing CSVs that feed into one analysis script and one Streamlit dashboard:

```
Final_Company_Aircraft.xlsx
        |
        v
01_pull_flights.py        ──>  raw_flights/<TAIL>.csv
                                       |
                                       v
                          02_enrich_flights.py
                                       |
                                       v
                          flights_enriched.csv  ──┐
                                                  |
pull_8ks.py  ──>  events_starter.csv              |
                  (manual classification)         |
                          |                       |
                          v                       |
                  events.csv ────────────────────>┤
                                                  |
                                                  v
                                       03_event_study.py
                                       (yfinance + market model)
                                                  |
                                                  v
                                  event_study_results.csv
                                                  |
                                                  v
                                          dashboard.py
                                          (Streamlit)
```

## Files

### Inputs
- `Final_Company_Aircraft.xlsx` — verified sample of 10 aircraft with FAA registry chain of evidence

### Scripts
- `01_pull_flights.py` — pulls flight data from OpenSky REST API (OAuth2). Uses 2-day chunks, hard-stops on rate limit (HTTP 429), supports resume.
- `02_enrich_flights.py` — joins raw flights with airport metadata from OurAirports.com. Produces one row per flight with departure/arrival airport names, cities, lat/lon.
- `pull_8ks.py` — pulls all 8-K filings for the 3 focal firms from EDGAR submissions API. Outputs a starter CSV with filing date, item codes, and source URLs.
- `03_event_study.py` — pulls daily stock prices via yfinance for the 3 focal firms + S&P 500. Estimates market model on [-250, -30] window for each event, computes CAR over [-1, +1]. Builds flight-activity features in the [-30, 0] window. Joins everything into one row per event.
- `dashboard.py` — Streamlit dashboard (built by team).

### Outputs (gitignored — generated locally)
- `raw_flights/<TAIL>.csv` — per-aircraft raw OpenSky data
- `flights_enriched.csv` — combined flights with airport details
- `events_starter.csv` — auto-generated 8-K list, columns blank for manual review
- `events.csv` — manually classified events (the one that actually feeds analysis)
- `prices.csv` — daily prices for focal firms + market
- `event_study_results.csv` — one row per event with CAR + flight features (analysis-ready)
- `airports.csv` — cached OurAirports database

### Documentation
- `paper_draft.md` — the writeup
- `README.md` — this file

## Setup

```bash
# Clone the repo
git clone https://github.com/owenhigin/stratum-aviation-project.git
cd stratum-aviation-project

# Virtual environment + dependencies
python -m venv .venv
source .venv/bin/activate          # mac/linux
# or .venv\Scripts\activate        # windows

pip install pandas requests openpyxl pyarrow yfinance numpy streamlit python-dotenv

# Get OpenSky credentials (DM Owen for the team's pooled set)
# Create .env in project root:
#   OPENSKY_CLIENT_ID=...
#   OPENSKY_CLIENT_SECRET=...
```

## How to run the pipeline (in order)

```bash
# 1. Pull flight data (~30 minutes if quota allows)
python 01_pull_flights.py

# 2. Enrich with airport details (~30 seconds)
python 02_enrich_flights.py

# 3. Pull list of 8-Ks (~5 seconds)
python pull_8ks.py
# Then manually classify events_starter.csv -> save as events.csv

# 4. Run the event study analysis (~1 minute)
python 03_event_study.py

# 5. Launch the dashboard
streamlit run dashboard.py
```

Each step writes its outputs to disk, so you can resume from any point. Skip script 1 and 2 if flight data is already pulled; skip pull_8ks.py if events.csv is already done.

## Methodology in one paragraph

For each retained 8-K filing $i$ on date $t_i$, we estimate a market model on the [-250, -30] trading-day window:
$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i R_{m,t})$$
and compute the cumulative abnormal return over the three-day event window:
$$CAR_i = \sum_{t=-1}^{+1} AR_{i,t}$$
We construct flight-activity features in the [-30, 0] day window (flight count over 30d and 7d, unique destinations, flights to target region for M&A events, flight count above firm baseline) and estimate the cross-sectional regression
$$CAR_i = \alpha + \beta_1 \cdot \text{flight\_count\_30d}_i + \beta_2 \cdot \text{flights\_to\_target\_region}_i + \gamma \cdot X_i + \epsilon_i$$
with event-type and firm fixed effects. The coefficients $\beta_1$ and $\beta_2$ test whether flight activity carries predictive content for event reactions.

## Team

| Person | Role |
|---|---|
| Owen | Data pipeline, FAA verification, OpenSky integration, event study code |
| Harry | (TBD — Streamlit dashboard) |
| Ford | (TBD — writeup, lit review, results interpretation) |

## Status

- [x] Aircraft verified (10/10 HIGH confidence via FAA + SEC + OpenSky)
- [x] OpenSky pull script working (auth, chunking, rate-limit handling)
- [x] EDGAR 8-K extraction working
- [x] Event study + market model code written
- [x] Paper draft (intro, lit review, methodology, limitations)
- [ ] OpenSky Trino academic application submitted, awaiting review
- [ ] Flight data pulled (blocked on API quota / Trino approval)
- [ ] 8-K events classified (Owen working on this)
- [ ] Dashboard built (Harry)
- [ ] Results filled in, vignettes selected
- [ ] Final writeup polish

## Caveats and limitations

See Section 6 of `paper_draft.md` for the full discussion. In short:
- Sample size (~30-50 events) is small for inferential claims; we present coefficient estimates as descriptive
- Passenger identity is unobservable from ADS-B data
- ADS-B coverage is uneven, particularly outside continental US/Europe
- Privacy regime selection bias: our sample is mid-cap by necessity
- API quota constrained the study window to 6 months
- yfinance is used instead of CRSP (acknowledged tradeoff)

## References

- Yermack, D. (2014). Tailspotting: Identifying and profiting from CEO vacation trips. *Journal of Financial Economics*, 113(2), 252-269.
- Bushee, B. J., Gerakos, J., & Lee, L. F. (2018). Corporate jets and private meetings with investors. *Journal of Accounting and Economics*, 65(2-3), 358-379.
- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13-39.
- OpenSky Network REST API: https://openskynetwork.github.io/opensky-api/rest.html
- SEC EDGAR Submissions API: https://www.sec.gov/cgi-bin/browse-edgar
- FAA Aircraft Registry: https://registry.faa.gov/aircraftinquiry
