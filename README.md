# Aviation Event Study — 3 Day Sprint Plan

## What we have
10 verified corporate aircraft, FAA registered owners cross-checked against
SEC DEF 14A filings and OpenSky operator data. All HIGH confidence.

| Company | Tail | Aircraft |
|---|---|---|
| Newell Brands | N904NB | Falcon 900EX |
| Skechers | N543GL | Bombardier BD-700 (Global) |
| Great Southern Bancorp | N923GS | Cessna 560XL |
| Life Time Group | N990LT | Falcon 900 |
| Nordstrom | N561FX | Bombardier Challenger 350 |
| Macy's | N765M | Gulfstream G200 |
| Murphy USA | N1MU | Bombardier Challenger 350 |
| Liberty Media | N780LM | Falcon 7X |
| CenterPoint Energy | N102CE | Bombardier Challenger 350 |
| Workday | N191MM | Falcon 7X |

## Study window
April 1, 2023 – April 1, 2025 (24 months)

## Three-person split

### Person A — Data pipeline (Days 1–2)
- Add `icao24` column to spreadsheet (copy from FAA registry pages)
- Make free OpenSky account, set credentials in environment
- Run scripts 1 + 2; deliver `flights_enriched.csv` by Day 2 noon
- Help Person C with charts on Day 3

### Person B — Event collection (Days 1–2)
Hand-collect a list of major announcements for 3 focal companies:
**Liberty Media, Workday, CenterPoint Energy**
- Pull 8-K filings from EDGAR for each
- For each 8-K, record: date, company, item code, brief description, URL
- Target: 15-30 events per company (so 45-90 total)
- Output: `events.csv` with columns:
  date, company, event_type, description, target_location, source_url

### Person C — Writeup + analysis (Days 1–3)
- Day 1: Draft intro, lit review (Yermack 2014, Bushee/Gerakos/Lee 2018), methodology
- Day 2: Once Person A delivers data, build descriptive analysis + charts
- Day 3: Final writeup, vignettes, conclusion, edits

## Daily sync
30 minutes at 6 PM, every day. No more.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate           # mac/linux
# or .venv\Scripts\activate         # windows
pip install pandas requests openpyxl

# Make a free account at https://opensky-network.org/index.php?option=com_users&view=registration
export OPENSKY_USERNAME="your_username"
export OPENSKY_PASSWORD="your_password"

# (after adding icao24 column to spreadsheet)
python 01_pull_flights.py     # ~15-30 min depending on rate limits
python 02_enrich_flights.py   # ~30 seconds
```

## Output files
- `raw_flights/<TAIL>.csv` — per-aircraft raw OpenSky data
- `flights_all.csv` — combined raw flights
- `flights_enriched.csv` — final analysis dataset (one row per flight, with
  airport names/cities/coords for both departure and arrival)
- `events.csv` — Person B's hand-curated event list
- `airports.csv` — cached OurAirports database (auto-downloaded)

## What the writeup will look like (Person C)

**Section 1: Introduction** (~1 page)
Frame the question: "Do flight patterns of corporate aircraft predict or
correlate with major corporate announcements?" Note this builds on Yermack
(2014) "Tailspotting" and Bushee, Gerakos & Lee (2018).

**Section 2: Data and methodology** (~2 pages)
- How aircraft were verified (FAA registry → SEC filings → OpenSky cross-check)
- Why these 10 mid-cap firms (verifiable, not privacy-shielded)
- Flight data via OpenSky REST API
- Event data via 8-K filings
- LIMITATIONS section: 24-month window, 10 firms, can't confirm passenger
  identity, descriptive not predictive

**Section 3: Descriptive results** (~2 pages with charts)
- Total flights per company
- Top destinations
- Geographic and temporal patterns
- Map visualization

**Section 4: Vignettes** (~2-3 pages)
Pick the 2-3 cleanest event/flight matches across the 3 focal companies.
For each: chart of flights in the [-30, +5] window around the event date,
narrative paragraph.

**Section 5: Discussion and limitations** (~1 page)
What we found. What we didn't find. What a longer study with more firms
could establish. The methodology shift to mid-cap firms (since most CEO
megacap planes are now privacy-protected) is itself a contribution.

**Section 6: Conclusion** (~half page)

Total: ~8-10 pages. Clean, honest, scoped to what's actually doable in 3 days.
