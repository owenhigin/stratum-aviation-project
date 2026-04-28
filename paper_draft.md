# Tracking Corporate Aircraft to Predict Material Event Returns

**An Event Study with Alternative Data**

Owen Higinbotham, Harry Keen, Ford Campbell

FIN 377: Data Science for Finance
Lehigh University
Advised by Professor Donald Bowen

---

## Abstract

We test whether pre-announcement flight activity of corporate aircraft predicts the magnitude of stock price reactions to material corporate events. Using a sample of ten verified U.S. corporate aircraft and a six-month window (October 2024 – April 2025), we construct flight-activity features in the [-30, 0] day window before each 8-K filing for three focal firms (Liberty Media, Workday, and Newell Brands) and regress event-window cumulative abnormal returns on these flight features. Building on the methodology of Yermack (2014) and combining it with a standard event-study framework, we treat flight data as an alternative data signal that may carry information about event significance prior to public disclosure. Our methodological contribution is documenting how recent expansions in aviation ownership privacy under 49 U.S.C. § 44114 and the 2024 FAA Reauthorization Act constrain the original Yermack approach, motivating a focus on mid-cap firms whose aircraft remain verifiable through public records. [FILL IN: high-level summary of empirical results once data is collected.]

---

## 1. Introduction

Corporate aircraft create a public information trail. Every flight broadcasts the aircraft's transponder code, position, and trajectory through ADS-B (Automatic Dependent Surveillance-Broadcast), and these signals are aggregated by community networks like the OpenSky Network into searchable historical databases. When a corporate aircraft can be linked to a specific firm or executive, its movements become an alternative data source — a window into where decision-makers are physically going in the days before that information is publicly disclosed.

Yermack (2014) was the first to formalize this idea in academic finance. Using a Wall Street Journal database of executive aircraft, he showed that corporate jet vacations correlated with periods of below-average firm performance, and that flight patterns leaked information about CEO time allocation that had not been previously visible to investors. Bushee, Gerakos, and Lee (2018) extended the methodology to roughly 400,000 corporate flights and documented that flight patterns reveal otherwise-private investor meetings during pre-earnings windows. Edgerton (2012) used corporate jet utilization to study agency problems in leveraged buyouts.

This paper combines the Yermack flight-tracking framework with a standard event-study methodology to ask a more targeted question: does pre-announcement flight activity predict the stock price reaction to material corporate events? We test this empirically by constructing flight-activity features in the [-30, 0] day window preceding each 8-K filing in our sample, computing cumulative abnormal returns (CARs) over the [-1, +1] event window using a market model, and regressing CARs on flight features. The framing treats flights as an alternative data signal — analogous to satellite imagery, credit card transactions, or web traffic data used in modern quantitative finance — that may carry information about event significance ahead of public disclosure.

A secondary contribution of the paper is methodological. The original Yermack (2014) study relied on a Wall Street Journal database obtained through a 2011 FOIA request, which mapped operator entities to specific tail numbers. That database is now defunct, and the underlying data environment has changed substantially. The 2024 FAA Reauthorization Act expanded ownership privacy protections, allowing aircraft owners to redact their identities from the public FAA registry, and the use of nominee trust structures (particularly under Wyoming law) has become widespread among high-profile aircraft owners. Mega-cap CEO aircraft — the kind Yermack and Bushee et al. could readily identify — are increasingly difficult to attribute to specific firms or executives through public records alone. We address this by deliberately focusing on mid-cap firms whose aircraft remain verifiable, and we document the verification process in detail in Section 3.1.

## 2. Literature Review

**Yermack (2014), "Tailspotting: Identifying and Profiting from CEO Vacation Trips."** Yermack tracked 35 corporate jets across S&P 500 firms over 2007–2010 using a database compiled by the Wall Street Journal. He found that vacation flights to CEO holiday homes were associated with subsequent below-average firm-level returns and that aggregate CEO leisure travel correlated with firm performance in economically meaningful ways. The paper is foundational in establishing that corporate aviation data has cross-sectional informational content beyond what is available in standard disclosure filings.

**Bushee, Gerakos, and Lee (2018), "Corporate jets and private meetings with investors."** Building on Yermack's framework but at much larger scale, Bushee et al. used approximately 400,000 corporate flight records to identify "roadshow" patterns — three-day windows containing flights to money centers and to non-money centers in which the firm has high institutional ownership. These flight patterns were predictive of subsequent earnings announcements and abnormal stock returns, suggesting that private investor meetings revealed in flight data carry information not yet impounded in prices.

