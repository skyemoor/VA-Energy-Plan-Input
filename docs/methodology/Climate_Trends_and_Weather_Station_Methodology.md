# Climate Trends and Weather-Station Methodology for Demand Profiles Through 2045

Compiled 2026-08-24, arising from a direct user question: how should climate change (summer heat
waves, winter "polar vortex" events) be expected to affect Scenario 3's own demand profiles through
2045, and what real Virginia-specific evidence exists to inform that. All content below follows the
standing instruction established this session: insights, rationale, and tradeoffs stated explicitly,
not left implicit.

**Guiding question, not yet fully answered — the rest of this file is groundwork toward it**: "how
will this affect demand profiles through 2045." Everything below is evidence-gathering and
methodology-setting in service of that question, not a final answer to it.

---

## 1. The authoritative Virginia-specific source: the Virginia Climate Assessment (VCA)

**Insight**: Virginia's first-ever statewide climate assessment was released November 2025 by GMU's
Virginia Climate Center (VCC), a peer-reviewed synthesis explicitly designed to inform exactly this
kind of infrastructure/demand planning question.

**Rationale/context**: worth a precise clarification, since the user asked specifically about "the
VA state climatology office" — there are two distinct things. An older "Virginia State Climatology
Office" (housed at UVA) is listed by the American Association of State Climatologists as effectively
vacant; Virginia and Arkansas were, until mid-2026, the only two states without a functioning state
climate office. A new, funded Virginia State Climate Office now exists at GMU. The VCA is the
authoritative current source, not the older UVA office.

Full citation: Ruess, P.J., Kinter, J., Ferreira, C.M., Ortiz, L.E., et al. (2025). *The First
Virginia Climate Assessment*. https://doi.org/10.13021/MARS/15226. Full PDF fetched directly:
https://static1.squarespace.com/static/63f528dab026ae551cca0060/t/6931df89743e0909035d357f/1764876169961/The+First+Virginia+Climate+Assessment.pdf

---

## 2. Summer heat — quantified, one-directional, and already connected to this project's own findings

**Insight**: the VCA both quantifies historical/projected summer heat trends and explicitly connects
them to the exact data-center/grid-stress dynamic this project has independently been analyzing.

- Wet Bulb Globe Temperature (WBGT — heat stress accounting for humidity/radiation, not just air
  temperature) has risen **0.29°F per decade since 1950**, statewide.
- Projected days above 95°F **dry-bulb air temperature** (Tmax — NOT WBGT; see Section 3 for why
  this distinction matters) by end-of-century: **~10 days** under low-emissions SSP1-2.6 to **>50
  days** under high-emissions SSP5-8.5 — CMIP6 ensemble, high confidence, wide range because it
  depends entirely on future global emissions, which this project cannot forecast.
- Cooling degree-days have risen **19.8-45°F-days per decade since 1951**, with the **largest
  increases specifically in the Tidewater and Northern climate divisions** — Northern Virginia named
  directly as one of the two most heat-intensifying regions in the state.

