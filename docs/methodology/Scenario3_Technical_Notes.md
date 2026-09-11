# Scenario 3 — Technical Notes (Working Document)

*Compiled while the user was offline, per explicit direction ("go ahead").
Every item below is either (a) a factual research finding with clear
sourcing, presented for adoption, or (b) explicitly flagged as a
judgment call requiring the user's own review before being locked in.
Nothing here has been used to run a solve yet — this is preparatory
research toward Scenario 3's build, not a completed result.*

## 1. Flat-panel (rooftop/parking-canopy) solar capacity factor

**Status: researched and proposed, FLAGGED FOR USER REVIEW — not yet
adopted or used in any solve.**

### The question
Scenario 3's 20% distributed solar share (10% rooftop, 10% parking-lot
canopy) is physically different from the 80% utility-scale share this
project's existing solar_cf data represents — this project's own
existing data (Albemarle/Chesapeake/King George county-level PVWatts-
style output) reflects ground-mount arrays at or near optimal tilt.
Rooftop and parking-canopy installations do not achieve the same
capacity factor.

### What "flat-mount" actually means, worth being precise about
Genuinely flat (0°-tilt) panels are uncommon in practice. Commercial
flat-roof and canopy installations typically use shallow racking (10-15°
tilt via ballasted or mechanically-attached systems) — several
independent industry sources describe a well-designed 10-15° array as
landing "within a few percent" of a fully optimal, latitude-tilted
system on a per-panel basis. The larger, more consistent penalty comes
from a different source: rooftop/canopy installations are frequently
laid out in **east-west row configurations** specifically to maximize
panel density on a constrained roof/canopy footprint (tighter row
spacing than south-facing rows require) — trading roughly 10-15% lower
per-panel yield for meaningfully more installed capacity per unit area.
Given Scenario 3's rooftop/parking-canopy segment is explicitly
space-constrained by design, an east-west, density-optimized layout is
a reasonable assumption for at least part of this segment, not a
worst-case edge case.

### Sourced finding: NREL's own Commercial PV vs. Utility-Scale PV benchmarks
NREL's Annual Technology Baseline (ATB) maintains commercial PV as a
category distinct from utility-scale PV specifically because rooftop/
distributed siting "reduces both the potential capacity factor and land
(roof) space that is available for development" compared to utility-
scale (2024 ATB, Commercial PV page). Direct, fetched figures:

- **Commercial PV, U.S. mean**: 15.8% DC capacity factor (2024 ATB,
  first-year-of-operation basis; range 12.7%-19.8% across the 10 GHI
  resource classes used). Commercial PV in the ATB is explicitly modeled
  as a "200-kWDC, flat-roof-mounted system" — directly on point for
  Scenario 3's own rooftop/canopy segment, not an approximation from an
  unrelated category. Inverter loading ratio (ILR): 1.23.
- **Utility-scale PV**: cumulative median AC capacity factor for U.S.
  projects installed 2007-2021 (including fixed-tilt systems) was 24%
  (2024 ATB, Utility-Scale PV page); more recent LBNL data (2025) puts
  the range at 17%-31% depending on region.

**Unit conversion, made explicit rather than left implicit**: commercial
PV's 15.8% figure is DC; utility-scale's 24% figure is AC. Converting
commercial PV to an AC-equivalent basis using its own stated 1.23 ILR:
15.8% × 1.23 ≈ **19.4% AC-equivalent**.

**Resulting ratio**: 19.4% / 24% ≈ **0.81** — rooftop/commercial-scale
PV achieves roughly 81% of utility-scale's capacity factor under this
comparison, a ~19% reduction. This sits within, and is now grounded
by a specific sourced comparison rather than merely bounded by, the
broader ~3-25% range found across general industry sources on tilt/
layout penalties alone.

### Proposed methodology, pending user review
Apply a flat **0.81 multiplier** to this project's existing, blended
three-location solar_cf array to derive a distinct "distributed solar
cf" series for Scenario 3's 20% rooftop/canopy share, while the 80%
utility-scale share continues using the existing, unmodified solar_cf
array. This preserves this project's own real, hourly weather-year
shape (rather than inventing a new one) while applying a defensible,
sourced derating for the physically different siting.

**What this proposal does NOT resolve, flagged rather than assumed
away:**
- The 0.81 ratio is a national average comparison, not Virginia- or
  Dominion-territory-specific. This project's own existing solar_cf data
  is already Virginia-specific (three in-state counties); the 0.81
  derating factor is not.