**Edgerton (2012), "Agency Problems at Public Firms: Evidence from Corporate Jets in Leveraged Buyouts."** Edgerton showed that corporate jet utilization declines after firms go private through leveraged buyouts, supporting agency-cost interpretations of executive perquisites and demonstrating that flight data captures economically meaningful aspects of firm behavior.

**Event-study methodology.** The standard event-study framework dates to Fama, Fisher, Jensen, and Roll (1969) and was systematized by MacKinlay (1997). The framework computes abnormal returns around an event date as the difference between observed returns and a benchmark expectation, typically generated by a market model estimated over a pre-event window. Cumulative abnormal returns (CARs) over a short window centered on the event date are the standard outcome variable for testing whether new information has been priced. We follow this conventional design in our analysis.

**Privacy regime literature.** Section 803 of the FAA Reauthorization Act of 2024 expanded the FAA's privacy programs (codified at 49 U.S.C. § 44114), allowing aircraft owners to formally redact their names from publicly accessible registry records. In parallel, state-level privacy structures — particularly Wyoming nominee trusts — have become widely used by high-net-worth aircraft owners to obscure beneficial ownership. We are not aware of prior academic work documenting how this regime change affects the feasibility of Yermack-style empirical research, and we treat this gap as part of our contribution.

## 3. Data and Methodology

### 3.1 Sample Construction

Our sample consists of ten U.S.-registered corporate aircraft, each linked to a publicly traded mid-cap U.S. firm through a multi-source verification process. We deliberately chose mid-cap firms over the mega-cap firms studied in Yermack (2014) because mid-cap firms are less likely to use aviation privacy structures and their aircraft remain attributable through public records.

For each candidate aircraft we required a verifiable evidentiary chain consisting of: (1) an FAA Aircraft Registry record showing a registered owner whose name explicitly references the firm or a clearly identified corporate subsidiary; (2) confirmation that the owner's registered address corresponds to a verifiable corporate address (typically headquarters or a known facility); (3) corroborating disclosure in the firm's most recent SEC DEF 14A proxy statement or other annual filing; and (4) consistency with operator metadata in the OpenSky Network database. Aircraft for which any link in this chain was redacted, ambiguous, or contradicted by another source were excluded. The final sample of ten aircraft is summarized in Table 1.

**Table 1. Verified sample of corporate aircraft**

| Company | Tail Number | ICAO24 | Aircraft | Registered Owner |
|---|---|---|---|---|
| Newell Brands | N904NB | AC7F36 | Dassault Falcon 900EX | Newell Brands Inc |
| Skechers USA | N543GL | A6E3B2 | Bombardier BD-700 Global | Skechers USA Inc |
| Great Southern Bancorp | N923GS | ACC9F6 | Cessna 560XL | Great Southern Bank |
| Life Time Group | N990LT | ADD3AF | Dassault Falcon 900 | Life Time Fitness Inc |
| Nordstrom | N561FX | A72B34 | Bombardier Challenger 350 | Nordstrom Inc |
| Macy's | N765M | AA552E | IAI Gulfstream 200 | Macy's Corporate Services LLC |
| Murphy USA | N1MU | A00128 | Bombardier Challenger 350 | Murphy Oil USA Inc |
| Liberty Media | N780LM | AA918C | Dassault Falcon 7X | Liberty Media Corp |
| CenterPoint Energy | N102CE | A00C59 | Bombardier Challenger 350 | CenterPoint Energy Service Co LLC |
| Workday | N191MM | A16D01 | Dassault Falcon 7X | Workday Inc |

For deeper analysis we focus on three companies — Liberty Media, Workday, and Newell Brands — selected because each had non-trivial corporate event activity during the study window and each spans a different sector (media/entertainment, enterprise software, and consumer goods respectively).

### 3.2 Study Window

We restrict our analysis to a six-month window from October 1, 2024 through April 1, 2025. This window was chosen for two reasons. First, it is sufficiently recent that all aircraft in our sample have continuous coverage in the OpenSky Network database. Second, the six-month length captures a standard event-study horizon containing multiple fiscal quarters of corporate activity for each focal firm while remaining tractable within the API quota constraints described in Section 3.3.

### 3.3 Flight Data Source

Flight data is obtained from the OpenSky Network, a community-based ADS-B receiver network maintained by an academic consortium. We query the `/flights/aircraft` endpoint of the OpenSky REST API for each verified aircraft, identified by its 24-bit ICAO transponder hex code. Each query returns a list of flight summaries containing departure airport, arrival airport, takeoff time, and landing time. We enrich these summaries with airport metadata — name, city, country, latitude, longitude — drawn from the OurAirports.com public database.

