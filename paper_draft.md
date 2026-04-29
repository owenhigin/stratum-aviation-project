# Tracking Corporate Aircraft to Predict Material Event Returns

**An Event Study with Alternative Data**

Owen Higinbotham, Harry Keen, Ford Campbell

FIN 377: Data Science for Finance
Lehigh University
Advised by Professor Donald Bowen

---

## Abstract

We test whether pre-announcement flight activity of corporate aircraft predicts the magnitude of stock price reactions to material corporate events. Using a sample of six verified U.S. mid-cap corporate aircraft and a six-month window (October 2024 – April 2025), we construct flight-activity features in the [-30, 0] day window before each 8-K filing and regress event-window cumulative abnormal returns on these features. Across 39 retained events and three regression specifications, we find no statistically significant relationship between pre-event flight count and three-day CAR (coefficients near zero, p > 0.55). However, descriptive patterns are directionally consistent with the Yermack (2014) and Bushee, Gerakos & Lee (2018) hypotheses: events preceded by elevated flight activity have systematically lower hit rates of positive CARs in the earnings category, and the most striking individual case in our sample — Newell Brands' Q4 2024 earnings (-28.7% CAR) — is preceded by five flights including two round trips to the region surrounding the headquarters of Walmart, Newell's largest customer. Our methodological contribution is documenting that the original Yermack (2014) approach can still be replicated in the post-2024 aviation privacy regime when applied to mid-cap firms whose aircraft remain verifiable through public records.

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

Our analysis sample consists of six U.S.-registered corporate aircraft, each linked to a publicly traded mid-cap U.S. firm through a multi-source verification process. We deliberately chose mid-cap firms over the mega-cap firms studied in Yermack (2014) because mid-cap firms are less likely to use aviation privacy structures and their aircraft remain attributable through public records.

For each candidate aircraft we required a verifiable evidentiary chain consisting of: (1) an FAA Aircraft Registry record showing a registered owner whose name explicitly references the firm or a clearly identified corporate subsidiary; (2) confirmation that the owner's registered address corresponds to a verifiable corporate address (typically headquarters or a known facility); (3) corroborating disclosure in the firm's most recent SEC DEF 14A proxy statement or other annual filing; and (4) consistency with operator metadata in the OpenSky Network database. Aircraft for which any link in this chain was redacted, ambiguous, or contradicted by another source were excluded from the cross-sectional analysis.