- Whether Scenario 3's rooftop/canopy segment should be modeled as
  south-facing-shallow-tilt (closer to the "within a few percent"
  finding) or east-west-density-optimized (closer to the "10-15% per-
  panel" finding) changes which end of the sourced range is more
  appropriate — 0.81 is presented as a reasonable single point estimate
  spanning both, not a resolution of which layout Scenario 3 should
  assume.
- Whether this single ratio should apply uniformly to both the rooftop
  and parking-canopy sub-segments, or whether they warrant separate
  treatment (a canopy structure has more layout freedom than a
  building's existing roof shape), has not been considered.

**This entire section is presented as a well-sourced starting proposal,
not a locked-in decision** — flagged explicitly per this project's own
standing practice of not silently locking in judgment-heavy modeling
choices, especially ones affecting a new scenario's core physical build.

**Citation candidates for this finding** (to be added to the citations
tracker once adopted, per this project's "document = citations too"
convention):
- NREL 2024 ATB, "Commercial PV" page: https://atb.nrel.gov/electricity/2024/commercial_pv
- NREL 2024 ATB, "Utility-Scale PV" page: https://atb.nrel.gov/electricity/2024/utility-scale_pv
- Ramasamy et al. (2022), "U.S. Solar Photovoltaic System and Energy
  Storage Cost Benchmarks, With Minimum Sustainable Price Analysis: Q1
  2022," NREL — the underlying commercial PV representative-technology
  source ATB itself cites.


## 2. Genuine price-elastic demand response

**Status: researched, FLAGGED FOR USER REVIEW — substantial genuine
uncertainty in the underlying literature itself, not just in this
project's own modeling choice. Not yet adopted or used in any solve.**

### The question
Per direct user confirmation, Scenario 3's ComEd-style retail rate
design should produce **genuine price-responsive load shifting**, not
the simpler peak-proportional DSM allocation the prior session's own
(differently-defined) "Scenario 3" used. This requires an actual
elasticity or behavioral mechanism connecting the hourly day-ahead/
real-time price signal to real load shift — a genuine methodological
build, not a reuse of existing DSM machinery.

### The literature is genuinely, substantially split — not settled
enough to pick a single confident number
This is worth stating plainly rather than glossing over: unlike the
flat-panel CF question above, where sources converged on a specific,
usable range, price elasticity findings for real-time/hourly pricing
specifically are widely divergent, including one directly contradictory
major finding:

- **Spain's 2015 mandatory residential RTP rollout — the largest-scale
  real-world test available** — found, using expected national wind
  production as an instrument for price (a strong identification
  strategy, not a naive correlation): **"no difference in behavior
  across RTP and non-RTP households"** — essentially zero measured
  price response at scale, for a mandatory (not opt-in) residential
  population.
- Smaller, **opt-in** U.S. residential RTP pilots ("Rethinking real-time
  electricity pricing," and the related "Estimating the Elasticity to
  Real-Time Pricing" study) found enrolled households were
  "statistically significantly price elastic" — but self-selection into
  an opt-in program is a real confound the Spain study's mandatory
  design avoids, and the measured welfare gain was modest ($10/household
  -year in increased consumer surplus). The same study found dedicated
  in-home price-information devices ("Energy Orbs") measurably increased
  elasticity — suggesting genuine response may depend heavily on
  information/engagement tooling, not price exposure alone.
- **Commercial and industrial customers show meaningfully higher
  elasticity than residential**, consistently across sources, due to
  operational flexibility (BEMS, shiftable processes, on-site storage).
  This is directly consistent with the prior-session research already
  in this project's history (the DLC-vs-price-signal literature,
  FERC's historical ~3%-of-peak-demand ceiling on demand response
  generally).

### Follow-up: does automation (smart HVAC, home automation, modern BEMS) change this? (added this session, per direct user question)

**Short answer: the underlying mechanism has genuinely changed in a way
the older studies above could not have captured — but the evidence base
for how much it changes the actual number is itself of a different,
weaker kind than the Spain finding above, and that gap should be stated
honestly rather than papered over.**

The Spain study's own explanation for near-zero response — "low
potential gains or high nonmonetary costs of information acquisition and
behavioral change" — describes a *human* barrier: a consumer would need
to notice the price, remember it, and manually act on it. Automated
response removes exactly that barrier by design. This is a real,
mechanistic reason to expect the Spain finding understates what a
genuinely automation-enabled population would do, not a reason to
distrust the Spain finding itself — it measured what it measured (2015,
manual/informational response) correctly; the question is just whether
it's the right analog for a 2026-and-beyond, automation-heavy population.

**What the literature search actually found, and its real limits:**
- A substantial, active body of academic literature exists specifically
  on automated, price-responsive home/building energy management —
  Althaher, Mancarella & Mutale (2015, *IEEE Trans. Smart Grid*) is a
  foundational, directly-on-point example: an automated HEMS controller
  responding to dynamic price signals across deferrable, curtailable,
  and thermal loads. More recent work extends this with deep
  reinforcement learning (2025) and multi-sector price-elasticity
  matrices disaggregated by customer class (Dec 2025, *ScienceDirect*) —
  directly matching this project's own "split by customer class"
  proposal above, though without a specific number this project has
  independently verified.
- Quantified results exist within this literature — for example, one
  2024 real-time-pricing HEMS optimization study reports 5.7-6.6% cost
  reduction — but **these are simulation/optimization studies
  demonstrating what an automated system can achieve under modeled
  conditions, not large-scale empirical measurements of what actual
  deployed households do**, the same distinction that separates
  "technically possible" from "actually happens at scale." This is a
  fundamentally different evidence type than the Spain study, which
  measured real households' real behavior under a real, mandatory
  program.
- The large-scale, real-world data that does exist for automated
  residential response is overwhelmingly **event-based automated demand
  response (ADR)** — Ecobee's eco+, SCE's Smart Energy/Summer Discount
  Plans, and similar utility programs, where a utility calls a discrete
  event (a handful of times per year, during genuine system stress) and
  enrolled smart thermostats automatically adjust for that specific
  window. Measured results here are real and substantial (20-40% AC
  load reduction during an event, per multiple program-level sources).
  **This is a mechanistically different thing from what Scenario 3's own
  continuous, hourly day-ahead/real-time tariff would invoke** — a
  handful of coordinated, utility-triggered events per year is not the
  same claim as automated systems continuously arbitraging against an
  hourly price signal all year round. Both are "automated," but they are
  different mechanisms with different evidence bases, and citing one as
  support for the other would be a real error.

**Net effect on the three options presented above**: this doesn't
resolve the underlying uncertainty so much as relocate it. It provides
a genuine, well-sourced reason to believe option 1 (near-zero,
Spain-anchored) is likely too conservative for an automation-enabled
population going forward — the mechanism the Spain study's own
authors identified as the probable cause of non-response is
substantially weakened by automation. But it does not hand this project
a specific, empirically-validated replacement number for genuine hourly
price-responsiveness specifically, the way the Spain study did for
manual response. **This remains presented as informed judgment, not a
resolved figure** — the honest state of the evidence is "automation
likely raises the achievable response meaningfully above the Spain
finding, direction confirmed by mechanism, magnitude not yet
pinned down by evidence of the same rigor."

**Citation candidates, this subsection:**
- Althaher, S., Mancarella, P. & Mutale, J. (2015), "Automated Demand
  Response From Home Energy Management System Under Dynamic Pricing and
  Power and Comfort Constraints," *IEEE Trans. Smart Grid* 6(4),
  1874-1883.
- ScienceDirect (Dec 2025), "A novel modeling framework for demand
  response-based energy management systems in smart electricity
  markets" — the price-elasticity-matrix-by-customer-class methodology.
- Program-level sources for event-based ADR results (Ecobee eco+, SCE
  Smart Energy Program) — directionally useful, not independently
  verified to this project's usual primary-source standard; flagged as
  such.

### Cross-utility DA/RT and TOU pilot evidence (added 2026-09-02, direct user request)

Direct follow-up to the automation question above: real-world DA/RT and TOU pilot results
from ComEd, NY, CA, HI, and MD/DC, checked directly rather than assumed. **The honest
finding: genuinely mixed, not a resolution of the elasticity decision.**

- **ComEd (IL) — a new, separate program, not the same one already cited above.** ComEd is
  rolling out "Delivery Time-of-Day" (DTOD) in 2026 — a fixed four-period rate, not
  continuous hourly pricing — following a 4-year pilot that found **6.5-9.7% peak-demand
  reduction each summer**. This is distinct from ComEd's own existing "Hourly Pricing"
  program (true real-time, ~1% residential enrollment since 2007, already cited above and
  still accurate per a March 2025 source) — the two should not be conflated; DTOD's real
  result says something about TOU-style response, not about true hourly/real-time uptake.
- **Hawaii — a real, recent, and directly disconfirming result.** HECO's "Shift and Save"
  pilot (~16,000 randomly-selected residential/commercial customers, 1:2:3
  daytime:overnight:evening-peak price ratio, closed to new enrollment Feb. 2025) found
  **no statistically significant change in customer energy usage** in its first six months
  of real data (Jan-June 2024), with only 54% overall satisfaction. This is a genuine,
  recent (not Spain-2015-era) empirical result strikingly similar to the Spain finding
  despite nearly a decade passing and presumably more automation being available — a real
  counterweight to the automation-improves-response hypothesis, not just an old data point.
- **PEPCO/DC (MD-adjacent) — the strongest empirical support found for the automation
  premise, but old.** The PowerCentsDC pilot (2008-2010) found consumers reduced summer
  peak demand by **up to 50%**, "with the greatest reductions occurring when dynamic prices
  were combined with automated air conditioner control via smart thermostats" — real,
  measured behavior, not simulation. Caveat: 15+ years old, and its mechanism (Critical Peak
  Pricing/Critical Peak Rebate, plus a separate Hourly Pricing group) is event-based for two
  of its three groups, not a continuous hourly signal the way Scenario 3's own design is.
- **A well-established meta-analysis worth adding as a fourth reference point**: Faruqui &
  Sergici find 3-6% peak reduction for TOU rates broadly and 13-20% for Critical Peak
  Pricing, across many pilots in multiple countries. A related finding (Faruqui, Hledik &
  Palmer, 2012) is that the on-to-off-peak price *ratio* itself is a key driver of price
  response — a design-lever finding independent of automation, worth keeping distinct from
  the automation question this subsection is otherwise about.
- **No clean WA or MD-specific residential DA/RT finding located** (WA's own TOU piloting
  appears commercial-only per what was found; MD's own picture runs through PEPCO above).
  **CA**: a real, recent (2025) SCE dynamic-pricing final evaluation report exists, but no
  clean topline peak-reduction figure was extracted from it — a candidate for a follow-up
  read if a CA-specific number is later needed.

**Net effect on the three options presented above, restated honestly**: this adds real
signal on both sides of the automation question — DTOD and PowerCentsDC support it directly;
Hawaii's own recent, large-sample pilot directly disconfirms it under broadly similar
conditions. It does not resolve which of the three elasticity options to use, and it
specifically does not upgrade "near-zero" to something confidently ruled out — Hawaii's
result keeps that option live even under presumably higher 2024-2025 automation levels than
Spain's 2015 population had.

### A critical distinction the literature itself flags, worth getting right
The NBER working paper on long-run electricity demand dynamics states
directly: *"The elasticity we identify here is fundamentally different
from the elasticity estimated in the real-time pricing literature, which
reflects intra-day substitution patterns as well as any overall
reductions in electricity."* This matters directly for Scenario 3:
**most commonly-cited "residential price elasticity" figures (e.g., EIA/
NEMS: short-run -0.03 to -0.13 in year 1, long-run up to -0.50 at year
30) measure response to a *sustained price-level change* — annual or
monthly demand response to electricity getting structurally more
expensive — not the *intra-day substitution* (shifting load from an
expensive afternoon hour to a cheap overnight hour) that an hourly day-
ahead/real-time tariff actually invokes.** Applying a NEMS-style
sustained-price elasticity to an hourly price-shifting mechanism would
be using the wrong kind of elasticity for the question being asked. The
real-time-specific studies above (Spain, the opt-in U.S. pilots) are the
methodologically correct category to draw from — and they are exactly
the ones showing the widest, most contested range of outcomes, from
"zero" to "modest but real."

### Proposed methodology, pending user review

**Mechanism, to keep this properly linear within the existing LP
framework**: rather than a genuinely endogenous price-demand feedback
loop (which would make the demand series depend on the LP's own
dispatch/price outcome, breaking linearity and creating a circularity
the solver cannot handle directly), propose a **linearized, ex-ante
price-response adjustment**: compute an expected hourly price shape
first (this project already has an hour-of-day synthetic shape,
Appendix A-adjacent), then apply a fixed, pre-computed load-shift
adjustment to the demand series based on that shape — the same basic
approach this project already uses for the existing DSM peak-shaving
allocation, but keyed to price level per hour rather than load level
per hour. This is a disclosed simplification (a "price-informed fixed
shape," not true within-solve elasticity), consistent with how this
project has handled other LP-linearity constraints throughout its
history (e.g., the fixed synthetic hour-of-day price shape already used
elsewhere).

**Elasticity value — genuinely unresolved, three options rather than
one recommendation:**
1. **Adopt something close to zero / minimal**, defensible directly by
   the Spain finding — the largest, most rigorously-identified,
   mandatory-rollout study available, and arguably the most relevant
   given Scenario 3's own rate design would not be voluntary opt-in.
2. **Adopt a modest, opt-in-pilot-consistent value** (something in the
   short-run EIA/NEMS range, e.g. -0.10 to -0.15, while flagging this
   openly as borrowing a sustained-price elasticity for an intra-day
   mechanism, an imperfect substitute given the distinction above but
   the best quantified figure this research turned up).
3. **Split by customer class** — near-zero for the residential share,
   meaningfully higher for the commercial/industrial share, reflecting
   the consistent finding that C&I flexibility is real while residential
   is contested — mechanically more complex (Scenario 3's demand series
   would need a customer-class breakdown it doesn't currently have) but
   arguably the most honest treatment of what the literature actually
   supports.

**This is presented as three defensible options, not a recommendation
locked in during this session** — this decision has more genuine
empirical uncertainty behind it than the flat-panel CF question above,
and deserves the user's own judgment rather than a default pick.

**Citation candidates for this finding:**
- Fabra, Natalia, et al., "The Real-Time Price Elasticity of Electricity"
  (Spain RTP study) — https://nataliafabra.org/wp-content/uploads/2021/01/RTP.pdf
- "Rethinking real-time electricity pricing," ScienceDirect —
  https://www.sciencedirect.com/science/article/abs/pii/S092876551100042X
- EIA, "Price Elasticity for Energy Use in Buildings in the United
  States" (Jan 2021) — https://www.eia.gov/analysis/studies/buildings/energyuse/pdf/price_elasticities.pdf
- NBER Working Paper, "The Long-Run Dynamics of Electricity Demand" —
  https://www.nber.org/system/files/working_papers/w23483/revisions/w23483.rev2.pdf
- EPRI (2007/2008), "Price Elasticity of Demand for Electricity: A
  Primer and Synthesis" — foundational synthesis, referenced across
  multiple other sources found in this search.

## #3 — Scenario 3/4/5 split decisions, confirmed 2026-09-04

**Context**: user is considering splitting the existing Scenario 3 into
three: a new Scenario 3 (EE/DLC/DER/LSRV-DRV, everything except DA/RT
pricing), Scenario 4 (same, plus DA/RT), Scenario 5 (same as 4, plus
data-center-restricted buildout with load flexibility, both TBD). The
decisions below were confirmed for the new, narrower Scenario 3
specifically — not yet applied to Scenario 4 or 5.

**Panel angle (supersedes the earlier CF-ratio framing)**: Scenario 3 is
an hourly model, so the flat annual CF ratio (0.81) and its underlying
layout assumption (shallow-tilt vs. east-west) are no longer the right
question — confirmed moot, not resolved. What matters instead is the
actual panel-angle assumption driving the hourly generation shape:
annual-energy-maximizing tilt for rooftop (the standard convention,
pending confirmation the existing Sterling solar CF data doesn't already
embed a usable tilt/azimuth), closest-to-optimal for canopy given real
structural constraints (e.g. common east-west row orientation for
parking canopies).

**Distributed storage sizing/dispatch mechanism**: adopts the 8.3
"Recommended Program" configuration as-is (undiscounted wholesale-
equivalent energy rate; PJM-ELCC-derated capacity for both storage and
solar; LSRV-style locational adder; Virginia's own current D-REC
environmental rate; DRV-style event-based rate; the new transmission-
avoidance transfer mechanism).

**DER-owner arbitrage vs. the export-rule structure**: resolved as a
direct consequence of the above, not a separate decision — 8.3's own
energy-rate design is explicitly built around compensating "a
well-timed, storage-backed owner's real dispatch behavior," which
already implies independent DER-owner dispatch, not a centrally-directed
one. Modeled as a post-hoc calculation analogous to Appendix P #8's
existing export-rule treatment, not a new endogenous mechanism inside
the LP itself — consistent with the same "keep upstream complexity out
of the solver" principle already established for the DA/RT price-
response mechanism (now scoped to Scenario 4).

**DLC-vs-price-signal choice for the retail-rate component**: resolved
by the split itself — DLC by default for the new Scenario 3, since
DA/RT is excluded by definition (moved to Scenario 4). No remaining
choice to make here for Scenario 3 specifically.

**DLC-with-backup-generation externality (~$213-253/MWh, Ashburn-style)**:
include in this project's own Tier 1/2/3 social-cost framework —
confirmed this was specifically a social-cost question.

**Avoided-transmission-cost transfer split**: adopts the 25/75 (DER
owner/ratepayer) split from the parallel session as-is, not
re-derived.

**Revenue-volatility floor mechanism**: adopt as a general project-wide
policy — for any scenario with wholesale/market-exposed energy-value-
timing pricing, not scoped narrowly to Scenario 3 alone.

**Distribution-upgrade cost for high-DER-penetration hosting capacity**:
$500/kW benchmark figure accepted. Circuit-count refinement: user's
position is that few or no circuits will actually need upgrades, since
(a) the solar will be firmed, (b) urban/suburban generation amounts fall
below local demand, and (c) data-center-serving circuits specifically
won't need bi-directional-flow upgrades given their load magnitude.
**Flagged, not yet fully reconciled**: this sits in tension with the
user's own item-18 export/overgeneration position (firmed solar can
still overgenerate "the closer we get to 100%") — both can be true at
different penetration levels, but which regime Scenario 3 actually
operates in isn't yet resolved. Revisit before treating the near-zero-
circuit-count position as final.

**Export/overgeneration treatment (post-processing)**: explicitly held
open for further discussion, not decided. User's position: urban/
suburban firmed generation is not expected to be an issue (doesn't
exceed local demand), but utility-scale solar without firming can
certainly cause overgeneration, and even firmed solar will show some
overgeneration at high (near-100%) penetration. How export is handled in
post-processing is the open mechanism question.

**Distribution-line-loss-reduction value stream** (Maryland CEIR-20,
up to $6/MWh): conditional deferral, not a yes/no. Revisit after initial
solving, once owner-DER IRR is computable — add only if IRR comes back
negative or very low.

**Regulatory-process risk for Order 2222/VPP implementation timeline**:
the existing Virginia/Dominion VPP pilot provides real, partial risk
mitigation against a ComEd-style mid-process withdrawal scenario — a
modicum of mitigation, per the user's own framing, not a full
resolution.

**Farmland lease income to VA landowners**: clarified, not still an open
research gap. The rate research already exists and is independently
verified this session (same $1,200-2,500/acre/year figure as citation
C005 in the master citations file; 4-6 acres/MW land-use factor for
single-axis tracking, per Activity Tracker item 8's own original
scoping). What remains is a concrete, ready-to-build calculation task —
applying the rate and land-use factor to Scenario 3's own corrected
solar build sizes — not further research.

**Heat pump/PHIUS quantified impact — re-researched 2026-09-04**: found
a real, well-sourced benchmark, though not Virginia-specific. Opinion
Dynamics / CPUC, "Grid Benefits of Passive Houses, Phase II" (January
2025) — EnergyPlus 8760-hourly modeling comparing Passive-House-
principle homes against code-baseline homes across California climate
zones, feeding the resulting load shapes into real utility feeder
models. Key figures: HVAC energy reduction up to 32% (climate-severity-
dependent — lower in mild zones, higher in extreme-conditioning zones);
summer peak HVAC reduction up to 30%; winter peak reduction up to 50%;
and a directly relevant grid-hosting-capacity finding — over 20% more
Passive-House homes could be added to a sample feeder than code-
baseline homes before hitting element loading limits, with real avoided-
reconductoring costs quantified ($0-$1.4M per feeder in their sample).
California climate zones aren't directly transferable to Virginia's
Zone 4, but the methodology (8760-hourly BEM comparison feeding real
feeder models) and the magnitude range are a real, well-sourced anchor
for a Virginia-specific figure, rather than starting from zero.
URL: https://www.cpuc.ca.gov/-/media/cpuc-website/divisions/energy-division/documents/building-decarb/passive-house-phase-ii-report.pdf

**Locational value credit — what a real VA-specific study would need**:
(a) a specific, named constrained location on Dominion's own system
facing a real capacity-driven upgrade; (b) that location's actual
planned upgrade cost and timeline, from Dominion's own transmission
planning documents (not a literature search); (c) the capacity/energy
DER would need to provide at that location to defer or avoid the
upgrade; (d) the resulting deferral value. Meaningfully more work than
the current NY-benchmark approach, since it requires a real Dominion
document, not published literature — likely why it hasn't been done.

**Land acreage treatment**: two separate, still-open accounting
choices, not one — (1) whether agrivoltaic acreage counts as equivalent
to standard exclusive-use solar acreage or as its own distinct
dual-use category; (2) whether rooftop/canopy solar (zero incremental
land, built on existing structures) is excluded from the land-acreage
total entirely or tracked as its own "zero-incremental-land" line.

**Physical-feasibility rooftop check — proposed method**: take
Scenario 3's own final rooftop MW build-out figure, convert to acreage
using this project's existing land-use factors, and compare directly
against Virginia's real ~68.4 GW total viable-rooftop ceiling (Google
Project Sunroof). A single, bounded arithmetic check, not a research
task — ready to run once Scenario 3's rooftop MW figure is finalized.

**FERC 2222 market-participation scoping**: TBD, still open.

## #4 — Second round of Scenario 3/4/5 decisions, confirmed 2026-09-04

**Panel angle (resolves the open question from #3 above)**: winter-
output-maximizing, not annual-energy-maximizing. Rationale: winter is
both the peak-demand season and the lowest-insolation season for this
project's own geography, so optimizing for winter output targets the
hardest-constrained period directly, rather than spreading benefit
toward summer when insolation is already abundant. Technically implies
a steeper tilt angle than the standard tilt-equals-latitude annual-
optimal convention (steeper tilt favors low-sun-angle winter production
over high-sun-angle summer production).

**Land acreage treatment**: one combined total, with the agrivoltaic and
rooftop/canopy subtotals preserved underneath it for possible separate
display later. Resolves the two-part open question from the prior round.

**Locational value credit**: use the existing NY LSRV benchmark numbers
directly ($31-37/kW-year); no Virginia-specific avoided-cost study
pursued. Closes out the "what would a VA study need" scoping question
as moot.

**DLC-with-backup-generation externality — refinement, not a new
decision**: the backup generators driving the Ashburn-style externality
will need to be Tier 4 (the strictest EPA nonroad diesel emissions
class). Since this requirement applies uniformly across every scenario
with any DLC-induced backup-generator use, it's a constant cost applied
identically everywhere, not a scenario-discriminating lever. Refines,
rather than reopens, the earlier "yes, cost it" decision.

**FERC 2222 market-participation scoping**: resolved — scope to the
true wholesale DERA pathway specifically, not the private-bilateral
pathway already active today. Closes the prior "TBD."

**Revenue-volatility floor mechanism — scope refinement**: applies to
DER-owner (rooftop/canopy) market arbitrage specifically, not to
utility-scale solar/battery, including PPA-contracted utility-scale
facilities. Dominion is assumed to handle its own utility-scale assets'
market participation directly — a sophisticated market participant
doesn't need the same volatility protection an individual DER owner
would. No interaction identified with the centrally-optimized
utility-scale dispatch already inside the LP.

**Physical-feasibility rooftop check**: confirmed, proceed with the
proposed method (Scenario 3 rooftop MW converted to acreage via
existing land-use factors, compared against Virginia's ~68.4 GW total
viable-rooftop ceiling) once the rooftop MW figure is finalized.

**Suburban/urban overgeneration — partially confirmed, one caveat
flagged, not yet fully closed**: the user's claim (urban/suburban
solar+battery output would be fully absorbed by local demand, no
overgeneration issue) holds at the aggregate level — a 10%+10%
(rooftop+canopy) share of total solar is small enough to plausibly stay
below aggregate urban/suburban demand statewide. **Not yet verified at
the individual-feeder level**, though — this is an aggregate-share
claim, and doesn't automatically hold locally unless that capacity is
also spread evenly across circuits rather than concentrated on a subset
of them. The CPUC/Opinion Dynamics study (C104) tracked exactly this
distinction directly (backfeed hours as their own separate grid-impact
metric from peak-load hours) and found measurable, if small, voltage
effects from solar backfeed even in their own aggregate-favorable
sample. Recommend an explicit feeder-level check using that same
methodology before treating this as fully resolved — right in
aggregate, not yet confirmed at the resolution that would actually
matter for distribution planning. Still connects to the unresolved
item-18/item-21 tension flagged in the prior round.


## #5 — Distribution-upgrade cost, resolved via direct assumption, 2026-09-04

**Confirmed, not assumed**: checked directly whether Dominion's real
Hosting Capacity Tool could supply the bulk, aggregate circuit-count
data needed to answer this rigorously. It exists and is real, but is an
interactive, single-location lookup map (zoom to an address, check that
site's remaining capacity) — not a bulk dataset or API. No path exists
to pull aggregate data from it at the scale this question needs,
confirming the "manually-intensive" flag already on record.

**Adopted per direct user instruction**: 5% of Dominion's distribution
systems will need an upgrade for bi-directional flow, replacing the
PNAS-67%-of-feeders-proxy-derived ~910-2,140-circuit estimate entirely.

**Denominator confirmed, 2026-09-04**: applied to the narrower,
already-refined urban/suburban, non-data-center-dedicated circuit
subset (1,360-3,200 — not Dominion's total circuit count), per direct
user confirmation.

**What this implies concretely**:

- **68-160 circuits affected**
- **136-800 MW of affected capacity** (at the existing 2-5 MW/circuit
  placeholder)
- **$68M-$400M total distribution-upgrade cost** (at the existing
  $500/kW figure) — this is the adopted, final figure, replacing both
  the prior $0.9-5.4B illustrative range and the earlier total-
  denominator version of this same 5% assumption ($94M-$470M).

## #6 — Resilience tilt and Bath County discrete-block resolutions, 2026-09-04

**Resilience tilt — resolved as a documentation split, not a code change**:

- **Whitepaper-narrative-facing content (for whoever assembles the benefits
  discussion)**: mention resilience to host customers and society as a
  real, qualitative benefit of long-duration storage (iron-air's 100-hour
  duration vs. shorter-duration alternatives) — this matches NSPM's own
  framework directly, which names host-customer and societal resilience
  as the categories where resilience value is genuinely material, as
  opposed to utility-system-level benefits from centrally-dispatched
  storage, which NSPM's own language calls "likely not material."
- **Modeler-facing content (stays here, in this file, and in
  `lp_model.py`'s own existing comment)**: the small, disclosed,
  one-directional tie-breaking nudge (RESILIENCE_TILT_PCT, originally
  0.03) stays documented as exactly what it honestly is — a modeling
  technique to break a confirmed near-cost-tie between Na-ion and
  iron-air, not a researched valuation of resilience. Not claimed in the
  narrative as a quantified benefit.
- **Not resolved, flagged rather than assumed**: whether to reinstate
  RESILIENCE_TILT_PCT from its current 0.0 back to 0.03 is a separate
  question from the documentation split above, tied to the status of an
  active "RBD trial" (Internal Debugging Log #20.6) this session has no
  visibility into. Left at 0.0 pending confirmation that trial has
  concluded.

**Bath County discrete 480 MW pumping blocks — resolved, not modeled**:
confirmed sufficient given the scale comparison — the maximum possible
gap between a continuous-optimal dispatch value and the nearest
achievable 480 MW step is at most half a block (~240 MW), small relative
to the system's total sodium-ion, iron-air, and solar capacity.
**Clarification worth recording alongside this, since it's a broader,
standing model characteristic, not specific to this one decision**: this
LP has no geographic/nodal structure at all — a single, system-wide
energy balance, not a model with distinct regions. So the smoothing
argument doesn't depend on assets specifically located near Bath County
— the model's total system-wide flexibility already dwarfs a 240 MW
rounding gap regardless of location, since there's no location concept
in the model to begin with. Worth keeping in mind as a general model-scope
limitation: this model could not represent a genuine, real-world
*local*/transmission-constrained version of a problem like this even if
one existed.
## #7 — Items 18 and 21, fully resolved, 2026-09-04

**Item 21, all three sub-questions now resolved:**

(a) **$500/kW figure and the narrower-denominator circuit-count refinement, adopted as-is** —
confirmed directly (not the "$500k/kW" alternate reading, which was a slip). Final figure stands:
68-160 circuits, 136-800 MW, **$68M-$400M total distribution-upgrade cost**, applied to the
narrowed urban/suburban non-data-center-dedicated subset (1,360-3,200 circuits), per direct
confirmation two turns prior.

(b) **Cost borne on the utility side**, parallel to the transmission-avoidance mechanism — not
allocated to individual DER-owner interconnection fees.

(c) **Dominion's own 15%-of-peak-load screening threshold — sourcing significantly strengthened,
not just independently verified.** The original documentation flagged this figure as sourced only
from "a third-party solar-industry website." Direct research this session traced it to something
considerably stronger: FERC Order No. 792 (2013) itself is the underlying source of the 15% screen
convention generally, and states directly, in its own words, that "the existing 15 Percent Screen...
approximates a 50 percent minimum load screen" — a direct, authoritative, named equivalence (C105).
FERC's own preferred, adopted standard is actually 100% of minimum load, having explicitly rejected
more conservative 33%/67% alternatives proposed by NRECA/EEI/APPA. Treating this as resolving the
original "verify against an official document" question, even without a Dominion-specific filing — a
federal order is a stronger source than a Dominion filing would likely be regardless.

Also found and worth retaining as context: a real, standard "minimum daytime load" measurement
window exists as an alternative to the peak-load screening approach — Hawaiian Electric's own field
practice uses a 10am-2pm window specifically (matching the user's own initial recall closely), while
the standard FERC/ISO interconnection clause language specifies 10am-4pm for fixed-panel PV systems
(8am-6pm for tracking systems) — two real, slightly different versions depending on the source, not
a single settled figure across the industry.

**Item 18, resolved — was never actually a contradiction with item 21, once precisely scoped:**

The user's own clarification resolves this cleanly: the two statements were about different asset
populations all along. "Even firmed solar overgenerates the closer we get to 100%" (item 18's
original framing) is a system-wide, utility-scale observation. "Urban/suburban areas won't see
overgeneration" (item 21's own reasoning) is specifically about the narrower DER-owner-arbitrage
subset — rooftop/canopy assets engaged in market arbitrage in urban/suburban areas, where local
demand absorbs all generation. Utility-scale solar/battery facilities are explicitly a different
matter, outside this project's own arbitrage calculations entirely.

**Germany precedent, verified directly rather than accepted on assertion**: the user's own account —
"Germany's issue was not enough batteries overall" — is strongly corroborated by multiple independent
sources found this session. Ember (via energynews, C106) states directly that current storage
capacity in Germany and the EU "is clearly insufficient to absorb production surpluses during solar
or wind peaks." Other sources found (not separately added as citations, but consistent) attribute
Germany's negative-price experience to the same root cause, with one adding a relevant policy-design
nuance: guaranteed fixed feed-in tariffs meant German solar owners were paid even during negative-price
hours, removing the market incentive to pair solar with storage in the first place. This project's
own Scenario 3 design (solar explicitly paired with firming/storage throughout, per the scenario's own
definition) does not share that structural gap — supporting the position that this project's own
firmed urban/suburban DER-owner assets are not necessarily subject to the same overgeneration dynamic
Germany experienced, since the root cause was a storage shortfall (policy-driven), not an inevitable
consequence of high solar penetration itself.

**Net effect**: both items now fully resolved, with no remaining internal tension between them.

## #8 — Solar-time window correction, 2026-09-04

**Direct user correction, verified and adopted**: the Hawaiian Electric 10am-2pm minimum-daytime-
load window (not the broader 10am-4pm standard FERC/ISO clause window) was selected as the basis
for this project's own use, on sound physical grounds — solar irradiance reliably peaks around solar
noon, and a tight ±2-hour window centered on it captures peak output more precisely than a wider one.

**Precise implementation, worked through rather than adopted as a flat "10am-2pm" literal**:
Virginia's longitude relative to Eastern Time's standard meridian (75°W) is a small effect — true
solar noon falls only ~10 minutes after clock-noon for Richmond specifically (up to ~30 minutes at
the state's westernmost edge). The dominant effect is Daylight Saving Time, not longitude: Virginia
observes DST for roughly eight months of the year (mid-March to early November — also the higher-
solar-output months), during which clocks run an hour ahead of the underlying solar-time reference.
A window applied as a literal "hour 10 through hour 14" against data timestamped in ordinary local
clock time would miss true solar noon by a full hour for most of the year.

**Adopted, UTC-anchored window (DST-invariant by construction)**: **15:00-19:00 UTC**, year-round.
Translated to local clock time for implementation against locally-timestamped data:
- **10am-2pm Eastern Standard Time**, roughly November-March
- **11am-3pm Eastern Daylight Time**, roughly March-November

**Standing implication for future work, not just this one item**: any minimum-daytime-load or
backfeed-hours analysis this project performs going forward (including the still-pending feeder-
level overgeneration check from items 18/21) should use this UTC-anchored window or its DST-aware
local-clock equivalent, not a flat "hour 10-14" assumption applied blindly across the full year.

**Direct follow-up, 2026-09-04: does this close the feeder-level check?** Corrected on further
reflection — yes, effectively, and my prior "still open" framing above was itself stale. The
time-window fix and the data-availability gap are indeed two separate prerequisites, as stated above
— but the user's own earlier 5% distribution-upgrade assumption (section 7 above) already resolves
the practical question this check existed to answer, just via a different path than empirical
feeder-by-feeder verification. Adopting a non-zero (5%) assumption, rather than an absolute "zero
circuits ever need upgrading" position, already concedes that some local-level mismatch can occur —
which is the substantive content the feeder-level check was trying to establish. Given the underlying
data constraint (no bulk Dominion feeder data) is permanent, not a temporary research gap, a direct,
disclosed assumption in place of empirical verification is the correct, pragmatic closure, not a
placeholder standing in for work still owed. Treating this as closed.



## #9 — Energy-rate assumption basis updated, 2026-09-05

**Prior basis**: $63.00/MWh ($45 EIA-average-LMP baseline x 1.40 DOM-zone premium,
the latter confirmed earlier this session as Dominion's real, structural ~40%
premium over the RTO average, sourced from `Notes_from_Previous_session.docx`).

**New basis, adopted**: the $45 EIA-average-LMP baseline is replaced with a
directly-sourced, current PJM-wide load-weighted energy figure from Monitoring
Analytics (PJM's own Independent Market Monitor) — **$75.47/MWh** (2026 YTD,
Jan-Jul, load-weighted average, all months included with no exclusions — see
below). Applying the existing 1.40 DOM-zone premium unchanged: **$105.66/MWh**,
replacing $63.00/MWh.

**Why 2026 YTD was chosen over the full 2025 year or a blended average** — this
was a direct, reasoned methodological choice, not a preference for the larger
number:
- Full 2025 (all 12 months, load-weighted): $48.94/MWh — reasonably close to the
  original $45 baseline (+9%).
- 2026 YTD (Jan-Jul, load-weighted): $75.47/MWh — substantially higher (+54% vs.
  2025).
- Blended 19-month view: $58.89/MWh — was considered and rejected as the adopted
  basis.
- **The blended and full-2025 views implicitly treat 2025 and 2026 as equally
  representative draws from a stable distribution.** The adopted reasoning is that
  they are not: data-center load growth is a structural, ongoing driver of PJM
  congestion (not a one-time event), and new transmission construction is
  structurally slow to relieve that congestion (landowner/community siting
  pushback causes real, multi-year delays — PJM's own build-out consistently runs
  behind the load-growth curve). This is a "structural shift, not mean-reversion"
  argument, which justifies weighting the more recent year over an average of the
  two.

**January 2026 ($155.39/MWh) deliberately kept in the average, not excluded** —
direct user instruction, on the grounds that weather/congestion-driven price
spikes are a recurring, structural feature of PJM's real market (the same
category of event as Winter Storm Fern, already a citation in this project's
record), not an anomaly to filter out. Excluding it would have understated the
real, representative energy-cost exposure this project's own energy-rate
assumption is meant to capture.

**Caveat carried forward, not yet resolved**: 2026 is still a partial year
(Jan-Jul only, Aug-Dec not yet posted as of this update). The structural argument
for weighting 2026 is sound regardless, but the exact $75.47 figure could shift
once the full year is available — worth revisiting later in 2026 rather than
treating this as permanently fixed.

**Also flagged, not yet decided**: whether this project's own forward-looking
checkpoint years (2030, 2035, etc.) should assume the data-center-driven
congestion premium continues escalating beyond the 2026-derived level, or hold
flat at it. Treated as a separate, open decision — not folded into this update
without direct confirmation.

**Sourcing**: both the 2026 (C107) and 2025 (C108) Monitoring Analytics data
files are now formally cited in `Master_Citations.xlsx`. Both carry the same
source-stated limitation, worth restating precisely: Monitoring Analytics'
own page explicitly states this data "should not be used to calculate the costs
of any specific market activity in PJM." This project's own use is consistent
with that limitation, not in tension with it — the data informs an internal
modeling assumption for policy analysis, not a formal, auditable cost calculation
for any specific market transaction or utility financial filing. Both files also
flagged for potential relevance to Scenario 4 (DA/RT pricing) specifically, given
their energy-price-component granularity — not yet used for that purpose, kept
tracked via citation for when that work begins.
## #10 — Scenario 3 WMA participation and lookahead capability, 2026-09-05

**Direct decision**: for Scenario 3, all B.1.d/B.1.e (DER-owned rooftop and
parking-canopy) segments — C&I, schools, and parking-lot/canopy solar+battery
systems — are assumed to have full wholesale market arbitrage (WMA) participation
(via FERC 2222, direct or DERA-mediated per the existing D.1 structure) with a
**6-day lookahead capability** specifically.

**Direct connection to the lookahead-window framework** (see
`Six_Day_Lookahead_Firming_Documentation.md`): this means D.2's own supply-side
price-response modeling should be grounded in the **6-day** results (265.42-266.72 MW
worst-day firm level, true 4-county fleet, depending on rooftop tilt) as its basis —
not the 1-day or 3-day figures. Carrying the framework's own caveat forward
precisely: this is a perfect-foresight ceiling, not a real-world-achievable
guarantee — the real-world figure, given actual forecast skill at a 6-day horizon,
sits somewhere between this ceiling and the 1-day floor (0 MW), a gap this
project's own methodology does not resolve.

---

## Foresight asymmetry between utility and distributed storage (2026-09-11)

**This is a bias in the comparison Scenario 3 exists to make, and it must be stated wherever
distributed storage performance is reported.**

### The two halves of the model see different futures

| | lookahead |
|---|---|
| Utility-scale storage, dispatched inside the LP | **perfect** — knows the entire year |
| Distributed storage, responding to `distributed_exogenous_price_mwh` | **effectively none** |

The first is established: own-data capacity accreditation measured on LP dispatch read **100.0%**
against **31.8%** from a no-foresight heuristic on the same fleet and weather
(`lp_package/capacity_accreditation.py`). The LP pre-positions storage for hours it knows are
coming.

The second follows from the scarcity-proxy defect: the six-day scarcity term is near-constant
(CV 3.99%, minimum 84% of mean), so the price series carries **no multi-day lookahead content**.
All its time-varying signal comes from congestion and marginal-loss shapes.

### Why this is not a neutral modelling choice

At high solar and battery penetration, a forecast dunkelflaute implies **steadily rising expected
prices through its duration**. An operator who can see that meters stored energy out judiciously
and may hold charge for days waiting for the best hour — switching from *cycle daily* to **ration
across days**.

The LP does exactly this for utility storage, because it has perfect foresight. The distributed
segment cannot, because its price signal says the same thing every hour of the year.

**So any finding that distributed storage underperforms utility-scale storage on arbitrage value
inherits this asymmetry.** The distributed segment is competing blindfolded.

### The rebound effect — a real failure mode worth modelling eventually

If PJM remains day-ahead-only and DER fleets optimise on that horizon, every operator discharges
into the same first-day peak, storage is exhausted early, and the later days of a multi-day event
arrive with the fleet empty. The resulting spike is **worse than if nobody had discharged**.

Short lookahead does not merely forgo value — it **manufactures the scarcity it failed to
anticipate**.

**Fleet heterogeneity is what makes this tractable.** Real DER fleets carry a wide range of
lookahead sophistication. Longer-lookahead operators profit heavily from the day-four spike, and
that profit is the signal driving adaptation. The rebound is self-correcting over time — but only
where some operators have lookahead to begin with, and only after at least one expensive event has
taught it.

This also bears on the policy argument: **a market design that provides longer-horizon price
signals reduces a physical reliability risk**, not merely a commercial inefficiency. That is a
stronger claim than "DERs would earn more with better signals."

### Options, none yet taken

1. **Fix the proxy** — give it a capacity reference so it produces a genuine rising path. Changes
   the distributed build; a modelling decision, not a bug fix.
2. **Run a no-foresight utility dispatch** for comparison, so both halves are blindfolded equally.
   Consistent, but discards the LP's optimisation.
3. **Report the asymmetry alongside the result** and make no claim about relative storage
   performance. Cheapest, and honest.

Option 3 is the current position by default. Options 1 and 2 are both improvements on it.
