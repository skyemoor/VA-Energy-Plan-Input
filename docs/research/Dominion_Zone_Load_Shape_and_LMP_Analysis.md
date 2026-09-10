# Dominion Zone Load-Shape and Real-Time LMP Analysis

Compiled 2026-08-24, arising directly from the A.2 (extended) avoided-cost discussion (entries #82,
#84). Two data sources analyzed: (1) PJM-wide hourly metered load
(`PJM-hrl_load_metered-Aug-1-2024_July-31-2025.csv`, user-uploaded), and (2) real-time hourly LMPs
for Dominion-zone locations (Loudoun, Tysons, Richmond/"Twelfths", VA Beach — user-uploaded, plus an
initial APS-zone proxy check before the real DOM-zone files were located).

**Standing instruction from this point forward (direct user request, 2026-08-24): all findings
below are written with insight, rationale, and tradeoffs made explicit, not left implicit.**

---

## 1. Load-duration-curve analysis — peak/avg ratio is a misleading proxy for curtailment value

**Insight**: a lower peak-to-average load ratio does NOT mean more hours near peak (a "broad
plateau"). Across all 21 PJM zones checked, the correlation between peak/avg ratio and hours spent
≥90% of that zone's own peak is **-0.75** — the opposite of the naive assumption. Dominion (ratio
1.662) has only 97 hours/year ≥90% of its own peak — among the fewest of any zone checked, despite a
relatively low ratio. AEP (ratio 1.535, even lower than Dominion's) has 215 such hours — more than
double.

**Rationale**: a low peak/avg ratio can arise from two genuinely different underlying causes that
look identical on this single summary statistic:
- A high, steady baseload lifts the average without broadening the peak — the peak stays sharp and
  narrow. This is Dominion's own pattern, plausibly driven by its substantial, continuously-running
  data center load (already extensively documented elsewhere in this project's own A.7 research) —
  a load type that runs near-constantly rather than cycling with weather/occupancy, which raises the
  floor/average without adding new peak-hour stress.
- A genuinely broad, sustained high-demand period spreads the peak over more hours. This is closer
  to AEP's own pattern.

**Tradeoff**: peak/avg ratio is cheap to compute and easy to communicate, but risks a materially
wrong conclusion if used alone to judge curtailment value or to select a "comparable" utility for
benchmarking (as this project's own entry #84 discussion initially did, pairing Dominion with AEP on
ratio similarity alone before this analysis qualified that pairing). The fuller hours-near-peak
profile is more accurate but requires full hourly load data and materially more computation — worth
the cost specifically when the conclusion (e.g., which utility is the "closest comparable") carries
real weight, as it does here.

---

## 2. Real-time LMP analysis — avoided energy cost, a third independent line of evidence

**Insight**: avoided ENERGY cost (distinct from, and additive to, entry #82's avoided CAPACITY
cost) substantially exceeds Dominion's flat $36/kW/yr incentive. Using the actual top-97-hour prices
(97 chosen to match the load-duration-curve threshold above, for direct comparability) at five real
DOM-zone locations, September 2025-August 2026:

| Location | N=97 avoided energy cost | As % of $36/kW/yr |
|---|---|---|
| Tysons | $136.29/kW | 378.6% |
| Loudoun | $126.06/kW | 350.2% |
| Twelfths (Richmond) | $93.18/kW | 258.8% |
| VA Beach | $93.08/kW | 258.6% |
| Southill | $90.98/kW | 252.7% |
| **Average across all 5** | **$107.92/kW** | **299.8%** |

An initial check used PJM's Mid-Atl/APS zone as a proxy (before the real DOM-zone files were
located) and found $68.98/kW (191.6%) — every real DOM-zone location priced HIGHER than that proxy,
not lower.

**Rationale**: this is directionally consistent with, and now directly confirms in the energy
market, something already established in this project's own capacity-market research — Dominion's
own zone cleared at a real premium to the PJM-wide average in the 2025/2026 BRA ($444.26 vs
$269.92/MW-day). The same underlying scarcity/constraint dynamics that produce that capacity premium
plausibly also produce the energy-price premium found here. This strengthens confidence that the
finding is real and structural, not an artifact of which specific benchmark got chosen — three
independent lines of evidence (peaker capex in entry #82, cross-state rates in entry #84, and now
real-time LMPs) all point the same direction.

**Tradeoff, stated directly rather than left as a footnote**: every figure above is a
**perfect-foresight upper bound**, not a realistic expected value. No real curtailment program calls
the exact top-97 hours of the year with hindsight precision — Dominion's own program is triggered by
forecasted stress (temperature, day-ahead load forecasts), not by knowledge of actual real-time LMPs
after the fact. A real program captures some fraction of this value, not all of it, and that fraction
depends entirely on how well forecast-based calling aligns with when prices actually spike. This
number is useful as a ceiling on the avoided-energy-cost argument, not as a proposed replacement
value for the $36 rate.

---

## 3. Location-timing split — the genuinely new, actionable finding

**Insight**: extreme-price events split by SUB-LOCATION within Dominion's own zone, not just by
utility or state — something neither the aggregated DOM-zone load data (Section 1) nor a single-zone
LMP proxy could reveal on its own, since both treat the zone as one undifferentiated whole.
- **Loudoun and Tysons** (Northern Virginia, in/near Data Center Alley): top-price hours cluster
  entirely in a **July 2-3, 2026 summer heat event**.
- **Twelfths (Richmond) and VA Beach** (outside that corridor): top-price hours cluster instead in a
  completely different event — a **late January/early February 2026 winter cold snap** (Jan 31-Feb
  9). No overlap with the Northern Virginia locations' own top event at all.

**Rationale**: plausibly reflects genuine geographic/climatic diversity within Dominion's own
service territory, compounded by Northern Virginia's own concentrated, continuously-running data
center load (already established in Section 1 as a likely driver of that region's own flatter,
baseload-heavy profile) producing a different peak-driver profile than the more
weather-/occupancy-driven Richmond/VA Beach locations. Not confirmed as causal — a reasonable,
evidence-consistent hypothesis, not a proven mechanism.

**Quantified, not just asserted**: checking how many of each location's own top-20 highest-price
hours fall inside Dominion's existing, already-documented curtailment call windows (summer 2-9pm,
winter 6-11am/5-10pm):

| Location | Top-20 hours inside existing call windows |
|---|---|
| Loudoun | 17/20 (85%) |
| Tysons | 17/20 (85%) |
| Twelfths (Richmond) | 14/20 (70%) |
| VA Beach | 15/20 (75%) |

**Tradeoff — the core, actionable design question this surfaces**: Dominion's existing uniform,
statewide call window is simpler to administer and communicate to customers than a
location-differentiated one, but measurably under-captures value at the non-Northern-Virginia
locations (70-75% coverage vs. 85% at Loudoun/Tysons). A more granular, location-specific call-window
design could capture more of the available value at Richmond/VA Beach specifically, but at the cost
of real added program complexity (more rules to design, file with the SCC, and communicate) and
potential customer confusion if different DOM-zone customers face different rules depending on where
they sit. Not a small-vs-large tradeoff with an obvious answer — worth flagging as a genuine open
design question rather than asserting the location-differentiated approach is simply "better."

### 3a. A fifth location (Southill) and a refinement of the "no overlap" framing above (added 2026-08-24)

**Insight**: a fifth real DOM-zone location, Southill (a 13kV substation node, user-uploaded), was
checked against the same September 2025-August 2026 window and N=97 threshold. Result: $90.98/kW
(252.7% of the $36/kW/yr flat rate) — the lowest of the five, but only marginally so (6 percentage
points behind VA Beach), not "much lower" as one might guess. Southill slots cleanly into the same
winter-dominated cluster as Richmond/VA Beach (8 of its own top-10 hours fall in the same Jan 31-Feb
9 winter event), a third independent location confirming that cluster rather than creating a new
one.

**A genuine correction to the "no overlap at all" framing directly above**: Southill's own top-10
included one hour (Jan 25, 2026, 9am) not present in the other four locations' own top-10 lists.
Checked directly rather than assumed to be a localized/Southill-specific event: all five locations
show nearly identical prices at that hour ($1,475-$1,552), and the `system_energy_price_rt`
component — a shared, PJM-wide marginal-cost component — is EXACTLY identical ($699.39) across all
five. This confirms the event was zone-wide (arguably system-wide), not localized to Southill. It
only appears in Southill's own top-10 (and not Loudoun/Tysons's) because Loudoun/Tysons's own July
2-3 summer spike was roughly 2x more extreme ($2,900-3,400/MWh vs. ~$1,500/MWh here), crowding this
January event out of their own top-N lists — not because they were unaffected by it.