OpenSky's REST API enforces a daily credit budget on authenticated users and limits each `/flights/aircraft` query to a two-day window. We accordingly chunk our queries into two-day segments and pool API credentials across three group-member accounts to remain within rate limits.

### 3.4 Event Data Source

Material corporate events are identified through SEC Form 8-K filings for each focal company over the same six-month window. 8-K filings disclose a defined set of material events within four business days, identified by item codes (1.01 for material agreements, 2.01 for completed acquisitions, 5.02 for officer changes, etc.). We pull all 8-K filings for our three focal companies via the SEC EDGAR submissions API and classify each by item code. We exclude routine filings (Item 5.07 annual meeting vote results, Item 9.01 standalone exhibits, Item 7.01 disclosures of already-public information) which carry no information asymmetry. For each retained filing we record the filing date, item codes, a brief description, and where applicable the location of the counterparty (acquisition target headquarters, etc.).

### 3.5 Stock Price Data and Abnormal Return Computation

Daily closing prices for each focal firm and for the S&P 500 (ticker `^GSPC`) are obtained from Yahoo Finance via the `yfinance` Python package. We compute daily returns as percent changes in adjusted close.

For each event $i$ on date $t_i$, we compute abnormal returns using a standard market model:

$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i R_{m,t})$$

where $R_{i,t}$ is the firm's daily return on day $t$, $R_{m,t}$ is the S&P 500 return on day $t$, and $(\hat{\alpha}_i, \hat{\beta}_i)$ are OLS estimates of the market-model parameters from a pre-event estimation window of $[-250, -30]$ trading days relative to the event date. The 220-day estimation window is standard in the literature (MacKinlay 1997) and excludes the 30 days immediately before the event to avoid contamination from any pre-announcement information leakage.

We compute the cumulative abnormal return over the three-day event window $[-1, +1]$:

$$CAR_i = \sum_{t=-1}^{+1} AR_{i,t}$$

This three-day window is the standard short-horizon CAR specification and captures both the market reaction on the announcement day and any spillover into the days immediately surrounding it.

### 3.6 Flight-Activity Features

For each event $i$, we construct flight-activity features measured over the pre-event window $[-30, 0]$ trading days. The features include:

- **`flight_count_30d`**: total number of flights operated by the firm's aircraft in the [-30, 0] window
- **`flight_count_7d`**: total flights in the narrower [-7, 0] window
- **`unique_destinations_30d`**: count of distinct arrival airports in the [-30, 0] window
- **`flights_to_target_region`** (M&A events only): binary indicator equal to 1 if any flight in the [-30, 0] window arrived at an airport within 100 miles of the target's headquarters
- **`flight_count_above_baseline`**: flight_count_30d minus the firm's average 30-day rolling flight count over the entire study window (a rough abnormal-flight measure)

These features capture both the intensity of pre-event aviation activity and, where applicable, its geographic targeting.

### 3.7 Cross-Sectional Regression

We test whether pre-event flight activity predicts event-window abnormal returns by estimating the cross-sectional regression:

$$CAR_i = \alpha + \beta_1 \cdot \text{flight\_count\_30d}_i + \beta_2 \cdot \text{flights\_to\_target\_region}_i + \gamma \cdot X_i + \epsilon_i$$

where $X_i$ is a vector of controls including event-type fixed effects (M&A, Earnings, Executive_Change, Material_Agreement) and firm fixed effects. The coefficients of interest are $\beta_1$ and $\beta_2$. A positive and statistically significant $\beta_2$ would indicate that pre-event flights to the target region predict larger absolute event reactions, consistent with an information-leakage interpretation.

We also estimate a specification with the absolute value $|CAR_i|$ as the dependent variable, since pre-event flight activity may signal event significance without indicating direction.

We acknowledge upfront that our sample size — likely 30 to 50 retained events across three focal firms — is small for cross-sectional regression, and we interpret coefficient estimates as descriptive rather than statistically definitive.

## 4. Results

[FILL IN: Section 4.1 — Descriptive statistics. Total flights per company, top destinations, time patterns. Insert geographic visualization. Number of retained events per company and event type.]

[FILL IN: Section 4.2 — Mean CARs by event type. Standard event-study summary table showing average CAR[-1,+1] for M&A, Earnings, Material_Agreement, Executive_Change events with t-statistics testing CAR ≠ 0.]

[FILL IN: Section 4.3 — Cross-sectional regression results. Table of regression coefficients on flight features with standard errors.]