**Rationale for direct relevance to this project's own prior work**: the VCA independently makes the
same connection this project's own Dominion-zone LMP analysis found (see
`Dominion_Zone_Load_Shape_and_LMP_Analysis.md`). Direct quote: *"The recent surge in energy intensive
data centers, particularly in the Northern division, could impact the sensitivity of the electric
system to warming climates as demand for cooling increases as its share of the local grid demand
increases."* And: *"heat index extremes are the most common weather type during outages in counties
in the Northern Climate Division."* A peer-reviewed state assessment independently confirms the
Northern-VA-summer-heat-vulnerability pattern already found empirically in the Loudoun/Tysons LMP
spike data (entry #86) — convergent evidence from two entirely different methods.

**Tradeoff**: the 10-50+ day range is wide because emissions pathway is unknowable in advance. Any
single number chosen for future-year modeling checkpoints is a judgment call about which pathway to
assume, not a fact — should be stated as an assumption, not presented as a forecast.

---

## 3. Wet bulb vs. dry bulb — a real distinction, clarified directly (user question)

**Direct answer**: the "10-50 days above 95°F" projection is **dry bulb** (standard air/Tmax
temperature), NOT WBGT. Confirmed by the VCA's own exact wording: *"days with **maximum
temperatures** reaching 95°F"* — "maximum temperature" is standard Tmax terminology, distinct from
WBGT, which the VCA's own Table 1 lists as a separate indicator alongside dry bulb, wet bulb, and
heat index.

**Why this matters practically, not just technically**: WBGT is always lower than air temperature
except at 100% humidity. A 95°F WBGT reading would be near the upper limit of human survivability —
essentially unprecedented. 95°F dry-bulb is a routine Virginia summer afternoon. Conflating the two
(as the two figures were presented near each other, without disambiguation, in this project's own
prior turn) risks badly misjudging how extreme/plausible the projected day-count actually is.

---

## 4. Winter cold / "polar vortex" — genuinely more complicated than summer heat, not a simple "yes"

**Insight, stated directly even though it may run counter to intuition**: the VCA's own data shows
the *opposite* of straightforward winter-cold intensification, at the level of overall statistical
distribution. High-confidence finding: *"the coldest days are warming faster than the warmest days."*
Extreme cold nights are decreasing 1-3 days/decade; extreme warm nights increasing 1-2 days/decade.
Projected minimum daily lows are expected to rise even faster (175-250% of global mean warming) than
daily highs (100-150%).

**Rationale for why this is a genuinely different question than discrete cold-snap event frequency**:
the VCA's finding is about the overall distribution of winter temperatures, not about whether
discrete, disruptive polar vortex disruption *events* are becoming more frequent within a warmer
overall winter. This is an active, explicitly unresolved scientific debate, not settled either way.
Direct quote from a Dec. 2024 peer-reviewed review (Cohen et al. and related work, IOPscience): *"It
is widely accepted that Arctic amplification will increasingly moderate cold-air outbreaks... Yet,
some recent studies also argue that Arctic amplification... may contribute to more frequent severe
winter weather including disruptive cold spells... it is necessary to resolve whether [these] are
coincidental or physically linked."* Real, documented evidence exists on both sides, including that
"the frequency of [stratospheric polar vortex] stretching events increased in the era of amplified
Arctic warming" (Cohen et al. 2021, cited in Springer Nature Climate Dynamics, Jan. 2026).

**A concrete, well-timed correspondence worth flagging, not treated as proven causation**: the
winter cold-snap event already found in this project's own Dominion-zone LMP data (Jan 31-Feb 9,
2026; entry #86) sits inside a window when multiple real, documented Sudden Stratospheric
Warming/polar vortex disruption events were actively covered in real-time forecasting news — one in
early-to-mid January 2026, another in February-March 2026. This project didn't go looking for this
connection; it fell out of independently-sourced climate literature after the fact. The exact
disruption dates have not been confirmed to precisely match the LMP spike to the day — a plausible,
well-timed correspondence, not a proven causal link.

**Tradeoff for future-year methodology**: summer heat evidence is one-directional and supports
treating historical extreme-heat-hour frequency as a **floor, not a ceiling**, for 2035/2040/2045
checkpoints. Winter cold evidence does not support the same one-directional adjustment — applying a
"more frequent/severe" multiplier to winter extremes the same way as summer would not be defensible
on current evidence. The safer stance: treat the historical winter-extreme record as roughly
representative, without an assumed intensification the science doesn't yet support.

---

## 5. Weather-station methodology — a three-category framework, refined twice by direct user input

**This section's own framework changed materially over the course of the conversation, and both
changes are recorded here rather than only the final version, since the reasoning matters as much as
the conclusion.**

### 5a. Initial framing (superseded): find a station that stayed rural, to isolate the "true" climate
signal from urban-heat-island (UHI) contamination.

### 5b. Reconsidered (direct user correction): population centers are where the people — and their
air conditioners — actually are. For an energy-demand project specifically, a station that became
*more* urban/suburban over time is not contaminated data to filter out; it is capturing exactly the
compound signal (background climate warming + local development-driven warming) that actually drives
demand growth. UHI-causing development and demand-driving development are not two separate
phenomena to disentangle — they are the same underlying growth process viewed from two angles.

### 5c. Final, three-category framework (direct user refinement, this turn): rather than choosing
one station type, use multiple categories for different, complementary purposes:

| Category | Purpose | What it isolates |
|---|---|---|
| **Stayed rural** | Baseline/floor | Pure background climate-change signal — what happens even where no local development occurs |
| **Already-populated, stayed populated** | Established-UHI reference | Background warming + an *already-mature* urban heat island, without a newly-intensifying component |
| **Rural-to-urban transition (e.g., Sterling)** | Most directly demand-relevant | Background + a *newly emerging* heat island — exactly where this project's own demand growth is concentrated |

**Rationale for why all three matter together**: having all three lets a future projection
decompose expected warming into components — how much will happen regardless of further local
development (category 1, a floor that applies everywhere) vs. how much is specifically tied to
continued urbanization (categories 2 vs. 3, showing the difference between a heat island that's
already fully formed and one still actively intensifying). For Loudoun/Data-Center-Alley
specifically, where background warming and rapid local development are both happening
simultaneously, this decomposition is exactly what's needed to project forward defensibly rather
than conflating the two effects into one unexplained trend.

### Candidate stations identified so far

**Category 3 (rural-to-urban transition) — Sterling, VA, station confirmed AND trend now computed
directly from real data (updated 2026-08-24, following user upload to Project KB)**:
- Station: Weather Forecast Office Sterling, VA. GHCND:USC00448084. 38.9764°N, -77.4869°W, elevation
  87.8m. Confirmed as an exact match against the file the user uploaded (`SterlingVAWeather1977
  2026.csv`, 17,811 rows, station/name/lat/lon all identical to the NOAA metadata already confirmed).
- Period of record: **September 1, 1977 - August 21, 2026** (~49 years). 1977 and 2026 excluded from
  the annual trend below as partial years (1977 starts Sep 1; 2026 ends Aug 21, missing the tail of
  peak heat season, which would artificially depress that year's count).
- **Days ≥95°F per year, 1978-2025 (48 full years), computed directly**:

| Period | Avg days ≥95°F/yr |
|---|---|
| 1978-1987 | 4.80 |
| 1988-1997 | 6.70 |
| 1998-2007 | 7.90 |
| 2008-2017 | 7.50 |
| 2018-2025 | 8.38 |

  Linear trend: **+0.715 days/decade** (fitted value ~5.3 days at 1978, ~8.7 days at 2025) — roughly
  a 75% increase in the decadal average from the earliest decade to the most recent. Full-record
  mean: 7.00 days/yr — within the VCA's own statewide 0-25 day range (Section 4), a useful sanity
  check though not a direct apples-to-apples comparison (single station vs. statewide average).

  **Insight**: the trend is real but genuinely noisy year-to-year, not a smooth climb — 2010 had 24
  days (the single highest year in the record); 2017, seven years later, had zero; 2024 had 21 days
  (second-highest, and recent). This volatility should be preserved directly, not smoothed away —
  any single year says little on its own.

  **Rationale for a suggestive, not proven, local-development marker**: Dulles Town Center (a real,
  dateable suburban-development marker in Sterling itself) opened in 1998, and the 1998-2007 decade
  shows a real step-up from the prior one (6.70 → 7.90 days/yr). Consistent with, but not proof of, a
  local-development contribution layering on top of the broader statewide warming trend (Section 2's
  own WBGT +0.29°F/decade finding) — a single coincidental timing observation, not a demonstrated
  causal link.

  **Tradeoff/known gap**: this trend cannot yet be decomposed into "background climate change" vs.
  "local Sterling-specific development" components without the Category 1 (stayed-rural) comparison
  point — Sterling alone shows total warming, both effects combined. That decomposition is the
  concrete next step once Pennington Gap's own station data is obtained.

  **Data file saved**: `sterling_days_ge_95F_by_year_1978_2025.csv` (in this project's own working
  directory) — the full annual series, for reuse in future plotting or comparison work without
  needing to reprocess the raw file again.

**Category 1 (stayed rural) — Pennington Gap, VA, station-confirmed AND trend computed, with a real
data-quality issue caught and corrected mid-analysis (2026-08-24)**:
- Town in Lee County, far southwest Virginia. One of the VCA's own 10 named reference climatology
  stations. Population has declined, not grown (peak 1,946 in 1990; ~1,558-1,624 as of 2024-2026, a
  ~20% decline, still declining at -0.51%/yr) — officially classified **0.0% urban** by the U.S.
  Census Bureau, a direct verified designation, not an inference from population size. Tiny,
  geographically-constrained footprint (1.69 sq mi, hemmed in by Appalachian terrain) that has not
  expanded; high poverty rate (56-59%) consistent with no meaningful development pressure over the
  period.
- Station: USC00446626, Pennington Gap, VA. 36.7586°N/-83.0105°W. Record extends back to **1934**
  (longer than the other four stations, which all start 1977) — matched to the same 1978-2025 window
  for direct comparability.
- **Located in PJM's AEP zone, not DOM** (direct user-provided context) — worth flagging directly:
  unlike Sterling/Richmond/Norfolk (all DOM zone), Pennington Gap's own weather trend isn't tied to
  Dominion's own load/price dynamics the same way — but AEP has already been a relevant comparison
  utility throughout this project (the Ohio DCT tariff precedent, the load-shape comparison in
  `Dominion_Zone_Load_Shape_and_LMP_Analysis.md`), so the zonal difference is a real caveat, not a
  disqualifying one.

  **A serious data-quality issue caught before it distorted the headline finding, not glossed over**:
  initial processing (naively reindexing missing years to 0) produced a "2008-2017: 0.00 days/yr"
  figure. Checking actual coverage-per-year revealed **nine consecutive years (2011-2019) with ZERO
  TMAX readings** at this station, plus four more years with substantial gaps (1995, 1996, 1998,
  2010) — 13 of 47 years (28%) with insufficient coverage. The "0.00" figure was an artifact of a
  near-decade-long data blackout being silently treated as "zero hot days," not a real finding.
  **Corrected** by restricting to the 34 years with adequate coverage (≥300 of ~365 days) rather than
  zero-filling the gap.

  **Corrected trend: -0.219 days/decade** (mean 2.24 days/yr, min 0, max 20 in 1988) — down in
  magnitude from the uncorrected -0.459, but same direction. Even this corrected figure leans on
  decade-buckets as thin as n=2 valid years in the worst-covered stretch (2008-2017); the full
  34-year linear trend is the more reliable summary statistic than any single decade average here.

  **Rationale for why the corrected, smaller-magnitude trend is actually more credible, not less**:
  -0.219 days/decade is consistent with the VCA's own statewide characterization of historical "very
  hot days" as only a small, low-confidence trend — a truly rural station showing flat-to-slightly-
  negative is plausible, not surprising, given that characterization.

  **Data files saved**: `pennington_gap_days_ge_95F_by_year_1978_2025.csv` (original, flawed
  zero-filled version, kept for reference) and
  `pennington_gap_days_ge_95F_by_year_1978_2025_CORRECTED.csv` (valid years only — this is the one to
  use for any future work).

**Category 2 (already-populated, stayed populated) — Richmond and Norfolk, station-confirmed AND
trend computed directly (updated 2026-08-24, following user upload)**:
- Stations: Richmond International Airport, VA (USW00013740, 37.51154°N/-77.32338°W) and Norfolk NAS
  (Naval Air Station), VA (USW00013750, 36.93746°N/-76.28926°W). Both confirmed from
  `RichmondAirportNorfolkNavalAirStation19772026.csv` (34,617 rows combined, two stations in
  long/stacked format). Both cover the identical Sep 1977-Aug 2026 period as Sterling, processed with
  the identical methodology (1977/2026 excluded as partial years).
- **Days ≥95°F per year, 1978-2025, both stations**:

| Station | 1978-87 | 1988-97 | 1998-2007 | 2008-17 | 2018-25 | Full mean | Trend (days/decade) |
|---|---|---|---|---|---|---|---|
| Norfolk NAS | 8.80 | 12.20 | 6.00 | 11.80 | 7.75 | 9.38 | **-0.083** |
| Richmond Int'l | 15.70 | 12.40 | 13.10 | 15.30 | 13.25 | 13.98 | **-0.177** |
| *Sterling (Cat. 3, for comparison)* | *4.80* | *6.70* | *7.90* | *7.50* | *8.38* | *7.00* | ***+0.715*** |

  **Insight**: both already-established urban stations show flat-to-slightly-negative trends over the
  full record, consistent with Richmond and Norfolk having already had their own urban-heat-island
  effect largely "baked in" by the start of the record in 1977, so their 48-year trend reflects
  mostly the background climate signal.

  **Tradeoffs and honest caveats, not glossed over**: (1) noise is larger here than at Sterling —
  Richmond ranges 0-40 days across the record, Norfolk 0-27 — and Richmond's own "decline" is not
  monotonic (2008-2017 at 15.30 is nearly as high as the first decade's 15.70); the net negative
  slope is real but driven by a noisy series, not a smooth decline. (2) **A positive data-quality
  cross-check**: Richmond's single highest year (40 days, 2010) and Sterling's single highest year
  (24 days, 2010) are the same year — consistent with a real, shared regional heat-wave event
  affecting both stations independently, not a data artifact at either one.

  **Data files saved**: `richmond_international_airport_days_ge_95F_by_year_1978_2025.csv` and
  `norfolk_nas_days_ge_95F_by_year_1978_2025.csv`.

**Category 4 (new — stable, already-settled, minimal ongoing development) — Suffolk Lake Kilby, VA,
station-confirmed, clean data, and directly extends the framework (2026-08-24)**:
- Station: USC00448192, Suffolk Lake Kilby, VA. 36.7297°N/-76.6015°W. Record extends back to **1948**.
  Data quality genuinely good — no substantial coverage gaps (max 10 missing days in any single year).
- Direct user description: "an old neighborhood on the outskirts of Suffolk, VA, with very little
  additional development nearby" — distinct from all three prior categories: not open-countryside
  rural (Pennington Gap), not a major urban center (Richmond/Norfolk), and not rapidly transforming
  (Sterling) — an established, low-density residential area that has remained stable.
- **Trend: -1.218 days/decade** (matched window, mean 5.67 days/yr) — the strongest-magnitude
  negative trend of all five stations.
- **Rationale for why this strengthens, not just adds to, the overall pattern**: an area that's
  already established but not actively transforming shows the same flat-to-declining signature as
  Richmond and Norfolk, not Sterling's growth — a fourth, independent confirmation of the same
  underlying logic from a genuinely different kind of location (small, old neighborhood rather than a
  major metro area).
- **Data file saved**: `suffolk_lake_kilby_days_ge_95F_by_year_1978_2025.csv`.

### 5d. Time-of-observation bias — a real, material qualification on the decomposition below (raised directly by the user, confirmed in the data, 2026-08-24)

**Direct user question, well-founded and confirmed**: does the data indicate when readings were
taken, given that a station shifting its observation time can produce a spurious trend unrelated to
actual climate? Checked directly rather than assumed either way — the answer is yes, the data does
indicate this, via the `TOBS_ATTRIBUTES` field's final comma-separated value (an HHMM time code),
and the finding is real and material.

**Observation-time history, extracted directly from each file**:

| Station | Observation time history |
|---|---|
| Sterling | 0900 (1977-1997) → 0700 (1998-2018) → 2400 (2018-present) |
| Pennington Gap | **1700** (1948-1990) → **0700** (1995-2010) → 0800 (2020-present) |
| Suffolk Lake Kilby | 2400 throughout (1948-2026) — no shift |
| Richmond / Norfolk | No TOBS field present at all (both are automated, airport-class USW-prefix stations); their own attribute fields carry no time code, consistent with (though not full proof of) automated equipment without the observer-visit-time dependency that creates this bias in the first place |

**Rationale for why this matters, and why it matters MOST for Pennington Gap specifically**: the
well-documented mechanism (Karl et al. 1986 and subsequent NOAA adjustment literature) is that an
**afternoon** observation time tends to produce a **warm** bias relative to other times (a hot
afternoon's peak can effectively get counted toward two consecutive daily readings before the
thermometer resets), so a shift **from afternoon to morning** produces an artificial **cooling**
step in the raw record — unrelated to actual climate. Pennington Gap shows exactly this pattern: a
5pm (afternoon) observation time for its first 42 years, shifting to 7am (morning) in the
mid-1990s — and lining this up against the already-computed decadal trend (Section 5, Category 1)
shows a steep drop (2.80 → 3.43 → 0.44 → 0.00 → 3.33 days/yr) that coincides suspiciously well with
the observation-time shift, not necessarily with anything climatic. Sterling's own shifts (9am→7am,
neither the "problematic" afternoon time, followed by a shift to midnight-based/likely-automated
readings) are less concerning. Suffolk Lake Kilby is clean — a single, unchanged observation time for
the full 78-year record — which if anything strengthens confidence in its own -1.218 days/decade
result specifically, since it's the one station in this set with zero observation-time confound.

**Tradeoff/honest limitation**: this project does not have NOAA's own formal TOB-adjustment algorithm
available to properly correct for this — the confound can be identified and its likely direction
reasoned about, but not cleanly removed with confidence. This is a real gap, not resolved here.

**A precision worth stating explicitly, since a plain-language summary of this section risks losing
it (2026-08-24)**: the mechanism above is NOT "7am is simply a cooler moment than 5pm, so the
reading is lower." TMax is not the temperature at the observation moment — it is the maximum over
the ~24 hours since the thermometer was last reset (TOBS, a separate field, is the temperature *at*
the observation moment). The actual mechanism is specifically about reset timing relative to the
diurnal cycle: an afternoon reset sits near the daily peak, so a hot afternoon's lingering warmth
just after reset can get captured as part of the *next* day's max too — a single real heat event
partially double-counted across two consecutive calendar-day readings. A morning reset sits near the
daily low, where no equivalent double-counting risk exists for hot afternoons. This distinction
matters for a further reason: the bias is concentrated specifically around extreme-heat-event
double-counting, not a uniform offset applied evenly across all days — meaning it plausibly affects
an "extreme-heat-day count" metric (exactly what this entire Section 5 analysis measures) more than
it would affect something like annual mean temperature, making the confound more relevant to this
specific analysis, not less.

### 5e. A further correction — "four stations agree" overstated the evidence, caught by direct user challenge (2026-08-24)

**Context**: after 5d above was written, a plain-language summary of it to the user stated "four
independent stations (Pennington Gap, Suffolk Lake Kilby, Richmond, Norfolk) all agree Sterling
shows real excess warming beyond background." The user directly challenged this, pointing out that
each of the four had changing observation times undermining their use as clean baselines. Checked
precisely against what 5d above actually established, station by station, rather than either
defending the summary or fully conceding the challenge:

| Station | Actually verified? |
|---|---|
| Pennington Gap | **Confirmed real shift** (1700→0700→0800) — agreement is genuinely compromised, as 5d already established |
| Suffolk Lake Kilby | **Confirmed NO shift** (2400 throughout) — the user's claim does not hold for this specific station; this remains a genuinely clean, positive verification, not an assumption |
| Richmond | **Not verified either way** — the "automated, no TOB confound" claim in 5d's own table above was an inference from the absence of a TOBS column, never independently confirmed against the station's actual equipment history |
| Norfolk NAS | **Not verified either way**, same reason |

**A near-miss caught while attempting to verify Richmond/Norfolk directly, disclosed rather than
silently avoided**: a search for their equipment history nearly surfaced information about a
different station — "Norfolk International Airport" (GHCND:USW00013737) — which is NOT the "Norfolk
NAS" station (GHCND:USW00013750) actually used throughout this analysis. Caught before conflating
the two; the search did not resolve Norfolk NAS's or Richmond's own actual equipment-transition
history, which remains a genuine, unresolved gap.

**Honest, corrected evidentiary assessment, replacing the overstated "four stations agree"
framing**: only ONE station — Suffolk Lake Kilby — is both positively confirmed TOB-clean and still
shows the same flat-to-negative direction as the other three. Pennington Gap's own agreement is
compromised by a known, real confound. Richmond and Norfolk's own reliability is genuinely unknown
— neither confirmed clean nor confirmed compromised. This is meaningfully weaker support for the
decomposition's own directional claim than "four independent stations converge" suggested. The
honest framing: one clean station agrees with the direction; one compromised station also happens to
agree, which is suggestive but not dispositive on its own; two stations remain unverified either way.
Sterling's own excess-warming finding remains plausible on this evidence, but should not be described
as resting on four-way independent convergence — it rests more precisely on one clean data point
(Suffolk Lake Kilby) plus directional consistency from stations whose own reliability has not been
fully established.

**Direct, material qualification on the decomposition below**: the +0.934 days/decade "Sterling
local excess" figure relies on Pennington Gap's -0.219 days/decade as the true background reference.
If a meaningful share of that -0.219 is a TOB artifact rather than a real trend — which the
suspicious timing above suggests is plausible — the true background trend could be closer to flat,
which would mean Sterling's actual local-development excess is SMALLER than +0.934, not larger. The
decomposition table below is retained for its directional value (Sterling still very plausibly shows
real excess warming relative to a genuinely rural area) but its precise magnitude should now be read
as an upper-bound estimate, not a settled figure, pending either a proper TOB adjustment or a
second, observation-time-stable rural station as a cross-check.

### The completed decomposition — Sterling vs. rural background, qualified by 5d and further corrected by 5e above

With Pennington Gap's corrected trend available, the decomposition this framework was built toward
can be computed — **read as an upper-bound estimate given the TOB-bias qualification in 5d, and
resting on weaker cross-station support than earlier drafts of this file claimed (5e), not a settled
figure**:

| | Trend (days/decade) |
|---|---|
| Sterling (total: background + local) | **+0.715** |
| Pennington Gap, corrected (background — likely includes some TOB artifact) | **-0.219** |
| **Implied local/development excess (upper bound)** | **+0.934** |

**Insight, stated with the corrected evidentiary weight per 5e**: Sterling's own warming trend
plausibly exceeds what a true rural background shows, but this should not be described as resting on
four-way independent convergence. Precisely: Suffolk Lake Kilby (positively confirmed TOB-clean)
independently shows the same flat-to-negative direction — one genuinely clean data point in
agreement. Richmond and Norfolk's own reliability is unverified, not confirmed either way. Pennington
Gap's own agreement is compromised by a known, real TOB confound and should not be counted as
independent support. What's genuinely uncertain now includes not just the precise size of Sterling's
excess, but the strength of the cross-station evidence for its direction — real, but resting on one
clean station plus unverified ones, not four independent confirmations.

**The full five-station picture, a clean 4-vs-1 pattern in raw trend direction — though see 5e above for why this should not be read as four independently-reliable confirmations**:

| Station | Category | Trend (days/decade) |
|---|---|---|
| **Sterling** | Transitioning (rural→suburban) | **+0.715** |
| Richmond Int'l | Established urban | -0.177 |
| Norfolk NAS | Established urban | -0.083 |
| Pennington Gap (corrected) | Stayed rural | -0.219 |
| Suffolk Lake Kilby | Stable, already-settled | -1.218 |

Four stations show flat-to-negative raw trends against Sterling's clear positive one — but per 5e
above, this should be read carefully: only Suffolk Lake Kilby is independently confirmed reliable
for this purpose. The pattern is suggestive, not a confirmed four-way convergence — a meaningfully
more honest framing than describing it as a strong multi-station confirmation.

**Tradeoffs and remaining honest caveats**: (1) n=1 for the "actively transforming" category — still
only Sterling represents this type; a second transitioning station (if one existed with a comparably
clean record) would meaningfully strengthen confidence in the +0.934 excess figure specifically. (2)
Individual-station trends remain noisy (see each station's own entry above for min/max ranges) — the
cross-station *pattern* is more robust than any single station's own precise slope, though see (4)
below for why that pattern itself is weaker evidence than it first appears. (3) Pennington Gap's own
record, even corrected, has real remaining data-quality limitations (thin decade coverage in
2008-2017 specifically) that a fully rigorous analysis would want to address further, e.g. by
checking whether a nearby, independent rural station shows a similar background trend as a
cross-check. (4) **Per 5e above**: only one of the four "reference" stations (Suffolk Lake Kilby) is
positively confirmed free of observation-time bias — Pennington Gap is confirmed compromised, and
Richmond/Norfolk's own equipment history remains unverified. Treat the cross-station agreement as
suggestive corroboration from one clean station, not as four independent confirmations.

---

## 6. A real, disclosed tooling constraint — fully resolved via direct upload (2026-08-24)

**Insight, stated directly rather than worked around silently**: attempting to retrieve station data
via web tools hit a genuine, hard tool limitation. The web_fetch tool can only retrieve URLs that
already appear in a prior search or fetch result — constructing a parameterized NOAA API query URL
from documented syntax (even copied directly from NOAA's own API documentation) counts as "editing a
seen URL's path" and is rejected. Separately, the bash tool's network access is restricted to a fixed
allowlist of package-manager/code-hosting domains — ncei.noaa.gov is not on that list.

**Resolved for all five stations via direct upload to the Project KB**, the same pattern already
established this session for the LMP and load CSV files: Sterling, Richmond, Norfolk, Pennington
Gap, and Suffolk Lake Kilby were all uploaded directly and confirmed as exact matches to their known
station IDs/coordinates. All five trend computations in Section 5 above were completed directly from
these files — no remaining workaround needed for the current framework.

## 7. Connecting to the guiding question directly — does Dominion's own load forecast account for the climate trend this project has documented?

Prompted by a direct user decision to stop searching for a better downtown-core station and instead
use what the Virginia Climate Center's own peer-reviewed team has already identified, then "see how
that could affect demand." This section is the first direct attempt in this file to connect the
climate-trend groundwork (Sections 1-7) to an actual demand figure.

### 7a. A file-location correction, disclosed directly

Two files needed for this step — `PJM_DOM_ZONE_Hourly_Data.csv` and Dominion's own hourly load
projections file — were initially reported as missing from the project. This was a genuine error on
this project's own part: both files were present in `/mnt/user-data/uploads/` (the location every
other file uploaded during this session, including all five weather stations, has actually lived),
not `/mnt/project/` (the persistent project knowledge base location this project checked first). The
user correctly pointed out both files were visible in the Project KB. Corrected by checking the
right location directly.

### 7b. What the files actually are — forward projections, not historical actuals, which changes the analytical approach

Both files turned out to cover **future years** (`PJM_DOM_ZONE_Hourly_Data.csv`: monthly, 2026-2046;
the hourly file: 2024-2048) — Dominion's own load forecast output, not observed historical load.
This means the originally-planned approach (empirically deriving a CDD-to-load conversion factor by
regressing historical CDD against historical load) is not methodologically valid here — regressing
real historical weather against Dominion's own *forecasted* future load would be circular, since
their forecast already embeds whatever weather assumption underlies their own model, not independent
historical observation.

**Redirected to a more directly useful, and arguably more actionable, question**: does Dominion's
own forecast already account for the climate trend this project has independently documented, or
does it assume weather stays fixed going forward?

### 7c. Finding: Dominion's own forecast uses a fixed weather-timing template, scaled by growth — strong, directly-tested evidence, not inference

**Insight**: the annual summer peak occurs at exactly 3:00 PM in every single year, 2024-2048 (25
consecutive years), within a narrow 7-day calendar window (July 18-24) that appears to simply cycle
through the same weekday-of-July pattern rather than represent independently-simulated weather.  The
annual winter peak shows the identical signature: 7:00 AM every year, within a narrow late-January
window (Jan 18-24).

**Rationale for why this is strong evidence, not overinterpretation**: real, independently-varying
weather does not produce this pattern. This project's own Sterling data (Section 5) shows the actual
annual count of ≥95°F days ranging from 0 to 24 across the historical record — genuine year-to-year
weather variability of that magnitude would be expected to produce at least some variation in which
hour and day the annual peak falls on, not the same hour for 25 straight years across two
independent seasons (summer and winter).

**A real nuance, tested directly rather than assumed**: the underlying shape is not perfectly frozen
— normalizing each year's load by that year's own annual mean shows the ratio at a fixed
day/hour drifting from ~1.12 to ~1.52 across the 25 years, consistent with the already-noted
declining peak-to-average ratio (Section 7d below). This is consistent with the load *mix*
evolving (more flat, continuous data-center load as a growing share of the total, an interpretation
directly consistent with this project's own already-established Dominion-zone load-shape findings
in `Dominion_Zone_Load_Shape_and_LMP_Analysis.md`) while the *timing* of when stress occurs stays
locked to a fixed historical template. Precisely: what evolves is how much load exists at that fixed
moment, not when that moment falls or how extreme the weather driving it is assumed to be.

### 7d. The peak-to-average ratio itself, and what it does and doesn't confirm

The annual peak-to-average ratio in Dominion's own projection declines steadily and monotonically
across the full 25-year span: 1.534 (2024) down to 1.253 (2048). Annual peak grows ~75% (17,266 to
30,159 MW) while annual mean grows ~114% (11,257 to 24,072 MW) over the same period — average load
growing faster than peak load.

**Rationale**: this is directly consistent with, and independently corroborates, this project's own
already-established finding that Dominion's zone has an unusually flat load shape driven by
substantial, continuously-running data-center load (`Dominion_Zone_Load_Shape_and_LMP_Analysis.md`,
Section 1) — and further, that Dominion's own forecast expects this flattening trend to continue and
intensify as data-center load's share of total demand grows further. This is a real, useful
cross-validation between this project's own independent load-shape analysis and Dominion's own
published forecast, arrived at through entirely different methods.

**What this does NOT do**: the declining peak/avg ratio is driven by load-mix composition, not by any
apparent climate-warming assumption — as established in 8c above, the fixed-timing signature
indicates weather itself is not being varied or intensified year to year in this forecast.

### 7e. Direct implication for the guiding question, stated plainly

Dominion's own published load forecast appears to assume the timing and pattern of extreme weather
stays fixed at historical-template levels through 2048, while this project has independently and
directly documented that the underlying weather itself is trending (+0.715 days/decade in days
≥95°F at Sterling, Section 5; +88.3 CDD/decade, Section 7f below) in a direction and at Sterling's
own actively-developing location specifically. If real future weather brings more frequent or more
severe extreme-heat events than the fixed historical template embedded in Dominion's own model
assumes, their own published peak-demand figures (e.g., 29,587 MW by 2045) are a plausible
**underestimate**, not a neutral central case — this is the first point in this entire climate-trend
research thread where the groundwork translates into a concrete, directional implication for the
project's own guiding question ("how will this affect demand profiles through 2045").

**Tradeoffs and honest limitations, not glossed over**: (1) this finding is about the *forecast
methodology's own structure* (a fixed weather-timing template), not a precise quantification of how
much Dominion's own peak figures might be understated — translating "Sterling's own weather is
trending X" into "Dominion's own 2045 peak-MW figure should be adjusted by Y" is a further,
not-yet-completed step. (2) It remains possible, though not indicated by anything found here, that
Dominion applies a separate, explicit climate adjustment elsewhere in their own planning process not
captured in this specific hourly-projection file — this file shows what the hourly SHAPE assumes,
not necessarily every input to Dominion's own broader IRP-level MW figures. (3) The CDD/day-count
trends used as the comparison point are Sterling-specific (Section 5's own "Category 3" station,
the most actively-developing location) — appropriate for illustrating the general phenomenon, but a
statewide or Dominion-system-wide weighted figure would be needed for a precise system-level
demand-adjustment estimate.

### 7f. Sterling's own CDD trend, computed directly, as the climate-side half of this comparison

Computed directly from Sterling's own TMax/TMin data (TAvg approximated as (TMax+TMin)/2, a standard
but not perfectly official-NOAA-identical approximation): Cooling Degree Days (base 65°F), 1978-2025.

| Period | CDD/yr |
|---|---|
| 1978-1987 | 962 |
| 1988-1997 | 973 |
| 1998-2007 | 952 |
| 2008-2017 | 1,211 |
| 2018-2025 | 1,298 |

**Linear trend: +88.3 CDD/decade** — notably steeper than the VCA's own statewide figure (19.8-45
°F-days/decade, Section 2). Worth explaining directly rather than treating as a discrepancy: this is
consistent with, not contradictory to, everything already established — the VCA's own figure is a
full-state average since 1951, while this is Sterling specifically since 1978, sitting in the
Northern division (one of the VCA's own two fastest-warming regions) and carrying its own
local-development effect on top (Section 5's own Sterling-vs-Pennington-Gap decomposition). A
single, actively-developing station exceeding the statewide upper bound is exactly what the rest of
this file's own findings would predict.


**Insight, stated directly rather than worked around silently**: attempting to retrieve station data
via web tools hit a genuine, hard tool limitation. The web_fetch tool can only retrieve URLs that
already appear in a prior search or fetch result — constructing a parameterized NOAA API query URL
from documented syntax (even copied directly from NOAA's own API documentation) counts as "editing a
seen URL's path" and is rejected. Separately, the bash tool's network access is restricted to a fixed
allowlist of package-manager/code-hosting domains — ncei.noaa.gov is not on that list.

**Resolved for all five stations via direct upload to the Project KB**, the same pattern already
established this session for the LMP and load CSV files: Sterling, Richmond, Norfolk, Pennington
Gap, and Suffolk Lake Kilby were all uploaded directly and confirmed as exact matches to their known
station IDs/coordinates. All five trend computations in Section 5 above were completed directly from
these files — no remaining workaround needed for the current framework.

---

### 7g. Priority note (2026-08-24, end of session) — this section's own next step deprioritized, not abandoned

Direct user decision: the remaining translation work from 7e's own tradeoffs (converting Sterling's
own weather trend into a specific revised system-wide peak-MW figure) is deprioritized to a lower
tier for now, in favor of picking up D.2 (extended) — school bus V2G next. This mirrors how A.5 (CVR)
was handled earlier in this project (`Scenario3_Scope_and_Gaps.md`): deprioritized explicitly means
not abandoned — the finding in 7c/7e above stands as a real, actionable result on its own, and the
## 8. Summary — where this leaves the guiding question

This file is groundwork, not a final answer to "how will this affect demand profiles through 2045" —
but the groundwork is now substantially more complete than earlier drafts of this file reflected,
and Section 7 above is the first point in this file that connects it to a concrete, actionable
implication rather than climate evidence alone.

**The single most directly relevant finding in this file (Section 7)**: Dominion's own published
2024-2048 load forecast uses a fixed weather-timing template (the annual summer peak lands at
exactly 3:00 PM and the winter peak at exactly 7:00 AM, every single year for 25 consecutive years,
within narrow calendar windows) scaled up by an annual growth factor — not a model that varies or
intensifies weather year to year. Since this project has independently and directly documented that
the underlying weather itself IS trending (Sterling's own +0.715 days/decade in extreme-heat days;
+88.3 CDD/decade), Dominion's own published peak-MW figures for 2035/2040/2045 are a plausible
underestimate of real future peak demand, not a neutral central case — the first concrete,
directional answer this file provides to its own guiding question, even though translating it into
a specific revised MW figure remains a further, not-yet-completed step (Section 7e's own tradeoffs).

**What's established on the climate-trend side itself**: (a) summer heat evidence is real, quantified, and one-directional statewide
— supports treating historical extreme-heat frequency as a floor for future checkpoints; (b) winter
cold evidence is genuinely mixed — does not support a symmetric "more severe" adjustment; (c) the
weather-station framework is now populated across all four categories with real, computed data, and
the core decomposition is directionally plausible, though both its precise magnitude and the
strength of its cross-station support carry real, disclosed caveats (Sections 5d and 5e): Sterling
(the one actively-transforming station) shows a clear positive trend (+0.715 days/decade), while
Pennington Gap (true rural baseline, corrected for a real 9-year data gap AND carrying a separate,
confirmed time-of-observation bias from a 1990s afternoon-to-morning shift), Richmond, Norfolk
(both unverified for observation-time stability), and Suffolk Lake Kilby (the one station positively
confirmed free of this confound) all show flat-to-negative trends. The implied local/development
excess at Sterling specifically is **+0.934 days/decade, read as an upper bound, not a settled
figure** — the direction (Sterling shows real excess warming) has genuine but more limited support
than earlier drafts of this file claimed: one clean station (Suffolk Lake Kilby) agrees, one
compromised station (Pennington Gap) also agrees but cannot be counted as independent confirmation,
and two stations (Richmond, Norfolk) remain unverified either way — not four independent
agreeing, but the precise magnitude is uncertain pending a proper TOB adjustment.

**Direct implication for the guiding question**: extreme-heat-day growth in Virginia appears
concentrated in actively-developing areas, not uniform statewide — meaning continuing-to-grow
corridors like Loudoun County (still expanding, notably with data-center construction) plausibly
face a worse extreme-heat trajectory through 2045 than already-mature areas, which the 4-of-5
stations here suggest may have largely exhausted their own development-driven intensification. This
is a real, evidence-based basis for treating future demand-relevant heat exposure as
location-dependent rather than applying a single statewide adjustment factor uniformly across all of
Scenario 3's own geography — though any specific magnitude carried into a demand model should be
treated as a defensible upper bound, not a precise figure, given Section 5d's own findings.

**What remains genuinely open**: (a) how to actually translate a "local excess, upper-bounded at
+0.934 days/decade" figure into a demand-model adjustment for 2035/2040/2045 checkpoints — this file
establishes the empirical basis but does not yet specify the translation method, and a proper TOB
adjustment (or a second, observation-time-stable rural station) would meaningfully sharpen this
figure; (b) whether this same transitioning-vs-stable pattern holds in other actively-developing
parts of Dominion's territory beyond Sterling specifically (a second transitioning-station comparison
would strengthen confidence
materially, given n=1 for that category currently); (c) the winter-cold side of the guiding question
has no equivalent station-level analysis yet — this entire Section 5 exercise covered summer heat
only.