We initially identified ten verifiable aircraft. Four were excluded from the cross-sectional analysis for reasons documented in our limitations section: Liberty Media's Falcon 7X (insufficient OpenSky flight coverage during the study window), Life Time Group's Falcon 900 (insufficient OpenSky coverage), Nordstrom's Bombardier Challenger 350 and Skechers' Bombardier BD-700 (Yahoo Finance discontinued historical price data following the firms' 2025 going-private transactions). The final analysis sample of six aircraft is summarized in Table 1.

**Table 1. Verified analysis sample of corporate aircraft**

| Company | Tail Number | ICAO24 | Aircraft | Ticker |
|---|---|---|---|---|
| Newell Brands | N904NB | AC7F36 | Dassault Falcon 900EX | NWL |
| Macy's | N765M | AA552E | IAI Gulfstream 200 | M |
| CenterPoint Energy | N102CE | A00C59 | Bombardier Challenger 350 | CNP |
| Great Southern Bancorp | N923GS | ACC9F6 | Cessna 560XL | GSBC |
| Murphy USA | N1MU | A00128 | Bombardier Challenger 350 | MUSA |
| Workday | N191MM | A16D01 | Dassault Falcon 7X | WDAY |

### 3.2 Study Window

We restrict our analysis to a six-month window from October 1, 2024 through April 1, 2025. This window was chosen for two reasons. First, it is sufficiently recent that all aircraft in our sample have continuous coverage in the OpenSky Network database. Second, the six-month length captures a standard event-study horizon containing multiple fiscal quarters of corporate activity for each focal firm while remaining tractable within the API quota constraints described in Section 3.3.

### 3.3 Flight Data Source

Flight data is obtained from the OpenSky Network, a community-based ADS-B receiver network maintained by an academic consortium. We query the `/flights/aircraft` endpoint of the OpenSky REST API for each verified aircraft, identified by its 24-bit ICAO transponder hex code. Each query returns a list of flight summaries containing departure airport, arrival airport, takeoff time, and landing time. We enrich these summaries with airport metadata — name, city, country, latitude, longitude — drawn from the OurAirports.com public database.

OpenSky's REST API enforces a daily credit budget on authenticated users and limits each `/flights/aircraft` query to a two-day window. We accordingly chunk our queries into two-day segments and pool API credentials across multiple group-member accounts to remain within rate limits.

### 3.4 Event Data Source

Material corporate events are identified through SEC Form 8-K filings retrieved via the EDGAR submissions API. 8-K filings disclose a defined set of material events within four business days, identified by item codes (1.01 for material agreements, 2.01 for completed acquisitions, 5.02 for officer changes, etc.). For each filing we record the filing date, item codes, a brief description, and where applicable the location of the counterparty. We exclude routine filings (Item 5.07 annual meeting vote results, Item 9.01 standalone exhibits, Item 7.01 disclosures of already-public information) which carry no information asymmetry.

After classification and exclusion, the analysis sample contains 39 events distributed across four event types: Earnings (15), Executive Change (10), Other (10), and Material Agreement (4).

### 3.5 Stock Price Data and Abnormal Return Computation

Daily closing prices for each focal firm and for the S&P 500 (ticker `^GSPC`) are obtained from Yahoo Finance via the `yfinance` Python package. We compute daily returns as percent changes in adjusted close.

For each event $i$ on date $t_i$, we compute abnormal returns using a standard market model:

$$AR_{i,t} = R_{i,t} - (\hat{\alpha}_i + \hat{\beta}_i R_{m,t})$$

where $R_{i,t}$ is the firm's daily return on day $t$, $R_{m,t}$ is the S&P 500 return on day $t$, and $(\hat{\alpha}_i, \hat{\beta}_i)$ are OLS estimates of the market-model parameters from a pre-event estimation window of $[-250, -30]$ trading days relative to the event date. The 220-day estimation window is standard in the literature (MacKinlay 1997) and excludes the 30 days immediately before the event to avoid contamination from any pre-announcement information leakage.

We compute the cumulative abnormal return over the three-day event window $[-1, +1]$:

$$CAR_i = \sum_{t=-1}^{+1} AR_{i,t}$$

This three-day window is the standard short-horizon CAR specification and captures both the market reaction on the announcement day and any spillover into the days immediately surrounding it.

### 3.6 Flight-Activity Features

For each event $i$, we construct flight-activity features measured over the pre-event window $[-30, 0]$ calendar days. The features include:

- **`flight_count_30d`**: total flights operated by the firm's aircraft in the [-30, 0] window
- **`flight_count_7d`**: total flights in the narrower [-7, 0] window
- **`unique_destinations_30d`**: count of distinct arrival airports in the [-30, 0] window
- **`flight_count_above_baseline`**: flight_count_30d minus the firm's average 30-day rolling flight count over the entire study window — a rough abnormal-flight measure

These features capture the intensity of pre-event aviation activity and its deviation from each firm's typical operational pattern.

### 3.7 Cross-Sectional Regression

We test whether pre-event flight activity predicts event-window abnormal returns by estimating a sequence of cross-sectional regressions:

$$CAR_i = \alpha + \beta_1 \cdot \text{flight\_count\_30d}_i + \beta_2 \cdot \text{flight\_count\_7d}_i + \gamma \cdot X_i + \epsilon_i$$

We estimate three nested specifications: (1) `flight_count_30d` only; (2) adding `flight_count_7d`; (3) adding event-type and firm fixed effects. Standard errors are heteroskedasticity-robust (HC3). With a sample size of 39 events across six firms, we acknowledge that statistical power is limited and that coefficient estimates should be interpreted as descriptive rather than definitive.

## 4. Results

### 4.1 Sample Description

The 39 retained events span six firms and four event types. Table 2 summarizes per-firm event counts and average flight activity:

**Table 2. Firm-level summary statistics**

| Firm | N events | Mean CAR | % Positive CAR | Avg flights (30d) | Avg flights (7d) |
|---|---:|---:|---:|---:|---:|
| Workday | 7 | +1.98% | 57.1% | 2.7 | 0.0 |
| Macy's | 7 | +0.58% | 42.9% | 9.4 | 2.0 |
| Murphy USA | 5 | +0.40% | 40.0% | 13.4 | 4.8 |
| CenterPoint Energy | 8 | -0.19% | 37.5% | 6.8 | 1.3 |
| Great Southern Bancorp | 7 | -1.54% | 42.9% | 16.3 | 5.9 |
| Newell Brands | 5 | -2.48% | 20.0% | 1.6 | 0.2 |

Aviation activity varies substantially across firms. Great Southern Bancorp's Cessna 560XL averaged 16.3 flights per 30-day window — by far the most active aircraft in the sample — while Newell Brands' Falcon 900EX averaged only 1.6 flights, the least active. This variation is what gives the cross-sectional regression its identifying variation.

### 4.2 Mean CARs by Event Type

Table 3 reports mean three-day CARs by event type:

**Table 3. Mean CAR[-1, +1] by event type**

| Event Type | N | Mean CAR | t-statistic |
|---|---:|---:|---:|
| Earnings | 15 | -0.44% | -0.24 |
| Executive Change | 10 | -0.13% | -0.13 |
| Material Agreement | 4 | -1.43% | -1.00 |
| Other | 10 | +1.15% | +1.56 |

No event-type category produces a mean CAR statistically distinguishable from zero at conventional significance levels. The sample-wide mean is essentially zero, consistent with the small-sample setting and the heterogeneity of event types.

### 4.3 Cross-Sectional Regression Results

Table 4 reports regression coefficients from three nested specifications:

**Table 4. Cross-sectional regression of CAR[-1, +1] on flight features**

| Variable | Model 1 | Model 2 | Model 3 |
|---|---:|---:|---:|
| flight_count_30d | -0.0010 | -0.0016 | -0.0033 |
| | (0.49) | (0.51) | (0.60) |
| flight_count_7d | | +0.0016 | +0.0027 |
| | | (0.34) | (0.35) |
| Event-type FE | No | No | Yes |
| Firm FE | No | No | Yes |
| R² | 0.007 | 0.009 | 0.072 |
| N | 39 | 39 | 39 |

*Heteroskedasticity-robust (HC3) absolute t-statistics in parentheses. None significant at p < 0.10.*

Across all three specifications, the coefficient on `flight_count_30d` is small, negative, and statistically indistinguishable from zero (p > 0.55 in every specification). The full specification with event-type and firm fixed effects explains only 7.2% of the variation in CARs. We do not reject the null hypothesis that pre-event flight count has zero predictive content for short-window abnormal returns in this sample.

### 4.4 Suggestive Descriptive Patterns

While the formal regression yields a null result, two descriptive patterns are worth noting given their consistency with the Yermack (2014) hypothesis and the fact that small samples have inherently low statistical power.

**Pattern 1: Positive-CAR hit rate is lower for events preceded by above-baseline flight activity.** Table 5 reports the share of positive CARs conditional on whether pre-event flight count exceeded the firm's own baseline:

**Table 5. Hit rate of positive CARs, by pre-event flight activity**

| Event Type | Above-baseline N | % positive | Below-baseline N | % positive | Lift (pp) |
|---|---:|---:|---:|---:|---:|
| Earnings | 4 | 0.0% | 11 | 63.6% | -63.6 |
| Executive Change | 2 | 0.0% | 8 | 37.5% | -37.5 |
| Material Agreement | 1 | 0.0% | 3 | 0.0% | 0.0 |
| Other | 4 | 100.0% | 6 | 33.3% | +66.7 |
| **All** | **11** | **36.4%** | **28** | **42.9%** | **-6.5** |

For earnings events specifically, every observation in our sample with above-baseline pre-event flight activity (N = 4) exhibited a non-positive CAR, while 7 of 11 below-baseline observations were positive. This pattern is directionally consistent with the hypothesis that elevated pre-event flight activity around earnings reflects management responses to anticipated negative news. We caveat strongly that a four-observation cell cannot support inferential claims; we report the pattern as motivation for the case study in Section 4.5.

**Pattern 2: "Dark" periods (zero flights in the 30-day window) are associated with positive CARs.** Across the four events with zero pre-event flights, the mean CAR is +4.6% (75% negative-CAR rate), versus -0.7% (57% negative) for the 35 events with at least one pre-event flight. Again, four-observation evidence is suggestive only.

### 4.5 Vignette: Newell Brands Q4 2024 Earnings

The most striking individual case in our sample is Newell Brands' Q4 2024 earnings announcement on February 7, 2025, which produced a CAR of -28.7% — the largest absolute CAR in the dataset. Newell reported a 6.1% year-over-year sales decline and initiated 2025 guidance projecting further sales contraction of 2-4%. The stock fell 26% on the announcement day on volume of 34.5 million shares, approximately five times the trailing average.

In the 30 days preceding the announcement, Newell's Falcon 900EX (N904NB, registered to Newell Brands Inc. at 6655 Peachtree Dunwoody Road, Atlanta) made five flights. Three of these involved the Atlanta DeKalb-Peachtree airport (KPDK), the corporate-jet airport for the Atlanta region where Newell is headquartered. Two were same-day round trips between Atlanta and airfields in Northwest Arkansas — specifically, arrivals at airstrips near Rogers and Eureka Springs, Arkansas. Rogers is in the Bentonville metropolitan area, where Walmart Inc. is headquartered. Walmart is Newell's largest single customer and a significant determinant of its quarterly performance, as documented in Newell's annual filings.

The pattern: two same-day round trips between Newell's headquarters region and the customer's headquarters region (January 16 and January 27, 2025), in the four weeks leading up to a guidance disappointment that produced a 26% single-day decline in market value.

We cannot infer the specific business purpose of these flights from public records, and the corporate aircraft is not exclusively used by senior leadership. However, the geographic pattern is consistent with customer-related discussions of the type that would be expected in advance of a negative earnings revision driven by a major customer relationship. By contrast, Newell's Q3 2024 earnings release on October 25, 2024 — which prompted a +28.5% positive market reaction — was preceded by zero observed corporate aircraft activity in the [-30, 0] window. The contrast between these adjacent quarterly events illustrates the type of pre-announcement pattern variation that Yermack (2014) and Bushee, Gerakos & Lee (2018) document at larger scale.

This vignette is one observation. It does not demonstrate predictive content of flight data in general. It is, however, the kind of granular pattern that motivates the alternative-data hypothesis our regression was designed to test.

## 5. Discussion

The headline empirical result is a statistical null: in our sample of 39 events across six mid-cap firms, the relationship between pre-event corporate aircraft activity and three-day announcement CARs is not statistically significant under any of three regression specifications. This is, in our view, an honest and informative result given the constraints of our research design.

Several explanations for the null result deserve consideration.

First, **sample size**. With 39 observations, our regression has limited power to detect economically meaningful effects. The original Bushee, Gerakos, and Lee (2018) result was identified across approximately 400,000 flights and tens of thousands of firm-quarters; we work with three orders of magnitude less data. A small effect that exists in the population may simply be undetectable at our scale.

Second, **selection bias from the privacy regime**. Our verification chain — designed to be robust against the post-2024 aviation privacy infrastructure — necessarily excludes large-cap firms whose aircraft are now shielded by federal privacy programs and nominee-trust structures. To the extent that informational content of flight data is concentrated at firms with the most aggressive private deal-making (which would correlate with privacy adoption), our sample may systematically miss the firms where the effect would be largest.

Third, **measurement error in the predictor**. Our `flights_to_target_region` variable was designed to test the Yermack target-matching hypothesis directly. After event reclassification, our sample contained no M&A events with both completed flight data and identifiable counterparty headquarters, eliminating cross-sectional variation in this measure. We retain it for completeness but it carries no information in this sample.

Fourth, **confounding through aircraft sharing**. Several aircraft in our sample are operated through executive flight management companies (e.g., the Newell Falcon 900EX uses callsign EJM904, indicating Executive Jet Management operation). These aircraft may carry passengers from multiple companies, weakening the signal between flight destination and the registered firm's executive activity.

Despite the null formal result, two descriptive patterns are worth noting. The hit-rate analysis (Section 4.4 Pattern 1) shows that earnings events preceded by above-baseline flight activity are uniformly negative in our sample, while below-baseline events are mostly positive. The vignette analysis (Section 4.5) finds the largest absolute CAR in the sample is preceded by a flight pattern with a clear customer-related geographic interpretation. Neither finding is statistically definitive, but both are directionally consistent with the alternative-data hypothesis at a sample size that is at the lower limit of feasibility for this kind of work.

The most important implication of our results is methodological. The Yermack (2014) approach **can still be replicated** in the post-2024 privacy regime — but only by deliberately restricting attention to firms whose aircraft remain attributable through public records. This restricts the sample size by orders of magnitude. Future work that obtains academic Trino access to the full OpenSky historical database, or that builds a verified aircraft registry across the entire S&P 500 or a sector, would dramatically expand statistical power and is the obvious next step for this line of research.

## 6. Limitations

This study has important limitations that constrain the strength of any claims we can draw from the data.

**Sample size.** Six firms and 39 events is small by event-study standards. Yermack (2014) used 35 firms over four years; Bushee et al. (2018) used aggregate data on roughly 400,000 flights. Our regression specifications are not powered for strong inferential claims, and we present coefficient estimates as descriptive.

**Excluded firms.** Four of our ten verified aircraft were excluded from the cross-sectional analysis. Liberty Media and Life Time Group Holdings were excluded due to insufficient OpenSky flight coverage during the study window — a known limitation of the community-driven ADS-B network. Nordstrom and Skechers were excluded after both firms' tickers were removed from Yahoo Finance's historical price database following 2025 going-private transactions, leaving us without a tractable price source under deadline constraints. The exclusion of two M&A events (Liberty/Dorna, Nordstrom/Norse) eliminated cross-sectional variation in our `flights_to_target_region` variable.

**Passenger identity is unobservable.** Flight tracking data identifies aircraft movements, not passenger movements. We cannot directly confirm that a company's CEO or any specific executive was on board any specific flight. Our framing follows Yermack and Bushee et al. in inferring decision-maker travel from corporate aircraft movement based on the known correlation between executive use and corporate jet operation, but this inference is probabilistic.

**Aircraft sharing through fleet operators.** Several aircraft in our sample are operated through executive flight management companies. These aircraft may not exclusively carry the registered firm's executives; their movements should be interpreted as a noisy signal rather than a clean record of corporate travel.

**ADS-B coverage gaps.** OpenSky's coverage relies on volunteer ADS-B receivers and is uneven. Coverage is generally strong over the continental United States and Europe but weaker in remote areas and over open ocean. Some flights may be missing from our dataset entirely.

**Privacy regime selection bias.** Our requirement that aircraft be cleanly attributable through public records selects systematically against firms whose aircraft are held through privacy structures. Mega-cap firms are underrepresented for this reason. Our findings should be interpreted as applying to the population of mid-cap firms with publicly verifiable aviation, not to the universe of corporate aviation.

**API quota constraints.** OpenSky's free-tier daily credit budget materially shaped our research design, including our six-month window. A future iteration of this study with academic Trino access to the full OpenSky historical database could expand both dimensions substantially.

**Counterparty location matching.** Our `flights_to_target_region` measure used substring matching of arrival cities against counterparty headquarters cities. This approach is conservative — flights to nearby corporate-jet airports (e.g., Teterboro for New York City meetings) may be missed.

**yfinance vs. CRSP.** We use yfinance for stock price data rather than the academic-standard CRSP database. yfinance is generally accurate for closing prices on liquid stocks but is less rigorously validated. The discontinuation of historical data for delisted tickers (Nordstrom and Skechers) is a specific manifestation of this tradeoff.

## 7. Conclusion

We document that the Yermack (2014) corporate-aircraft tracking methodology can be replicated in the post-2024 aviation privacy regime when deliberately restricted to mid-cap firms whose aircraft remain verifiable through cross-referenced public records. Across 39 events at six such firms over a six-month window, we find no statistically significant relationship between pre-event flight activity and three-day announcement CARs. Descriptive patterns in subsamples are directionally consistent with the alternative-data hypothesis but lack the statistical power to support inferential claims.

The most striking individual case in our sample — Newell Brands' Q4 2024 earnings announcement, preceded by five flights including two round trips to the headquarters region of Newell's largest customer — illustrates the type of granular pattern this methodology can surface. It also illustrates why the methodology is genuinely difficult to scale: identifying such patterns requires firm-by-firm verification work and case-specific interpretation of geographic context.

Two natural extensions would substantially advance this research line. First, academic Trino access to the OpenSky Network would remove the API quota constraint that limited our window to six months and would enable expansion to multi-year panels. Second, building a verified aircraft registry across an entire sector or index — perhaps with assistance from academic data partners or commercial aviation databases — would push sample size into the range where the regression-based hypothesis tests of Bushee, Gerakos, and Lee (2018) become feasible. The methodological infrastructure we document here is a starting point for that work.

## References

Bushee, B. J., Gerakos, J., & Lee, L. F. (2018). Corporate jets and private meetings with investors. *Journal of Accounting and Economics*, 65(2-3), 358-379.

Edgerton, J. (2012). Agency problems at public firms: Evidence from corporate jets in leveraged buyouts. *The Journal of Finance*, 67(6), 2187-2213.

Fama, E. F., Fisher, L., Jensen, M. C., & Roll, R. (1969). The adjustment of stock prices to new information. *International Economic Review*, 10(1), 1-21.

Federal Aviation Administration. (2025). FAA Aircraft Registry — N-Number Inquiry. https://registry.faa.gov/aircraftinquiry

Federal Aviation Administration Reauthorization Act of 2024, Pub. L. No. 118-63, § 803.

MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13-39.

OpenSky Network. (2025). REST API Documentation. https://openskynetwork.github.io/opensky-api/rest.html

Securities and Exchange Commission. (2025). EDGAR Submissions API.

Yermack, D. (2014). Tailspotting: Identifying and profiting from CEO vacation trips. *Journal of Financial Economics*, 113(2), 252-269.

49 U.S.C. § 44114 (Privacy of Aircraft Registration Information).