[FILL IN: Section 4.4 — 2-3 vignettes. For each: chart of flights and stock returns around the event date, narrative paragraph identifying any clear pattern. Strongest candidates will be selected once flight, event, and price data are joined.]

## 5. Discussion

[FILL IN: 3-5 paragraphs interpreting results. Anticipated structure:

- What did the cross-sectional regressions show? Did flight features carry predictive content for CARs?
- For events with no apparent flight-CAR relationship, what alternative explanations apply (chartered aircraft, virtual meetings, public information already available, sample size)?
- How do our results compare to prior literature (Yermack 2014, Bushee et al. 2018) given our different sample and design?
- What does the success or failure of replication tell us about the contemporary applicability of corporate aviation as an alternative data source?]

## 6. Limitations

This study has important limitations that constrain the strength of any claims we can draw from the data.

**Sample size.** Ten aircraft over six months produces a small set of retained events — likely 30-50 across three focal firms. This is small by event-study standards. Yermack (2014) used 35 aircraft over four years; Bushee et al. (2018) used aggregate data on roughly 400,000 flights. Our cross-sectional regressions are not powered for strong inferential claims, and we present coefficient estimates as descriptive rather than definitive.

**Passenger identity is unobservable.** Flight tracking data identifies aircraft movements, not passenger movements. We cannot directly confirm that a company's CEO or any specific executive was on board any specific flight. Our framing follows Yermack and Bushee et al. in inferring decision-maker travel from corporate aircraft movement based on the known correlation between executive use and corporate jet operation, but this inference is probabilistic.

**ADS-B coverage gaps.** OpenSky's coverage relies on volunteer ADS-B receivers and is uneven. Coverage is generally strong over the continental United States and Europe but weaker in remote areas and over open ocean. Some flights may be missing from our dataset entirely, and others may have incomplete arrival airport data.

**Privacy regime selection bias.** Our requirement that aircraft be cleanly attributable through public records selects systematically against firms whose aircraft are held through privacy structures. Mega-cap firms are underrepresented for this reason. Our findings should be interpreted as applying to the population of mid-cap firms with publicly verifiable aviation, not to the universe of corporate aviation.

**API quota constraints.** OpenSky's free-tier daily credit budget materially shaped our research design, including our six-month window and three-firm focal sample. A future iteration of this study with academic Trino access to the full OpenSky historical database could expand both dimensions substantially.

**Counterparty location matching is inexact.** When matching flights to M&A target locations, we use the target firm's headquarters city. Actual deal negotiations may take place at law-firm offices in major cities, at neutral locations, or virtually, none of which would produce the geographic flight signal our matching procedure looks for.

**Yahoo Finance data quality.** We use yfinance for stock price data rather than CRSP. yfinance is generally accurate for closing prices on liquid stocks but is less rigorously validated than CRSP. Splits, dividends, and corporate actions are handled via Yahoo's adjusted-close field, which is the standard but not perfect.

## 7. Conclusion

[FILL IN: Brief paragraph summarizing main findings, contribution, and future work. Two natural future directions: (1) expanding the sample using academic OpenSky Trino access; (2) extending the time window backward into the pre-2024 regime to test whether the privacy expansion materially changed the feasibility of Yermack-style replication.]

## References

Bushee, B. J., Gerakos, J., & Lee, L. F. (2018). Corporate jets and private meetings with investors. *Journal of Accounting and Economics*, 65(2-3), 358-379.

Edgerton, J. (2012). Agency problems at public firms: Evidence from corporate jets in leveraged buyouts. *The Journal of Finance*, 67(6), 2187-2213.

Fama, E. F., Fisher, L., Jensen, M. C., & Roll, R. (1969). The adjustment of stock prices to new information. *International Economic Review*, 10(1), 1-21.

Federal Aviation Administration. (2025). FAA Aircraft Registry — N-Number Inquiry. https://registry.faa.gov/aircraftinquiry

Federal Aviation Administration Reauthorization Act of 2024, Pub. L. No. 118-63, § 803.

MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13-39.

OpenSky Network. (2025). REST API Documentation. https://openskynetwork.github.io/opensky-api/rest.html

Securities and Exchange Commission. (2025). EDGAR Full-Text Search. https://efts.sec.gov/LATEST/search-index

Yermack, D. (2014). Tailspotting: Identifying and profiting from CEO vacation trips. *Journal of Financial Economics*, 113(2), 252-269.

49 U.S.C. § 44114 (Privacy of Aircraft Registration Information).