**Rationale for why this matters, not just a trivia correction**: the more accurate story is that
BOTH regions experience BOTH the summer and winter stress events — each region simply has its own
disproportionately more extreme "signature" event (summer for the north, winter for the
south/east/Southill), which dominates its own top-N list without the other event being absent
entirely. The original "no overlap at all" language (based on a top-5 check only) was a bit cleaner
than the underlying reality.

**Tradeoff this refinement changes for any future call-window redesign work**: a design premised on
"Northern Virginia never needs winter coverage" would be overstated — the region does experience
winter stress, just less severely than its own summer peak, and the existing winter window may
already be capturing a reasonable share of it. The core actionable finding above (85% coverage at
Northern VA vs. 70-75% elsewhere) still holds and is not undermined by this refinement — but the
underlying causal story is better described as "differing relative severity of a shared set of
regional events" than "two entirely separate, non-overlapping storm systems," which is a more
defensible claim to build any future policy recommendation on.

---

## 4. Summary — how these three sections relate to each other and to entries #82/#84

Not three independent findings bolted together — each qualifies or strengthens the others:

- Section 1 (load-duration curves) explains WHY Dominion and AEP, despite similar peak/avg ratios,
  are not as directly comparable as that single statistic suggested — a genuine correction to how
  entry #84's own comparison should be read.
- Section 2 (real-time LMPs) adds a third, independent, market-based line of evidence to entries #82
  (peaker capex) and #84 (cross-state rates) — all three now point the same direction (the $36/kW/yr
  rate looks low relative to what it's meant to approximate), which is stronger evidence than any one
  method alone, since each has different failure modes.
- Section 3 (location timing) is the most operationally actionable of the three — it doesn't just
  say "the rate might be too low," it identifies a specific, fixable design gap (call-window timing)
  independent of the rate-level question entirely.

**Known gap, stated directly rather than silently left out**: this analysis has not been run against
a genuinely representative sample of "typical" (non-extreme) years — the 2025-2026 window analyzed
includes a documented severe July 2026 heat event, meaning the top-N-hour figures above may be
elevated relative to a more typical year. Worth flagging as a real limitation before treating the
311.5% average figure as a stable, repeatable expectation rather than a description of this specific
period.
