# Virginia Grid White Paper — Reorganized Appendix Structure (First Draft)

**Status note, read first:** This is a structural first draft, not a final
polished document. Appendices A-C draw on prior sessions' work; Appendix A.8
onward captures a subsequent, substantial session focused on gas capacity
constraints, export/curtailment methodology, and the SLCOE-optimization
relationship -- all new since this document's last update. Appendices D-F are
carried over from the existing `VA_Grid_WhitePaper_Section.docx` with no
substantive changes, just relabeling. Appendices G onward (DER/interconnection
content from `Virginia_Energy_Plan_Input.docx`) remain a placeholder list.

**Updated caveat status:** The two bugs flagged in this document's earlier
draft (existing-solar treated as flat 24/7; CVOW wind normalized against its
own observed peak rather than the true 2,535 MW nameplate) have both since
been CONFIRMED FIXED -- `lp_model.py` now uses `CVOW_MW = 2535.0` directly
(verified by direct inspection of the module constant during this session's
chart-debugging work) and existing-solar uses a proper seasonal/hourly
profile, not a flat constant. This session surfaced several NEW, more
significant findings instead -- summarized in A.8-A.11 below. Historical
figures computed before the fixes described in A.8-A.10 (essentially all of
Appendix A's original Scenario 1/1B/3/3B/3C figures) should be treated as
SUPERSEDED, not just caveated -- the underlying LP formulation itself has
changed materially since they were produced.

---

## Appendix A — Resource Adequacy Methodology

*(Extends and renames the former Appendix N working draft; folds in the
RPS-realistic checkpoint methodology and Scenario 3B's definition, both new
this session.)*

### A.1 Purpose and Scope
Establishes why annual-average capacity-factor sizing is structurally
insufficient for reliability planning, and documents the true hourly
linear-programming framework built to test it against real historical
weather rather than typical-year averages.

### A.2 Weather-Year Selection and the Min-Max Robustness Finding

**Status: genuinely re-verified against this project's current,
Virginia-only demand basis (this session).** An earlier phase of this
project (confirmed directly by the user to have actually been run, not
merely inherited, unverified language) established this finding using
that phase's own inputs — Dominion's DOM-LSE load-serving-entity
demand, spanning both Virginia and North Carolina, and the CVOW wind
nameplate reference later corrected in this project's own history
(2,535.0 MW, superseded by the verified 2,587.2 MW figure used
throughout this project since). Files from that earlier run were
independently obtained and checked directly against this session's own
rebuild: both discrepancies confirmed with precision — the embedded
demand series totals exactly 204,498 GWh, the same stale DOM-LSE-scope
figure found elsewhere in this project's history, and the wind data
differs from this session's own by a factor of exactly 1.020592,
mathematically identical to 2587.2/2535.0. So the earlier finding was
genuinely computed, on two independently stale inputs, not a single
demand-scope issue alone. This project's later, deliberate refactor to
Virginia-only demand (Appendix O) and the separate CVOW nameplate
correction (both already established in this project's history) mean
that earlier result could not be assumed to still hold without a
genuine re-run — the underlying weather-year data and cross-test
scripts were, in any case, not present anywhere in this project's
current working environment, so this could not have been quickly
confirmed even if the demand/wind inputs had been correct. Both gaps
are now closed. The user provided genuine, primary-source SAM
simulation output — three 1 GW reference solar arrays (Albemarle,
Chesapeake, King George Counties) and CVOW wind output, for the
calendar years needed to construct both missing hydrological years —
which were used to build `hydro_year_2012_13.npz` and
`hydro_year_2013_14.npz` (`build_hydro3_2012_13_2013_14.py`), on the
correct current-demand and current-CVOW basis, followed by a genuine
re-solve and cross-test.

**The finding holds, confirmed rather than assumed.** Three hydrological
years (April-March, avoiding mid-winter-event splitting) were
independently, jointly re-optimized (build size and dispatch together)
at the 2045 checkpoint, at this project's current Virginia-only demand:
2016-17 (captures the Dec 2016-Feb 2017 sustained low-insolation event),
2013-14 (Polar Vortex), and 2012-13 (the most severe short-window
insolation lull in the sample). Each design's fixed build size was then
tested, dispatch-only, against the other two years' weather
(`cross_test_2045_designs.py`):

| Design → tested against | Unserved energy (MWh) |
|---|---|
| 2016-17 → 2012-13 | 0 |
| 2016-17 → 2013-14 | 0 |
| 2012-13 → 2016-17 | 745,563 |
| 2012-13 → 2013-14 | 0 |
| 2013-14 → 2016-17 | 2,655,300 |
| 2013-14 → 2012-13 | 1,849,228 |

Applying Zeyringer et al.'s (2018, *Nature Energy*) min-max robustness
criterion: **2016-17 is confirmed, genuinely and independently, as the
unique design with zero unserved energy against both other tested
years' weather** — worst-case unserved energy of 0 MWh, versus 745,563
MWh for the 2012-13 design and 2,655,300 MWh for the 2013-14 design.
The archetype pattern from the original (DOM-LSE-basis) finding also
holds at current demand: 2013-14's acute, short-duration-stress design
fails worst against a sustained event, 2012-13 fails less severely,
2016-17 never fails. This explains, and now genuinely validates rather
than merely inherits, the choice to build this project's entire current
body of work — every scenario, every checkpoint — on 2016-17 alone.

**What this does and does not cover.** This re-verification used the
same hard (0.08% gas) constraint and the same 2045 checkpoint as the
most stringent, highest-stakes case — the one where a failure would
matter most. It has not been repeated for the soft (5%) gas constraint
case, nor for every checkpoint year; the original (DOM-LSE-basis)
finding reported all three designs robust to one another under the soft
constraint, and there is no specific reason to expect that to change at
current demand, but it has not been directly re-confirmed and should
not be presented as verified until it is.

### A.3 The Demand-Baseline Correction (historical, DOM-LSE basis — see
status note above for how this relates to this project's current,
Virginia-only demand basis)

A stale cached demand series (built early in this project, never
refreshed when the annual model's own demand trajectory was later
revised) understated every hourly-LP result by roughly 18-20% until
caught and corrected via a targeted sanity check, then a full 36-solve
re-verification — all within that earlier phase's own DOM-LSE (Virginia
+ North Carolina) demand scope. Root cause fixed at the source data
level to prevent silent recurrence within that scope. This correction
predates, and is distinct from, this project's later, separate decision
to narrow scope entirely to Virginia-only demand (Appendix O) — the two
should not be conflated: this section fixed a caching bug within a given
scope, while the later change was a deliberate scope decision, not a bug
fix.

### A.4 RPS-Realistic Checkpoint Methodology (new this session)
Rather than holding gas stringency fixed at its harshest setting throughout
the 2026-2045 window, this methodology follows Dominion's actual Virginia
Code SS56-585.5 RPS schedule year by year — 41% clean by 2030, 59% by 2035,
79% by 2040, ramping to 100% by 2045 — converted into an equivalent gas
allowance via nuclear's fixed, non-RPS-countable contribution. Four checkpoint
years (2030, 2035, 2040, 2044.5) are each independently, fully re-solved
(build sizes are free to respond to cost changes, not just re-priced), with
piecewise-linear interpolation for all physical quantities between
checkpoints -- solar included, after an earlier attempt at smooth
interpolation produced a negative-capacity artifact once one checkpoint's
value dropped sharply relative to trend.

**Scenario 3B / 1B variant:** follows the same real RPS schedule until it
would require gas below a permanent 5% floor, then holds flat at 5% rather
than continuing to ~100% — since RPS's own 2044 requirement (95% clean) already
equals this floor, only the terminal 2044-45 checkpoint requires a separate
solve; earlier checkpoints are identical to the base RPS-realistic trajectory
and are reused directly.

### A.4.1 Relationship to PJM's Own ELCC/RRS Methodology (new, addresses a direct question)
This project's checkpoint-LP-plus-interpolation approach is a deliberately
different, and much less computationally expensive, methodology than PJM's
own ELCC/RRS model (documented in full at A.12) -- not an attempt to
replicate it, and the two should not be read as equivalent or as one
validating the other.

PJM's approach draws its statistical power from breadth: 31 historical
weather years x 13 load rotations x 100 resource-performance draws =
40,300 simulated years, from which "critical hours" and marginal ELCC values
emerge as an average over a very large, though independently-scrambled
(load and resource weather drawn separately, per E3's own flagged
limitation -- see A.12), sample. This project's approach draws its power
from depth in the opposite direction: only 2-3 real historical weather years
(A.2, A.7), but each one run as genuine, unbroken chronological hours with
load and weather from the SAME real year, never scrambled or rotated apart.
This means the true multi-day persistence of an actual sustained event (the
Dec 2016-Feb 2017 stretch that drives this project's sizing) is preserved by
construction -- precisely the property E3 found PJM's own model does NOT
fully capture, and flagged as a growing risk specifically "as energy storage
penetrations increase" (A.12), which is directly relevant given how much
this project's own storage buildout (particularly iron-air LDES) depends on
surviving that exact kind of stretch.

Neither approach is simply better: PJM's breadth gives statistically
defensible tail-risk estimates this project's 2-3 years cannot claim: this
project's depth gives a persistence-correct picture of the ONE stretch it
does model, that PJM's own scrambling methodology does not guarantee. This
project's own A.7 discloses the resulting limitation plainly -- a
2-3-weather-year sample, not the 15-40+ years the broader literature (and
PJM's own practice, at far greater computational cost) suggests for full
statistical robustness. Closing that gap, rather than adopting PJM's
scrambling/rotation apparatus wholesale, is the natural next step (see A.7
and the weather-year-breadth discussion), since chronological persistence
without statistical breadth and statistical breadth without persistence are
different, complementary gaps -- not substitutes for one another.

### A.5 Solver Methodology and Numerical Conditioning
[Carried forward from prior Appendix N — sparse constraint handling, GW/GWh
rescaling, native HiGHS interior-point method for the hard-constraint case,
independent solution verification against the raw constraint set to ~1e-6 MW
closure.]

### A.6 Export: Removed Entirely (originally a disclosed structural limitation, since superseded)
**SUPERSEDED -- see A.9 for the full history and current state.** The $5,000
MW export cap described in earlier drafts was introduced to resolve a solver
degeneracy (unbounded arbitrage from a finite export price against unlimited
volume). A subsequent session identified a deeper problem: even capacity-
limited, export still created a real arbitrage incentive whenever the export
price exceeded gas cost, causing gas to be dispatched purely to sell, not to
serve demand -- found saturated at or near the 5,000 MW cap in the majority
of hours in multiple tested checkpoints, material enough to flag prominently
rather than disclose in passing. The eventual fix (A.9) removed export from
the LP's own optimization entirely, rather than attempting to bound or
reprice the arbitrage away.

### A.7 Known Limitations
Two-to-three-weather-year sample (not the 15-40-year sample literature
suggests for full statistical robustness); verification-rigor asymmetry
between Phase 1 builds and Phase 2 cross-tests; the peaker-fleet capacity
gaps noted in A.8.4 below.

### A.8 Existing Gas Fleet Capacity Constraint (new, substantial session)

#### A.8.1 The Core Finding
Every Scenario 1/1B/3/3B/3C checkpoint solve, from this project's start
through the prior draft of this document, allowed gas dispatch up to
whatever the RPS percentage constraint alone permitted, with no check
against how much gas generating capacity Dominion actually has standing.
Peak implied gas dispatch at several checkpoints (e.g. 17,735-21,758 MW)
exceeded the real, verified existing fleet by a factor of 2-4x, in as much
as 56% of hours at some checkpoints -- self-contradictory, since these
scenarios also assumed no new gas CAPEX. This mirrors, and was directly
prompted by, an earlier and simpler version of the same error caught in
Scenario 3C specifically (originally $23.45/MWh under unconstrained gas,
corrected to $53.11/MWh once capped -- reversing it from the cheapest to
the most expensive of six scenarios computed).

#### A.8.2 Existing Fleet Data Sources and Verification
20 gas plants identified and individually researched: 7 originally-assumed
"combined-cycle" plants (later found to include multiple sites that are
Dominion-owned but not solely CCGT) plus 13 additional peaker/mixed-type
plants, largely via direct EIA plant-level generation-history data
(monthly, 2001-2026) cross-checked against secondary sources and, where
available, Dominion's own official SEC 2023 Form ARS capacity table --
the latter established as the authoritative primary source once found,
superseding secondary-source figures throughout (e.g. Chesterfield's true
gas-only capacity is 386 MW, not the 1,446.6 MW used throughout this
project previously -- that figure was the SITE's combined coal+gas total;
Chesterfield's own observed generation decline from 2016-2019 onward was
entirely a coal-unit retirement, confirmed directly by a Dominion
spokesperson statement that gas Units 7&8 "will remain in service").

Two new plants (Bremo, Bellemeade) were identified this way that had not
been tracked at all previously, both confirmed retired via a directly-cited
SEC 10-Q (six facilities, 1,292 MW, cold-reserved Dec 2018, permanently
retired March 2019).

#### A.8.3 Physical vs. Policy-Driven Retirement (Schedule A vs. B)
Two distinct capacity schedules were built for two distinct purposes.
Schedule A applies pure physical/data-driven retirement (30-year CCGT /
30-45yr combustion-turbine lifespan assumptions, refined against each
plant's own EIA generation data where a formula-predicted retirement could
be directly confirmed or contradicted) -- used for Scenario 3C, which
explicitly models a world without any RPS/VCEA policy constraint. Schedule
B additionally retires three plants whose physical life would otherwise
outlast the 2045 window (Brunswick County, Potomac Energy Center,
Greensville) at exactly 2045, on the reasoning that a genuinely 100%-clean
requirement leaves them no market to sell into regardless of remaining
physical life -- used for Scenario 1/3's own terminal-year context.

#### A.8.4 Data Gaps and Honest Uncertainty, Disclosed Rather Than Smoothed Over
Eight of the ten peaker/mixed-type plants show generation dropping to
exactly zero at the same month (Dec 2024) across two different owners
(Dominion, ODEC) -- treated conservatively as unavailable capacity, but an
independent-verification search found no direct news/regulatory
confirmation of formal retirement, and Global Energy Monitor's own
Gordonsville page (updated Jan 2026) still lists it as "operating" status.
This is disclosed explicitly as CAUSE UNCONFIRMED throughout the
underlying reference files, not asserted as confirmed retirement.

#### A.8.5 Mid-Life Overhaul / EOH Analysis
Equivalent full-load hours were computed directly from each plant's own
generation history and compared against literature-sourced overhaul
thresholds (48,000-100,000 EOH mid-life window for CCGT-style plants;
900-1,200 starts for heavy-duty-frame combustion turbines). Found the
large majority of the active CCGT-style fleet sitting at or past this
decision point simultaneously in 2026, not spread evenly across time --
consistent with, and partial independent evidence for, the separately-
confirmed pattern of active reinvestment proposals across the fleet in
this same period (Chesterfield's own proposed, not-yet-SCC-approved
4-unit expansion; Remington's proposed BESS/turbine upgrade, also
unapproved; the Chesterfield Energy Reliability Center, whose own
approval status changed twice within this session alone -- approved,
reported suspended, then reasserted as approved after the SCC declined
an environmental-group reconsideration petition).

#### A.8.6 Overhaul/Retention as the Preferred Response to an Identified Shortfall
Where a checkpoint re-solve shows the RPS-allowed gas ceiling cannot
physically be reached given Schedule A/B's capacity (confirmed for
Scenario 1's 2035 checkpoint specifically: existing fleet maxes out
around 27% gas share against a 41% RPS allowance), three response paths
were compared by full-window PV: no action (over-comply via extra
solar/storage, $92,742.7M), new-build simple-cycle capacity ($89,525.9M,
capital recovered over an accelerated 10-year stranded basis since the
new capacity has no residual value once RPS reaches its terminal 2045
requirement), and overhauling/retaining specific near-EOL plants instead
of building new ($88,048.8M -- cheapest, since overhaul capital cost is
orders of magnitude below new-build for comparable capacity). This is
established as an explicit, disclosed ASSUMPTION rather than a confirmed
plan -- the specific overhaul cost is a midpoint literature estimate, and
one of the two retained plants (Tenaska Virginia) is third-party owned,
meaning retention would require a negotiated agreement, not just a
Dominion capital decision. New-build, when actually needed, is
standardized to simple-cycle combustion turbines only (not CCGT) for
these scenarios specifically, on cycling-wear grounds -- three reference
unit sizes established (Aeroderivative ~100MW, F-Class ~250MW, H-Class
~430MW) to be mixed and matched to whatever shortfall size is found.

### A.9 Export and Curtailment: Diagnosis and Fix (new, substantial session)

#### A.9.1 The Arbitrage Problem, Identified via a Chart Sanity Check
A routine dispatch-stack visualization (Feb 1-5, Scenario 1's 2035
checkpoint) surfaced gas dispatched at its full capacity cap
simultaneously with export at its full 5,000 MW cap, in the same hours --
economically backwards, since gas cost (~$37-44/MWh) was below the export
price (~$63/MWh average), meaning the LP was generating gas specifically
to sell it rather than to serve demand. This is structurally the same
issue previously identified and fixed in Scenario 2's own methodology
(C.3 above), but had never been applied to Scenario 1/1B/3/3B/3C, which
retained export by default throughout.

#### A.9.2 A Structural Gap That Made the Fix Non-Trivial: No Curtailment Variable
`build_problem()`, the function underlying Scenario 1/1B/3/3B/3C's entire
re-solve, was found to have no unserved-energy or curtailment variable at
all -- unlike `build_scenario2_problem()`, which already had both. The
hourly energy-balance constraint enforced supply equals demand as a hard
equality with no slack; disabling export without first adding curtailment
risked replacing one problem (unwanted arbitrage) with a worse one
(solve infeasibility whenever generation surplus exceeded what demand,
storage-charging, and export together could absorb).

#### A.9.3 The Fix
Curtailment and unserved-energy variables were added to `build_problem()`,
matching the pattern already established and working in
`build_scenario2_problem()` (unserved penalized at $100,000/MWh, matching
literature convention, to guarantee it is never economically preferred
over any real alternative; curtailment penalized at a negligible
$0.01/MWh, just enough to avoid solver indifference). Export was then
removed from the LP entirely, per an explicit design choice: rather than
simply bounding export to zero (which would leave a now-permanently-
unused variable and price signal in the formulation), the export variable,
its price-profile term in the objective, and its own bounds line were all
structurally removed. Any generation surplus the LP cannot otherwise use
now flows into curtailment, which was directly confirmed non-trivial once
correctly measurable (over 1.1 million MWh at the 2035 checkpoint alone,
under the export-enabled formulation used for initial testing).

#### A.9.4 Post-Hoc Export-Potential Accounting, Kept Separate from the LP's Own Objective
Rather than removing the export question from this project's analysis
entirely, curtailment is now used as the basis for a separate, downstream
calculation -- `min(curtailment[t], EXPORT_CAP_MW)` valued at the
existing export price profile -- reported as informational potential
revenue, never fed back into the LP's own cost-minimization. This
preserves the legitimate question ("how much could exporting surplus
clean generation be worth") without letting that potential value distort
the dispatch decision itself, which was the root cause of A.9.1.

**This is a genuinely two-phase decision, worth stating explicitly rather
than leaving implicit (2026-08-16 clarification, prompted by a direct
question about whether A.9's export removal reads as a rejection of
export value generally -- it does not).** Phase 1 (A.9.1-A.9.3, the LP's
own optimization) removed export because it was creating a specific,
mechanical arbitrage incentive -- gas dispatched to sell rather than to
serve demand -- not because export or wholesale market value is judged
illegitimate as a category. This is consistent with, not contradicted by,
NSPM guidance (Section 6.3.2) that wholesale market price effects should
not be waved away as "just a transfer payment": "a BCA test should
include both impacts because both the buyer's costs and the supplier's
profits are a part of the benefits and costs of the electricity
resource." Phase 2 (this section) is where that legitimate value question
actually gets answered -- properly, downstream of the LP, where it cannot
distort the underlying dispatch.

`EXPORT_CAP_MW = 5,000 MW` is an explicit, disclosed DEFAULT assumption
for this Phase 2 calculation, not a hard physical or regulatory limit --
adjustable if a better-sourced figure becomes available. **Status as of
this writing: scoped, not yet executed against this session's corrected
checkpoint curtailment data.** Real curtailment figures already exist
from the completed 2030 and 2035 checkpoints (34,454 MWh and 2,658,772
MWh respectively) and are ready inputs once this calculation is run;
it has not yet been performed for either checkpoint under the corrected
(post-heat-rate-fix) methodology.

**A deeper limitation, worth stating explicitly rather than only noting
the figure is adjustable**: this is a structural simplification, not
just an unsourced number. Real power flow between Dominion and
neighboring zones (AEP, Duke, the broader PJM footprint) is governed by
continuously-recalculated thermal, voltage, and stability constraints
across specific transmission interfaces and lines -- N-1 contingency
analysis across the whole topology, not a single scalar. This project's
entire hourly LP treats Dominion's system as one "copper-plate" node
with no internal transmission structure, no distinction between which
interface power is crossing. A single fixed export-cap number, however
well-sourced, remains a static proxy standing in for a fundamentally
dynamic, multi-constraint reality -- representing that accurately would
require actual line-level topology and full AC power-flow modeling, not
an extension of this LP's own framework. Any curtailment or export-
revenue figure downstream of this constraint inherits this limitation
directly, and should be read as illustrative of the right order of
magnitude, not as a precise physical result.

### A.10 What the LP Actually Optimizes, and Its Relationship to SLCOE (new, substantial session)

Each checkpoint's LP minimizes a single year's absolute Net Cost (build
CAPEX/O&M for solar, sodium, and iron-air, plus that year's gas fuel cost,
plus the unserved/curtailment penalty terms above) -- not SLCOE directly.
SLCOE itself is a separate, PV-weighted calculation performed afterward,
across all four checkpoints together (piecewise-linear interpolation of
Net Cost between checkpoints, discounted at WACC, summed, then divided by
PV demand over the same window). Per-checkpoint cost-minimization is
mathematically equivalent to minimizing SLCOE directly under two
conditions that hold throughout this framework: PV demand (the SLCOE
denominator) is fixed and unaffected by any build/dispatch decision, and
each checkpoint is solved fully independently with no cross-checkpoint
build carryover or path dependency. The one partial exception -- the
existing gas fleet's own capacity schedule (A.8.3) evolving year to year
due to plant retirements -- does not break this equivalence, since each
checkpoint still treats that year's available capacity as a fixed input,
not something shaped by a prior checkpoint's own dispatch choices.

### A.11 Solver Performance Note (new, substantial session)
Adding curtailment/unserved-energy variables increased typical checkpoint
solve time substantially (roughly 65-185 seconds previously, to
approximately 260-290 seconds after). Tested and ruled out cost-
coefficient-range conditioning as the primary driver (reducing the
unserved-energy penalty 100x, from $100,000 to $1,000/MWh, produced only
a ~7% solve-time improvement but caused genuinely non-zero unserved
energy to appear in the solution -- confirming the original penalty
magnitude is necessary for correctness, not just conservatively large).
The added variables/constraints themselves are the more likely driver.
Current practice is to accept the longer solve time with a more generous
timeout (400s+) rather than further performance tuning, which is not this
project's substantive goal.

### A.12 PJM Reserve Requirements and Battery/ESR Reserve Participation (new, substantial session)
Dominion Energy Virginia (DEV) operates within PJM, whose reserve-margin
and ancillary-service framework governs system-wide (not just this
project's own gas-fleet) resource adequacy. Verified against PJM's own
manuals, market filings, and Market Monitor reports; corrections and
disclosed uncertainties are noted below rather than smoothed over.

**Long-term planning reserves (capacity market).** Installed Reserve
Margin (IRM) = 17.7% for the 2024/25 through 2026/27 Delivery Years,
declining slightly to 17.6% for 2027/28 (PJM 2023 Reserve Requirement
Study), set to satisfy NERC/ReliabilityFirst Standard BAL-502-RFC-03: a
Loss of Load Expectation (LOLE) of no more than one occurrence in ten
years. IRM is converted to the Forecast Pool Requirement (FPR), which
expresses the same reserve level in unforced-capacity (UCAP) terms.
CORRECTION to an earlier draft of this formula: FPR = (1+IRM) x
(1 - Pool Average EFORd) is the PRE-2025/26 methodology. Beginning with
the 2025/26 BRA, PJM redefined this as FPR = (1+IRM) x (Reference
Resource Accredited UCAP Factor), reflecting PJM's shift to ELCC-based
(Effective Load Carrying Capability) capacity accreditation -- a
substantive methodology change, not just a relabeling, and directly
relevant to how this project's own storage and solar resources would be
capacity-accredited in PJM's actual market, as distinct from this
project's own energy-balance-only LP treatment of resource adequacy.

**Real-time operating reserves.** Reserve products are layered by
response time: Synchronized (Spinning) Reserve, required within 10
minutes, online/synchronized resources only, **calculated per the
underlying rule as 100% of the Most Severe Single Contingency (MSSC)**
(this project's adopted basis -- see the disclosed operational-deviation
note below for why this is stated explicitly as a choice, not assumed);
Primary Reserve, required within 10 minutes, calculated as 150% of MSSC
with at least 100% met by synchronized resources (confirmed across
multiple independent PJM Market Monitor reports, 2020-2025); and
Secondary Reserve, the current 30-minute-response product. **Secondary
Reserve replaced Day-Ahead Scheduling Reserve (DASR) outright on October
1, 2022** (Monitoring Analytics' 2025 Annual State of the Market Report
for PJM: "PJM implemented the DASR market on June 1, 2008, and eliminated
it on October 1, 2022") -- DASR itself is now historical and excised from
this appendix rather than described in detail, since it no longer exists
as a PJM product. The same 2025 report rates the Secondary Reserve market
"Competitive" across market structure, participant behavior, AND market
performance, with an "Effective" market design -- a materially
better-functioning market than Synchronized Reserve or Non-Synchronized
Reserve, both rated "Not Competitive"/"Flawed" in the same report. This
is directly relevant to the battery/ESR discussion below: Secondary
Reserve looks like the more genuinely viable current market for storage
participation.

MSSC magnitude: this project uses **1,700 MW for the Mid-Atlantic
Dominion (MAD) reserve sub-zone specifically**, sourced to a 2014 PJM
educational presentation ("usually 1700 MW" for the MAD sub-zone). This
is an explicitly CONSERVATIVE assumption -- a current, precise, primary-
sourced RTO-wide or MAD-specific figure was not located (search
intentionally kept non-exhaustive per project direction), and reserve
requirements have generally trended with system growth since 2014, so
the true current figure is at least as likely to be higher than lower.
Flagged for revisitation if a more current figure becomes available.

Also documented, as a disclosed operational deviation this project
explicitly does NOT adopt: PJM's Market Monitor reports that since May
19, 2023, PJM has actually set the synchronized reserve reliability
requirement to 130% of MSSC rather than the 100% the underlying rule
specifies, characterizing this directly as PJM having "unilaterally and
inappropriately extended" the requirement (Monitoring Analytics 2025
SOM Report) -- a documented, still-live source of price distortion
across the synchronized reserve, non-synchronized reserve, AND energy
markets simultaneously, per the same report. **This project's basis is
the underlying 100% rule, not PJM's actual 130% practice, per explicit
project direction (2026-08-16)** -- noted here as context for why PJM's
own real-time market costs may run somewhat higher than this project's
treatment implies, not as a correction this project needs to make.

**A direct, current, and highly authoritative validation of this
project's A.13 methodology, from PJM's own Independent Market Monitor
(2026-08-16 addition).** Monitoring Analytics' 2025 Annual State of the
Market Report for PJM evaluates 2026/2027 BRA market performance as "not
competitive... as a result of the flaws in the Effective Load Carrying
Capability (ELCC) design including the failure to correctly define the
reliability contribution of thermal resources in the winter" -- an
official, current confirmation of the same winter-thermal-reliability
critique already documented via the E3 audit above, now from PJM's own
watchdog rather than a third-party consultant. More directly still, the
same report recommends: "The ELCC approach needs to be applied on a unit
specific basis, incorporate hourly supply and demand matching, and pay
resources based on actual availability and performance rather than on
assumed performance derived from a very limited data set of
misinterpreted performance results based on unrepresentative extreme
historical weather." That is, in substance, a description of this
project's own A.13 Algorithm 1 (hourly, own-data matching) rather than a
blended statistical average -- the single strongest available validation
of this project's adopted approach, from the most authoritative possible
source for this specific critique.

**Real, current, and growing capacity adequacy stress, directly
corroborating the SCC filing already discussed (2026-08-16 addition).**
The same report: "PJM was also short of meeting its reliability target as
of June 1, 2025, on an ICAP and a UCAP basis. The amount that PJM is
short capacity grew from 208.7 MW in the 2026/2027 BRA to 6,516.6 MW in
the 2027/2028 BRA." The report explicitly attributes this to data center
load growth, quantifying "a combined total increase in capacity market
revenues for the 2025/2026 BRA, the 2026/2027 BRA, and the 2027/2028 BRA
of $23,100,955,341" attributable to existing and forecast data center
load -- an RTO-wide corroboration, from PJM's own independent monitor, of
the same dynamic already evidenced at the DEV-specific level in the
PUR-2024-00193 filing (Appendix A, main body). Also forward-looking and
directly relevant to Virginia specifically: the IMM has proposed a
"Reliability Backstop Auction" mechanism requiring large data center
loads to either bring their own new generation or be fully curtailable,
rather than continuing to interconnect without adequate capacity to serve
them -- a live regulatory proposal responsive to exactly the load-growth
dynamic this project's own scenarios are built around.

**Make-whole payments (Operating Reserve Credit / uplift).** Confirmed
against PJM's own terminology: Make-Whole Credit = Cost - Value, floored
at zero, where Cost is the resource's total offer (startup + no-load +
incremental energy) and Value is market revenue earned (energy + cleared
reserves). Paid when a resource is dispatched for reliability and market
revenue does not cover its offer-based cost; funded via Operating
Reserve Charges allocated to load-serving entities.

**Battery storage (ESR) reserve participation -- a real, meaningful
nuance, not a simple "batteries can/cannot" split.** Batteries
participating under PJM's Energy Storage Resource (ESR) model are
confirmed EXCLUDED from Non-Synchronized Reserve by rule (PJM FERC
filing: "because the resource cannot be both offline and online" --
independently confirmed by current third-party market-analytics
reporting). For Synchronized Reserve and Secondary Reserve, however,
the accurate framing is NOT that batteries are simply "allowed": PJM
Manual 11 sets Energy Storage Resources' default Tier 1 Synchronized
Reserve estimate to ZERO MW during market clearing (the same default
treatment applied to Nuclear, Wind, Solar, and Hydro), and the same
default-exclusion-with-exception-process structure applied to DASR
eligibility per the underlying FERC filing (2019, pre-dating DASR's
October 2022 replacement by Secondary Reserve) -- carried forward here
as the applicable structure for Secondary Reserve, DASR's direct
successor, though not independently re-verified against Secondary
Reserve's own current rules specifically. In both cases,
an individual resource owner must affirmatively request and be granted a
PJM exception demonstrating reliable sustained capability before that
resource can actually clear those markets -- a real, resource-specific
administrative and technical hurdle, not an automatic entitlement. Given
Secondary Reserve's confirmed better-functioning market design (above),
this exception path is more consequential there than for Synchronized
Reserve specifically.

Consistent with this default-exclusion structure, a June 2026 PJM
position paper confirms current battery participation in PJM is
concentrated almost entirely in the Regulation market, not reserves:
"Batteries comprised 28.0% and 26.7% of PJM's regulation fleet in 2023
and 2024 respectively. By contrast, PJM has very minimal battery
participation in its reserve markets." PJM's own Reserve Certainty
Senior Task Force is actively working on this gap as of this writing --
directly relevant context for how this project's own future storage
buildout (Na-ion, iron-air) would actually monetize reserve capability in
PJM's real market, versus the energy-balance-only treatment used in this
project's own LP.

### A.13 Adopted Capacity-Credit Methodology for This Project's Own Reserve-Margin Treatment (new, substantial session)
Given the E3-documented critiques of PJM's own ELCC/RRS model (A.12) --
multi-day persistence not captured, load/resource weather misalignment that
specifically understates winter risk, and a thin storage dataset (PJM has
under 500 MW of operational battery capacity as of late 2025) -- this
project does not simply import PJM's flat published class ratings as-is.
A literature review was conducted specifically to identify whether a more
defensible alternative or hybrid existed, rather than treating "PJM's
numbers" and "our own judgment" as the only two options.

**What the literature review found, in brief:**
- Capacity credit is explicitly utility/system-specific in established
  industry practice, not just an RTO-wide average to be imported wholesale
  (Puget Sound Energy's own ELCC primer: "The ELCC of a resource is
  therefore unique to each utility").
- California, an ELCC pioneer since 2018, is moving AWAY from pure ELCC
  toward an hourly, chronological "slice of day" framework specifically
  because ELCC proved difficult to implement and administer at scale (RFF,
  2023) -- a structural direction closer to this project's own checkpoint-LP
  approach than to PJM's probabilistic model.
- A peer-reviewed, validated rapid-approximation method exists for
  estimating solar/wind capacity credit directly from a system's own hourly
  data, with accuracy benchmarked against full ELCC: averaging a resource's
  capacity factor during a system's own top net-demand hours (Ssengonzi,
  Johnson & DeCarolis, 2022, *Renewable and Sustainable Energy Transition*,
  2:100033) -- the foundational finding traces to Milligan & Parsons, who
  showed the approximation converges toward the full ELCC metric once a
  sufficient number of top hours is used.
- Major RTOs have historically used exactly this class of simplified,
  own-data time-window approximation themselves, not always full
  probabilistic ELCC: PJM's own older wind method used capacity factor
  during 3-7pm, June-August, rolling 3-year average; NYISO uses 2-6pm
  (summer) / 4-8pm (winter) capacity factor windows.
- A validated, quantified declining-credit algorithm exists specifically for
  battery storage tied to penetration as a share of peak demand: Mills
  (2020, *Energy*, 210:118587) finds 4-hour storage's marginal capacity
  credit declines from an initial 85-95% to approximately 40-60% as storage
  nameplate capacity reaches 15% of a system's peak demand.
- A directly analogous state-level energy-system policy model (North
  Carolina, using the open-source Temoa framework) uses flat, constant
  capacity credit assumptions specifically because "modeling capacity
  credits as dependent variables introduces non-linearities into the
  [optimization] formulation" -- the same LP-tractability tension this
  project faces, addressed the same way, with the simplification disclosed
  rather than hidden.
- NREL's own ReEDS-based regional capacity-credit dataset (Pham, Cole &
  Gagnon, NREL, 2024/2025) provides an independent, more geographically
  granular (balancing-authority-level, not whole-RTO) cross-check source,
  with its own disclosed limitation (built on 2007-2013 weather data).

**Adopted approach:** compute this project's own solar/wind/storage capacity
credit directly from its own solved checkpoint hourly data, using the
validated algorithms below, cross-validated against PJM's published class
ratings (A.12) and NREL's regional dataset as two independent external
checks -- taking the more conservative (lower) value where our own-computed
credit and the external benchmarks diverge materially, rather than
defaulting to either source uncritically.

**Algorithm 1 -- Solar/Wind Capacity Credit (own-data, per Ssengonzi, Johnson
& DeCarolis 2022):**
1. From a checkpoint's solved hourly LP solution, compute net demand at each
   hour: `ND[t] = demand[t] - nuclear[t] - exist_solar[t] - CVOW_wind_gen[t]
   - new_solar_gen[t]` (residual load after all non-dispatchable clean
   generation -- an extension of the LP's own existing `residual` concept).
2. Rank all hours by `ND[t]` descending; select the top 10.
3. `capacity_credit_solar = mean(solar_cf[top 10 hours])` -- using the raw
   resource-class capacity-factor profile, not curtailed/dispatched output,
   to reflect true resource availability rather than a build-size artifact.
4. `capacity_credit_wind = mean(wind_cf[top 10 hours])`, computed identically.
5. `accredited_MW = nameplate_MW x capacity_credit` for each resource class.

**Algorithm 2 -- Storage Capacity Credit (own-data, per Mills 2020, extended
to this project's multiple duration classes):**
1. Compute this project's own storage penetration ratio at each checkpoint:
   `pen = total_storage_power_MW / checkpoint_peak_demand_MW`.
2. For 4-hour storage, linearly interpolate between Mills' two documented
   endpoints: credit = 90% (midpoint of 85-95%) at `pen -> 0`, declining to
   50% (midpoint of 40-60%) at `pen = 15%`; hold at the 15%-penetration value
   for `pen > 15%` (Mills' study did not characterize behavior beyond that
   point). This linear interpolation between Mills' two reported endpoints is
   this project's own simplification, disclosed as such -- Mills' underlying
   functional form was not independently obtained.
3. For 6-hour and 8-hour storage (this project's other duration classes),
   scale the 4-hour curve from step 2 by PJM's own published duration-ratio
   at matched vintage (6hr/4hr = 58/50 = 1.16x; 8hr/4hr = 62/50 = 1.24x, per
   A.12's 2026/27 BRA table) -- a disclosed synthesis of two independent
   sources (Mills' penetration-decline shape, PJM's duration-scaling ratio),
   not a direct citation of either source alone.
4. `accredited_MW = storage_power_MW x credit_storage(duration, pen)`.

**Cross-validation step (all resource classes):** compare the own-data value
from Algorithms 1-2 against PJM's published class rating (A.12) and NREL's
ReEDS regional figure; where these diverge by a material margin, use the
lower (more conservative) of the own-data and external values, and disclose
the divergence rather than silently picking whichever number is most
favorable.

### A.13.1 Actual LP Implementation: Five Disclosed Simplifying Decisions (new, substantial session)
Rather than applying Algorithms 1-2 above as blended, checkpoint-wide
credit percentages, the reserve-margin constraint actually implemented in
the LP uses each hour's own real data directly -- a more granular and, on
reflection, more defensible approach given this project's hourly-resolution
data already exists. Five specific decisions were made explicitly, each
stated here as a disclosed assumption rather than left implicit:

1. **Hourly actual resource availability, not one blended average.** The
   constraint uses each resource's real value at the specific hour checked
   (solar_cf[t], wind_cf[t], nuclear[t]) rather than a single ELCC-style
   percentage applied uniformly. This sidesteps the lossy summarization
   step Algorithms 1-2 were built for, using data this project already has.
2. **Peak NET demand, not gross peak demand, is the target hour.** As this
   project's own scenarios move toward higher clean-energy shares, the
   hour of highest *net* demand (residual stress after nuclear, existing
   solar, wind, and new solar) becomes the operative adequacy risk, not the
   hour of highest raw system demand -- a system with abundant clean
   generation is not stressed by gross peak load itself if renewables are
   simultaneously abundant that hour. The constraint hour is identified via
   `net_demand[t] = demand[t] - nuclear[t] - exist_solar[t] - wind_gen[t] -
   new_solar_gen[t]`, taking the single highest value.
3. **Full rated (installed) power for dispatchable resources -- gas and
   storage count at their full capacity, not "spare capacity beyond
   scheduled dispatch."** This matches the NSPM's own definition of
   generation capacity as installed capacity available if called upon
   (Section 6.3), not a residual-availability concept.
4. **This is an explicit, simplified proxy for full LOLE-based resource
   adequacy on a single deterministic weather-year solve -- not a
   replication of PJM's own actual methodology.** PJM's real approach
   (A.12) draws statistical power from 40,300 simulated years; this
   project's approach checks a single hard constraint at one identified
   hour, informed by only 2-3 real historical weather years (A.7). This
   should be read as a defensible, disclosed simplification consistent
   with NSPM's own acknowledgment that jurisdictions may use "a certain
   percentage of top load hours" or other alternative peak definitions
   (A.13 above), not as an attempt to match PJM's probabilistic rigor.
5. **Hard constraint, not a soft/priced shortfall.** The LP must build
   enough capacity to satisfy the reserve margin outright, consistent with
   how `unserved` energy is already treated elsewhere in this project's LP.
   A priced-shortfall alternative was considered, anchored to a real,
   directly-relevant number -- the $444.26/MW-day DOM Zone clearing price
   from the 2025/2026 BRA (PUR-2024-00193 filing, main body Appendix A) --
   but that price was explicitly "the maximum allowed under a price cap"
   in an unusually tight-supply auction, making it a poor basis for a
   stable long-run assumption; the hard-constraint approach was adopted
   instead as the more defensible choice.

**Mechanically:** the constraint is checked using the peak-net-demand hour
identified from an initial unconstrained solve, then added as a hard
inequality (`nuclear[t_peak] + gas_capacity_cap + CVOW_MW x wind_cf[t_peak]
+ storage_power_MW + solar_MW x solar_cf[t_peak] >= (1+IRM) x
demand[t_peak]`) and the checkpoint is re-solved; the peak-net-demand hour
is re-checked against the new solution and the process repeats if it has
shifted (for the 2030 checkpoint, it did not -- hour 7148 in both the
unconstrained and reserve-constrained solves, so no further iteration was
needed).

**A real implementation bug found and fixed in the course of this work,
worth documenting rather than quietly correcting.** The existing VCEA
storage-mandate mechanism (4,000 MW floor) enforced its 6-hour duration
requirement using a bound computed from the *fixed mandate number*
(4,000 MW x 6hr = 24,000 MWh), not from whatever power capacity the LP
actually ends up building. Once the reserve-margin constraint pushed
storage power beyond the 4,000 MW floor, the additional increment was not
required to carry any paired energy capacity -- producing a degenerate,
near-zero-duration addition for exactly the marginal portion, undermining
decision 3 above (full rated power should mean a *real*, deployable
battery, not a nameplate-power-only fiction). Fixed by replacing the fixed
numeric floor with a true proportional constraint tying stored energy to
whatever power capacity is actually built (`ENA_ >= min_duration_hr x
PNA_`, enforced as an LP inequality on the variables themselves, not a
precomputed bound) -- the same technique already used for the discrete
4/6/8-hr duration classes in `build_problem_multi_duration`, now applied
to the single-resource path as well.

**Result for the 2030 checkpoint, converged, no further iteration
required:** storage grew from the 4,000 MW regulatory floor to
5,081 MW (properly duration-matched at 6 hours throughout, 30,484 MWh),
adding approximately $64.8M/year to the checkpoint's Net Cost (a modest
increase relative to the checkpoint's ~$5.4B total) -- with curtailment
falling substantially as a side effect (34,454 -> 2,955 MWh), since the
larger, real battery captures meaningfully more of what would otherwise
be wasted generation. Final 2030 Scenario 1 Net Cost, incorporating every
correction and addition made this session (capacity-constrained gas fleet,
6-hour storage duration and cost basis, corrected simple-cycle heat rate,
VCEA storage mandate, and now the PJM reserve margin): **$5,507.2M.**

### A.14 Storage SoC Initial/Closing Condition (new, substantial session)
All three storage types (Bath County, Na-ion, iron-air) are initialized,
and required to end the modeled year, at **50% of their respective built
energy capacity** (`init_soc_frac = 0.5`, a single constant applied
uniformly across all three, hardcoded in `build_problem()` and never
overridden anywhere in this project's own driver code). This is a genuine,
disclosed **modeling convention, not a researched or independently sourced
figure** -- it was adopted because it is neutral (does not bias the LP
toward being helped or hurt by an arbitrary boundary condition), not
because 50% specifically reflects anything documented about how these
plants actually begin or end an operating year in practice.

This constant plays two roles, not one: it sets `soc[0]` (hour 0 of the
modeled year, i.e., April 1, given this project's April-1-start weather-
year convention -- see A.2), and it separately **requires `soc[T-1]` to
return to that same 50% level by the year's last hour**, a closing/cyclic
constraint. Without this closing constraint, the LP could otherwise "cheat"
the boundary -- draining storage to zero in the final hours (since no
future period exists in a single-year solve to make that costly) or
starting artificially full -- either of which would understate real
operating costs relative to a genuinely sustainable, repeating annual
cycle. This is standard practice in year-long dispatch optimization,
not specific to this project.

One point of plausibility worth noting, raised directly in discussion of
this convention: April 1 is a comparatively neutral point in the annual
cycle for Virginia's own demand/weather pattern -- neither deep winter nor
peak summer -- making a half-full starting reservoir/battery a reasonably
plausible assumption for that specific calendar point, even though it
remains a convention rather than a sourced figure.

---

### A.15 Two Additional Weather Years (2018-19, 2019-20) for Intermediate-Year Sensitivity Testing

**Code location**: `lp_package/build_new_weather_years.py`. Extends A.2's
original weather-year selection work (2016-17, 2013-14, 2012-13) with two
further years, built for spot-checking the intermediate-year dispatch-only
solves (Activity Tracker item 57) against weather conditions beyond the
single 2016-17 design year every checkpoint and intermediate year had
otherwise been tested against exclusively.

**Source data**, all user-uploaded, added to Project Knowledge:
- Solar: hourly PVWatts-style output for the same three locations used in
  the original 2016-17 build (Albermarle/Albemarle County, Chesapeake City,
  King George County), for calendar years 2018, 2019, and 2020.
- Wind: CVOW hourly output matrices (`*CVOWhourlymatrixkWhWake140mresults.csv`),
  same three calendar years.

**A genuine duplicate was caught and corrected during sourcing, worth
recording**: the first 2019 Albemarle upload was byte-for-byte identical to
the 2020 Albemarle file -- the same data accidentally uploaded twice under
two different year labels, leaving one of the two years genuinely missing
rather than duplicated. Confirmed and resolved by comparing each candidate
file's correlation against the already-unique, confirmed King George and
Chesapeake data for both years -- same-year weather across nearby Virginia
locations correlates far more strongly than the same location across
different years. The duplicate correlated at 0.92/0.83 (King
George/Chesapeake) against 2020, versus 0.71/0.69 against 2019 --
identifying it as mislabeled 2020 data, not 2019. The user re-ran and
re-uploaded genuine 2019 Albemarle data, independently re-verified the same
way (0.94/0.85 against confirmed 2019 data, versus 0.69/0.68 against 2020)
before being used here.

**Solar blending**: each location's raw output normalized to its own peak
(capacity factor, matching the exact convention already used for 2016-17 --
confirmed directly against the existing file, whose own max is 0.9924),
then averaged across the three locations. One handling note: the
re-uploaded 2019 Albemarle file uses a different column name and unit
("AC inverter output power | (W)" vs. the other files' "System power
generated | (kW)") -- immaterial to the per-file normalization step, since
normalizing by each file's own peak is unit- and scale-invariant.

**Wind parsing**: the CVOW source files use an unusual, non-obvious matrix
layout that does not match this project's normal flat hourly-row format --
worth documenting explicitly since a wrong read here would not have been
obvious downstream. Structure, confirmed by direct cell-value cross-checks
(not assumed): the first data row is a redundant repeat of the day-of-year
column indices as fake values and must be dropped; the remaining 24 rows
represent hour-of-day (0-23); the 365 data columns represent day-of-year.
Correct extraction: drop the redundant first row and the "Time stamp"
index column, transpose the resulting 24 (hours) x 365 (days) matrix, and
flatten in day-major order to produce a standard chronological 8,760-hour
series. Capacity factor computed by dividing by CVOW_MW (2,587.2) x 1000.
Sanity-checked against all three years: identical max capacity factor
(0.818) across 2018/2019/2020, consistent with a fixed rated-output
ceiling net of wake losses (matching the filename's "Wake140m" label) --
and appropriately LOW cross-year correlation (0.07-0.16, versus solar's
much higher cross-year correlation from shared seasonal/day-length
patterns), consistent with wind's genuinely weather-driven, non-repeating
year-to-year variability rather than indicating a data problem.

**Nuclear**: reused directly from the existing 2016-17 file, not
independently sourced for these two new years. Disclosed simplification,
not an oversight -- nuclear output is baseload and does not meaningfully
vary year to year the way solar and wind do, so this narrows what these
two new weather years actually test to solar- and wind-driven variation
specifically, which is the variation actually in question for this
project's storage-sizing and dispatch-timing conclusions.

**Fiscal-year splicing**: this project's April-1-start convention (A.2)
means each new weather year is built by splicing April-December of
calendar year N with January-March of calendar year N+1 (e.g., 2018-19 =
Apr-Dec 2018 + Jan-Mar 2019), at the exact 2,160-hour boundary (31+28+31
days x 24 hours, non-leap). Splice correctness confirmed directly, not
assumed -- cross-checked specific values (including a non-trivial,
non-zero midday value near the boundary) between the spliced array and its
source calendar-year arrays; exact match.

**Status**: both `.npz` files built and verified (`hydro_year_2018_19.npz`,
`hydro_year_2019_20.npz`). Not yet used in any solve -- next step is
running the intermediate-year dispatch-only mechanism (already built for
item 57) against these two additional years at a small number of spot-check
years, not the full 12, as originally proposed.

---

### A.16 Vintage-Tracked Annualized Cost Accounting (fixes the solar/storage checkpoint-objective asymmetry)

**Code location**: `lp_package/compute_vintage_tracked_costs.py`. Directly
resolves the asymmetry identified in this session's SLCOE discussion:
checkpoint objective values (`obj`) charge storage's *full cumulative*
fleet every checkpoint, correctly, but charge solar only its *newest
increment* since the prior checkpoint -- silently omitting the ongoing
annualized cost of everything built earlier. Confirmed directly from the
saved LP output: the `S_mw_incremental` key has no cumulative counterpart
in the checkpoint files, while `PNA_mw`/`ENA_mwh`/`EFE_mwh` have no
"_incremental" counterpart at all -- already full-fleet totals.

**Methodology, per direct user decision**: rather than simply re-pricing
the full cumulative fleet at each target year's current capex rate (which
this project's own capex functions confirm is declining over time,
consistent with NREL cost trends), each build "vintage" is charged at
*its own* historical capex rate, locked in at the year it was actually
built -- not re-priced downward in later years just because construction
got cheaper by then. This mirrors how project financing actually works:
amortization is fixed at commissioning, not renegotiated annually.

**Mechanics**:
1. Each year's cumulative total (solar, Na power, Na energy, iron-air) is
   decomposed into that year's "fresh" increment -- for solar, by backing
   out the prior year's own total degraded forward one year
   (`solar_degradation_factor`, 0.5%/yr, same function already validated
   elsewhere in this project); for storage, a direct year-over-year
   difference, since storage does not degrade in this model (A.14).
2. For any target year, cost = sum over every vintage year up to and
   including the target year, of (that vintage's fresh increment, degraded
   forward to the target year if solar) x (that VINTAGE year's own capex
   rate, via `lp.solar_capex(vintage_year)` etc. -- not the target year's).
3. **2030 (this project's earliest checkpoint) is a disclosed
   simplification**: with no prior year to decompose against, its full
   cumulative total is treated as a single vintage at 2030's own rate --
   in reality this represents 2026-2030 ramp-up this project has no
   granular year-by-year data for.

**Verification, not assumed**: summing the vintage-decomposed increments
(degraded forward as appropriate) back up for every one of the 16 solved
years reproduces the actual reported cumulative total exactly, to two
decimal places, confirming the decomposition is mathematically exact
before any cost-rate weighting is applied.

**Result -- the scale of the correction is substantial, not marginal**:

| Year | Solar $M | Na Power $M | Na Energy $M | Iron-air $M | Total $M |
|---|---|---|---|---|---|
| 2030 | 1,748.1 | 0.3 | 0.8 | 0.0 | 1,749.2 |
| 2035 | 4,067.8 | 50.5 | 833.6 | 395.7 | 5,347.5 |
| 2040 | 6,563.5 | 101.9 | 1,639.6 | 395.7 | 8,700.7 |
| 2045 | 14,995.6 | 174.5 | 2,616.6 | 5,034.2 | 22,821.0 |

(Full 16-year table, including intermediate years, in the Activity Tracker
item logging this work.)

For scale: 2045's vintage-tracked capex+O&M alone ($22,821.0M) already
exceeds the entire old checkpoint objective value ($16,151.9M, which also
included gas fuel cost) -- confirming the earlier, uncorrected figure was
substantially understating true system cost via the missing pre-2040 solar
fleet, not a marginal rounding difference.

**Status**: capex+O&M annualized cost stream complete and verified for all
16 years. Not yet combined with each year's own gas fuel cost (available
directly from the already-solved hourly dispatch, `g.sum() x gas_price`)
or the already-computed export revenue (B.5.1) into a single annual net-cost
stream, and not yet discounted to present value -- those remain the next
steps toward the final SLCOE/NPV figure.

**CORRECTION, same session, before this was used further**: a follow-up
question ("how would a utility accountant handle this?") surfaced a real
double-counting error in this section as originally written. See A.17.

---

### A.17 Correction: Storage Energy Components Use Cycling Cost, Not CRF-Annualized Cost

**Code location**: the storage-cost portion of
`lp_package/compute_vintage_tracked_costs.py` is superseded for the energy
components by a new, separate calculation (cycling-cost extraction from
already-solved dispatch, no new script needed -- see the year-by-year
table below).

**The error**: A.16 as originally written applied the same CRF-based
annualized-cost treatment to all four build variables (solar, Na power, Na
energy, iron-air energy) uniformly. But this project's own LP objective
already includes a separate, established mechanism for Na-ion and
iron-air's *energy* components specifically -- a per-MWh-discharged
"cycling cost," following Sandia National Labs' BESS Cycling Price Model
methodology (`cost = replacement cost / total lifetime throughput`),
because these two chemistries' real limiting factor is cycle life
(10,000-15,000 cycles for Na-ion, ~1,000 for iron-air), not calendar age.
Critically, this cycling cost is computed from the exact same
`NA_ENERGY_CAPEX`/`FE_ENERGY_CAPEX` rates used to build the CRF-annualized
figure -- so charging both, as A.16 originally did, recovers the same
underlying capital dollar twice through two different, parallel methods.

**Resolution, reasoned from standard capital-asset accounting**: a real
asset is depreciated by whichever method matches its actual limiting
factor -- calendar-time methods for assets that age out, throughput/units-
of-production methods for assets that wear out from use -- never both
simultaneously against the same cost basis. Since cycling, not calendar
age, is what actually limits Na-ion and iron-air energy capacity, cycling
cost is the correct, sole recovery mechanism for those two components.
**This affects only the energy (kWh) components.** Na power (`PNA_`)
is unaffected and remains CRF-annualized as in A.16 -- its cycling-cost
mechanism is not derived from `NA_POWER_CAPEX` at all, so no equivalent
overlap exists there; power electronics, inverters, and grid
interconnection genuinely do age out on a calendar basis rather than wear
out from cycling.

**Corrected calculation**: for each year, actual Na and iron-air discharge
(`nd`, `fd`) already exist in the saved hourly dispatch for all 16 solved
years. Valuing that real discharge at each year's own cycling-cost rate
(itself already present in every year's own LP objective, just not
previously extracted separately) replaces the CRF-based energy figures
from A.16.

**Sanity-checked a striking result before accepting it, not assumed
correct**: Na and iron-air discharge both drop sharply at 2045 versus
2044 (Na: 61,690 GWh vs. 188,066 GWh) -- confirmed genuine, not an array-
length or solve error (both years' arrays are the correct 8,760 hours;
2045 shows zero unserved energy). Explained directly by 2045's massive
curtailment (142,266 GWh, nearly 4x 2044's 36,185 GWh) and near-zero gas
dispatch (164.7 GWh vs. 2,387.9 GWh) -- by 2045 the system is so
overbuilt with solar that demand is increasingly met directly, without
needing to cycle expensive storage to shift surplus into other hours.
Consistent with, not contradicting, the storage under-utilization finding
already documented at M.8: a genuinely cost-minimizing system does not
maximize storage utilization, it uses storage only to the extent doing so
is actually economic.

**Result, corrected energy-component cost ($M)**:

| Year | Na cycling $M | FE cycling $M | Total energy $M | (A.16's incorrect CRF figure) |
|---|---|---|---|---|
| 2030 | 0.3 | 0.0 | 0.3 | 0.8 |
| 2035 | 138.3 | 34.7 | 172.9 | 1,229.3 |
| 2040 | 267.2 | 39.4 | 306.5 | 2,035.3 |
| 2045 | 329.4 | 103.5 | 432.9 | 7,650.8 |

(Full 16-year table in the Activity Tracker item logging this correction.)

The corrected figures are substantially smaller -- roughly 4-18x smaller
depending on the year -- confirming the original double-count was a real,
large error, not a rounding-level one.

**Updated total annualized cost by year** (solar CRF-annualized, per A.16,
unchanged + Na power CRF-annualized, per A.16, unchanged + Na/iron-air
energy cycling cost, corrected per this section):

| Year | Solar $M | Na Power $M | Energy cycling $M | Total $M |
|---|---|---|---|---|
| 2030 | 1,748.1 | 0.3 | 0.3 | 1,748.7 |
| 2035 | 4,067.8 | 50.5 | 172.9 | 4,291.2 |
| 2040 | 6,563.5 | 101.9 | 306.5 | 6,971.9 |
| 2045 | 14,995.6 | 174.5 | 432.9 | 15,603.0 |

**Status**: storage cost accounting now believed complete and correct --
power CRF-annualized, energy cycling-cost-based, no remaining known
double-count. Ready to combine with gas fuel cost and export revenue into
the final annual net-cost stream.

---

### A.18 Final SLCOE Assembly (16 Solved Years, Partial Window)

**Code location**: `lp_package/compute_final_slcoe.py`. Combines every
piece built this session into a single annual net-cost stream, discounted
to present value, producing this project's first actual SLCOE figure --
though a partial one, see the coverage caveat below before citing this
number anywhere.

**Formula, per year**: `net_cost = capex/O&M (A.16, solar + Na power,
CRF-annualized) + energy cycling cost (A.17, Na + iron-air, corrected) +
gas fuel cost (SIMPLE_CYCLE_HEAT_RATE, per this project's standing
Scenario-1 convention) - export revenue (B.5.1)`. Discounted to 2026 at
the established 4.5% real WACC. SLCOE = sum(PV net cost) / sum(PV demand),
demand from Appendix 2B-2 (Virginia-only, C071).

**Result**: SLCOE = **$54.59/MWh**, PV net cost $77.649B, PV demand 1,422.5
million MWh, across the 16 solved years (2030-2045).

**Critical coverage caveat -- this is NOT yet this project's final SLCOE
figure**: this project's own established SLCOE window is 2026-2045 (20
years, per this project's original methodology note). This result covers
only the 16 years actually solved or interpolated so far (2030-2045) --
2026-2029 have no build, demand, or dispatch data of any kind yet. Those
four years are missing from both the numerator and denominator here, not
assumed zero-cost -- this is a genuine gap, not a rounding simplification,
and the true 20-year SLCOE will differ from $54.59/MWh once 2026-2029 are
built out. Flagged explicitly rather than silently presenting a partial
figure as final.

**Full year-by-year net cost and PV, all 16 years, in the Activity Tracker
item logging this work.**

**Status**: first complete SLCOE calculation for this project, correctly
assembled from all previously-built, individually-verified components. Not
yet extended to 2026-2029 (would require the same build-interpolation,
demand-construction, and dispatch-solve pipeline already built this
session, applied to those four additional years) or converted into a
standalone NPV figure (straightforward from what's already computed here
-- NPV = -PV(net cost), same discounting already done, no new
calculation needed beyond presenting it as its own figure).

---

### A.19 Terminal (Residual) Value of Assets Outliving the 2045 Window

**Code location**: `lp_package/compute_terminal_value.py`. Directly
follow-on from A.18, prompted by a direct user question: solar and Na
power are CRF-annualized assuming a 25-year useful life, but this
project's analysis window (2030-2045, 16 years; eventually 2026-2045, 20
years) is shorter than that. Every vintage built within the window still
has real, remaining useful life after 2045 -- charging its full annualized
cost only for the years it happened to fall within the window, with no
credit for the remaining years, systematically overstates true net cost.

**Scope limit, important**: applies only to the two CRF-annualized asset
types (solar, Na power). Does NOT apply to Na energy or iron-air --
cycling-cost-based, no prepaid/un-amortized element exists to credit back,
since each year's cost is already fully settled by that year's actual
discharge (A.17).

**Mechanics**: for each vintage year, the fraction of its capex already
recovered within the window by 2045 is `annuity_factor(years_in_window) /
annuity_factor(25)` -- both expressed as fractions of the same annual
payment amount, so the ratio holds regardless of the payment's actual
dollar size. The remaining fraction, applied to that vintage's original
capex (at its OWN build-year rate, same vintage-rate-locking principle as
A.16/A.17 -- not 2045's or 2026's rate), is its terminal value as of 2045.
Discounted back to the project's 2026 base year like every other cost or
credit in this project's PV stream, then subtracted from total PV cost.

**Result -- large, not marginal, and the reason why is structural, not an
error**: with a 16-year window against a 25-year asset life, even the
earliest vintage (2030) recovers only 75.8% of its capex within the
window. Critically, this project's buildout is heavily back-loaded --
85,198 MW of solar alone was added just between 2040 and 2045 -- so the
vintages carrying the most capex have barely begun their 25-year life by
2045: the 2045 vintage itself has recovered just 6.5% of its cost by the
window's end. Since so much of total capex sits in these barely-recovered,
late-window vintages, the aggregate remaining value is large by
construction, not a modeling artifact.

| | Old (no terminal value) | New (with terminal value) |
|---|---|---|
| PV net cost | $77.649B | $28.644B |
| SLCOE | $54.59/MWh | $20.14/MWh |

Terminal value credit: $49.004B (PV as of 2026), reducing SLCOE by
$34.45/MWh (63.1%).

**Status**: terminal value now included for the CRF-annualized components.
Combined with A.18's remaining caveat (this covers only 2030-2045, not the
full established 2026-2045 window), this SLCOE figure is closer to but
still not this project's final, citable number.

---

### A.20 Critical Correction: Export Variable Silently Active in All Dispatch-Only Solves

**Code location**: the fix itself is in `lp_model.py`'s
`build_dispatch_problem()` function signature and body. Re-run scripts:
`solve_intermediate_years.py`, `solve_2026_2029.py`,
`recompute_dispatch_costs_20yr.py`, `compute_final_slcoe_20yr.py`.

**The bug**: `build_dispatch_problem()` was originally built for a
different purpose than how it ended up being used this session --
export-potential analysis specifically -- so it unconditionally set
`bounds[hv(t,IDX['e'])] = (0, EXPORT_CAP_MW)` and included a genuine
`-price[t]*e[t]` revenue term in its own objective, with no
`include_export` parameter at all. Every OTHER use of this function this
session -- the 12 intermediate-year dispatch-only solves (item 57) and the
2026-2029 extension -- silently violated this project's established,
project-wide convention of keeping export strictly post-hoc (A.6/A.9),
without either the caller or this documentation noticing until now.

**How it was caught**: the 2026 dispatch-only solve (zero build, the most
extreme test case) showed gas dispatch exceeding total demand -- a
physically impossible "132.7% gas share." Direct investigation traced the
excess to exactly `EXPORT_CAP_MW` (5,000 MW) at the worst hour. Extracting
the LP's own `e` variable directly confirmed it: nonzero for 8,756 of
8,760 hours, totaling 41.9 million MWh against 2026's entire 95.8 million
MWh of demand.

**Fix**: `include_export` added as an explicit parameter, defaulting to
`False`, properly gating both the bounds and the objective revenue term.
Checkpoints (2030/2035/2040/2045) were **never affected** -- they use the
separate `build_problem()` function, which already correctly excluded
export via its own `include_export` parameter throughout this session.

**Effect on results, now corrected**: with the bogus export outlet
removed, curtailment in the 12 intermediate years and 2026-2029 is
substantially higher than originally reported (e.g., 2031: 5,672.9 GWh
corrected vs. 719.1 GWh originally -- energy that should have shown up as
curtailment was instead being silently "exported" through a channel that
should not have existed), and gas dispatch is correspondingly lower and
more economically sensible. All downstream figures depending on these 16
years' dispatch -- energy cycling cost, gas fuel cost, and post-hoc export
revenue -- were recomputed from the corrected dispatch. Vintage-tracked
capex/O&M and terminal value were **unaffected** by this bug, since both
depend only on build sizes (interpolated from the checkpoints), never on
dispatch results.

---

### A.21 Final SLCOE and NPV: Full 20-Year Window (2026-2045), Corrected

**Code location**: `lp_package/compute_final_slcoe_20yr.py`. Supersedes
A.18's partial (16-year) result -- extends to the full, established
2026-2045 window (per this project's original SLCOE methodology) and uses
the corrected dispatch (A.20).

**2026-2029 construction**: no checkpoint exists before 2030, so 2026 is
treated as a "virtual checkpoint" with zero new (project-driven)
solar/storage build -- this project's own baseline year, and the point
`exist_solar_mw()` itself is defined relative to. Build sizes interpolate
linearly from that zero point to the real 2030 checkpoint, the same
piecewise-linear mechanism already used between every other pair of
checkpoints. Demand uses the same real, Virginia-only Appendix 2B-2 totals
and data-center flattening methodology (Appendix O) already established
for every other year.

**Result**:

| | Value |
|---|---|
| PV net cost (before terminal value) | $86.796B |
| Terminal value credit | $48.639B |
| PV net cost (with terminal value) | $38.158B |
| PV demand | 1,799.7 million MWh |
| **SLCOE (with terminal value)** | **$21.20/MWh** |
| **NPV of net system cost (with terminal value)** | **-$38.158B** |

NPV is reported as negative by convention -- this is a net cost stream,
not a profit-generating investment, so a negative NPV here means exactly
what it should: building and operating this system has a real, substantial
net present cost, not that the analysis found something wrong.

**Consistency check**: this figure ($21.20/MWh) is close to, not wildly
different from, the earlier partial 16-year result computed before both
the 2026-2029 extension and the export bug fix ($20.14/MWh) -- a
reasonable outcome given the two corrections partially offset (adding
2026-2029's own costs and demand, against the export-bug fix's corrected,
somewhat higher costs from properly-counted curtailment), rather than
either correction dominating unexpectedly.

**Status**: this is this project's first complete, full-window,
corrected-dispatch SLCOE and NPV figure. All known issues identified this
session -- the solar/storage checkpoint-objective asymmetry (A.16), the
storage energy double-count (A.17), the missing 2026-2029 years, the
missing terminal value (A.19), and the export-variable bug (A.20) -- have
been resolved and incorporated.

### A.22 Resource Adequacy Landscape: E3's Audit, the IMM's Critique, and
the Weather-Year-Selection Literature (consolidated this session)

A.4.1 and A.12 above already establish this project's relationship to
PJM's own ELCC/RRS methodology and document E3's audit findings and the
Independent Market Monitor's critique at the level needed for those
sections' own purposes. This section consolidates additional detail from
those same sources — specifically the IMM's own recommendations in full,
and the broader academic literature grounding this project's multi-year
weather-selection approach (A.2) — that did not fit naturally into either
earlier section without disrupting their own focus.

**The IMM's July 2025 proposal to PJM's ELCC Senior Task Force, in
full.** Monitoring Analytics' critique (already introduced at A.12) rests
on three specific recommendations, not a single undifferentiated
objection to ELCC:

1. **Remove Winter Storm Elliot (2022) and Polar Vortex 1 (2014) from the
   historical performance dataset**, on the argument that PJM has since
   implemented specific operational fixes (pre-day-ahead unit commitment,
   minimum start-temperature protocols, gas-nomination-cycle awareness)
   directly targeting the failure modes those events exposed, such that
   the historical outage data no longer represents the corrected system's
   forward-looking capability.
2. **Calculate accreditation on a resource-specific, not resource-class,
   basis** — PJM has stated no technical barrier prevents this, and this
   is the same recommendation already quoted at A.12 as validating this
   project's own A.13 methodology.
3. **Incorporate higher winter thermal capability** — the same finding E3
   reached independently (below), and already referenced at A.4.1.

Recommendations 2 and 3 are compatible with, and in the case of #3
directly reinforcing, this project's own approach. **Recommendation 1
deserves explicit, honest treatment, because it runs in the opposite
direction from the approach this project actually takes at A.2.** The
IMM's position — that operationally-patched historical failures should
not continue to weight forward-looking reliability assessment — is not
an unreasonable one on its own terms; it reflects a genuine, arguable
view about how much confidence to place in specific, identified
corrective actions. This project reaches a different conclusion, for a
reason specific to its own purpose rather than a rejection of the IMM's
reasoning generally: this project evaluates whether a **hypothetical
future resource mix**, which does not yet exist and carries no record of
operational correction, can physically survive **real historical
weather** — a different question from whether an *already-corrected,
currently-operating* fleet's historical failure data remains predictive.
The IMM's argument is about the second question. This project's A.2 is
about the first. Both positions can be correct within their own scope.

**E3's Consideration 13, in the audit's own words** (already summarized
at A.4.1, quoted here in full for the record). E3 found that PJM's
day-by-day THI-scrambling approach draws each day's resource performance
independently of the prior day's, which does not reflect the real,
physically-observed tendency of both high- and low-output periods to
cluster across consecutive days: *"the underrepresentation of multi-day
periods of low resource availability risks overstating the reliability
of the system and the ELCC of energy storage resources... energy storage
is likely to run out of charge in these (underrepresented) multi-day
events."* E3 found this same clustering effect empirically present in
real historical data for both solar output and combined-cycle forced
outages, with the consequence growing specifically as storage
penetration increases — directly relevant given how much this project's
own storage buildout (particularly iron-air LDES) depends on surviving
exactly this kind of sustained event.

**The broader academic literature this project's own weather-year
approach draws on.** A.2's citation to Zeyringer et al. (2018, *Nature
Energy* 3(5), 395-403) is the foundational method in a longer, actively-
cited lineage, not an isolated citation:

- **Zeyringer, Price, Fais, Li & Sharp (2018)** were the first to
  formalize optimizing a candidate system separately against each of
  several historical weather years, then evaluating every resulting
  design's performance under every *other* year's weather, selecting the
  design with the lowest worst-case cost — precisely the min-max method
  A.2 applies.
- **Dowling, Rinaldi, Ruggles, Davis, et al. (2020)**, examining a
  39-year (1980-2018) weather dataset for a 100%-renewable U.S.
  electricity system, found cost-optimal long-duration storage
  investment varies substantially depending on which historical years
  are included — directly reinforcing why a single-year result cannot be
  treated as representative on its own. This citation's exact journal
  and page numbers were not independently confirmed to the same standard
  as the others in this list (author names and topic verified via
  secondary citation only) and should be verified before formal
  publication.
- **Gøtske et al. (2024/2025), *Nature Communications***, applied the
  same cross-testing logic at much larger scale — 62 distinct historical
  European weather years, each tested against all others — finding
  explicitly that *"layouts designed for years with compound weather
  events prove more robust,"* a direct, quantified endorsement of
  prioritizing genuinely severe stress years in the design set,
  consistent with this project's own year selection at A.2. A 2025
  extension (arXiv, August 2025) executed 80×79 dispatch-only cross-tests
  against the same design set — the closest published methodological
  analog to this project's own Phase 1 (joint build optimization) /
  Phase 2 (fixed-build dispatch-only cross-test) structure, differing
  only in scale.
- **Van Duinen et al. (2026, submitted to *Applied Energy*)** propose
  simulated annealing against a seasonal sliced Wasserstein distance cost
  function for selecting a small, genuinely representative year subset,
  benchmarked against ENTSO-E's own continental resource-adequacy
  standard. Their explicit recommendation to define climate years as
  *hydrological* years (April 1–March 31), specifically to avoid
  splitting a genuine winter stress event across two calendar years, is
  directly consistent with — and provides after-the-fact methodological
  validation for — this project's own year-boundary convention at A.2.
- **Sundar et al. (2023), *Nature Communications***, used four real
  historical weather years to identify the specific large-scale weather
  patterns driving resource adequacy failures in the Western United
  States as renewable penetration rises, finding a small number of
  recurring compound high-temperature/low-wind/low-solar regimes account
  for the substantial majority of risk hours at 60% renewable
  penetration.
- This literature connects to earlier foundational work — **Pfenninger
  (2017, *Applied Energy*)** on multi-decade time-series reduction, and
  **Hilbers, Brayshaw & Gandy (2019, *Applied Energy*)** on importance
  subsampling under climate-based uncertainty — and to recent
  storage-specific work: **Öberg, Johnsson & Odenberger (2025,
  *Energy*)** on inter-annual weather variation's impact on storage and
  flexible generation, and **Pecora, Rhodes & Webber (2025, *Energy*)**
  on weather-year selection's direct impact on capacity expansion model
  outcomes.
- A field-level synthesis, **"Robust Capacity Expansion Modelling for
  Renewable Energy Systems under Weather Uncertainty"** (*iScience*, Cell
  Press; preprint arXiv:2504.06750), reviews this full Zeyringer-Dowling-
  Gøtske lineage as established background, confirming it is recognized
  within the field as a coherent, cumulative body of work rather than
  isolated results — and states the honest limitation of the
  cross-testing approach directly: it *"cannot assure solutions meet
  certain supply/demand across all years"* — cross-testing characterizes
  performance against the specific years tested, not a mathematical
  guarantee against more severe, untested conditions.
- Two further sources define the field's stated direction beyond simple
  cross-testing, noted here as candidates for future investigation rather
  than part of this project's current methodology: **"On long-duration
  storage, weather uncertainty and limited foresight"** (arXiv:2505.12538)
  draws a precise distinction relevant to how this project's own claims
  should be understood — modeling *multiple historical years*
  (interannual variability, what A.2's approach does) is a materially
  weaker claim than modeling true *weather uncertainty* in the formal
  stochastic-programming sense. A 2025 paper on Adaptive Robust
  Optimization for European "Dunkelflaute" events (arXiv:2507.11361)
  demonstrates the field's more rigorous alternative — endogenously
  deriving worst-case stress scenarios within a single optimization
  rather than relying on a fixed set of historical years at all — a
  materially larger undertaking than this project's current approach,
  noted as the field's own stated direction rather than a near-term
  extension.

**Climate non-stationarity — an acknowledged, unresolved limitation, not
addressed elsewhere in this project.** Every methodology referenced in
this section and in A.4.1/A.12 — PJM's ELCC/RRS Model, E3's audit, the
IMM's critique, and the academic literature above — shares a common,
largely unstated assumption: that historical weather, however sampled or
selected, remains representative of the conditions a system will
actually face in its planning horizon. This assumption is increasingly
contested, and this project does not resolve it. A 2025 review in
*Nature Reviews Earth & Environment* found daily record heat occurred
300–350% more frequently between 2016 and 2024 than a stationary-climate
assumption would predict — a divergence already measurable within the
exact period this project draws its own weather data from, not a distant
future projection. E3's own audit of PJM's model independently
acknowledges the same gap: *"climate adjustments are not standard in LOLP
modeling today given the uncertainty in how weather patterns will
change,"* and *"the assumption that historical conditions provide an
accurate representation is an ongoing area of research within the
field"* — a limitation of current standard industry practice generally,
not a shortfall specific to this project.

An emerging methodological response exists in the literature — Kelder et
al. (2025, *Nature Communications*) describe extreme value statistics
techniques that explicitly model how the statistics of extreme events
shift with time or global temperature, rather than treating historical
extremes as a fixed distribution, an approach the authors describe as
"widely tested, used, and adopted for estimating design values" in other
infrastructure-design contexts, though not yet standard in power-sector
resource adequacy modeling specifically. A national-scale precedent
exists too: Bloomfield (2025) prepared reasonable worst-case stress-test
scenarios for the UK's Climate Change Committee explicitly in the context
of a shifting climate baseline, rather than through unadjusted historical
resampling.

This creates a genuine tension with A.2's own approach, worth stating
rather than resolving artificially. A.2 deliberately seeks out more
severe historical years to strengthen the sizing exercise — but the
further back in time a candidate year is drawn from, the more this same
literature suggests it may represent a climate state increasingly
distant from the one this project's planning horizon will actually face.
Severity and recency are not the same objective, and this project does
not have a principled way to trade one against the other. The physical
mechanisms driving past severe events (stagnant high-pressure systems
suppressing both solar and wind simultaneously; extreme cold outbreaks
stressing thermal generation) remain physically plausible under a changed
climate — but the historical frequency and magnitude associated with any
specific past year should not be read as an unadjusted estimate of
future probability. This project does not attempt a climate-adjusted
reweighting of its historical years; doing so would require methodological
choices (which climate model, which emissions scenario, which adjustment
technique) that remain genuinely unsettled even within the specialized
literature above, and are outside this project's current scope. The
years used here are presented, and should be read, as real physical
stress tests of a candidate resource mix — not as calibrated probability
estimates of this project's actual planning-horizon conditions.

---

## Appendix B — Cost Assumptions (new this session)

### B.1 Solar CAPEX
2026 base of $1,474/kW-AC, derived from Lazard LCOE+ v18.0 (June 2025) Low/High
cases linearly interpolated to Virginia's actual blended capacity factor
(22.8%), corroborated independently by NREL ATB's 2024 base-year figure
projected forward. Superseded an earlier, generic $1,100/kW placeholder.

### B.2 Solar O&M
$24/kW-yr, reconciled across three sources: Lazard and LBNL's 2025 Data
Update (real FERC Form 1 data) both report $11-14/kW-yr for a narrow
core-maintenance scope; NREL's broader $24/kWAC-yr figure was confirmed, via
NREL's own 2021 ATB documentation, to deliberately include land lease,
property tax, insurance, asset management, and security — costs this model
has no separate line items for, making the comprehensive NREL figure the
correct match once scope is properly accounted for.

### B.3 Vegetation Management
A specific claim -- "$3-5/kW-yr in humid southeastern states, double the
national average" -- was traced to its source (an uncited spreadsheet-vendor
marketing blog, internally inconsistent with its own stated baseline, and
separately shown to misattribute an unrelated NREL figure) and REJECTED; no
regional climate penalty is quantified or applied in this model. The related
claim that agrivoltaic sheep grazing offsets such a penalty is similarly not
well-supported at the fleet-average level: the best available peer-reviewed
data (NREL/MDPI Sustainability 2023, 54 real utility-scale sites) finds
grazing roughly cost-neutral against conventional turfgrass mowing on
average (mean $1.55 vs. $1.51/kWdc-yr; turfgrass actually cheaper at the
median). Specific well-documented cases (OSU Extension's worked example;
Tampa Electric via Utility Dive) do show 50-75% site-level savings, but
these are best-case, well-optimized programs, not the typical outcome, and
are presented as such rather than as a fleet-wide offset.

**A refinement to the above, prompted by a direct question about whether the
NREL/MDPI grazing figure is even measuring the right business model for
Virginia specifically (2026-08-16).** The NREL/MDPI dataset's "sheep
grazing" sites appear to reflect a third-party, professionally-contracted
roving-grazier business model (the paper's own text: "Graziers incur costs
to purchase, haul, set up, and take down supplies and equipment, including
water tanks, pumps, mineral feeders, and temporary fencing" -- explicitly
attributing fencing/water/herding costs to the grazier, not the site
operator) -- a real model, and one some utilities do pay directly (Maryland,
for instance, has utilities paying shepherds to rotate herds between solar
sites). But Virginia's own statutory agrivoltaics definition (Va. Code
SS10.1-1197.5, already verified in the Agrivoltaics appendix) is explicitly
about integrating solar into an *existing* farm operation, not contracting
a specialized rotating-herd business -- a structurally different case, where
herding and water systems are the farmer's own pre-existing operating
costs, not a utility-borne line item.

Excluding the NREL/MDPI dataset's "Grazing" ($224/acre/yr mean) and
"Fencing" ($55/acre/yr mean) activity costs on this basis -- as costs that
belong to the farmer's own operation under Virginia's statutory model, not
to utility-borne O&M -- leaves only the residual mechanical maintenance
livestock don't fully handle. The same dataset shows mowing still occurs
even at grazing sites (6 real observations, mean $95/acre/yr, at an average
frequency of ~1 event/year per the dataset). **A conservative floor for
this residual, USING TWICE-YEARLY MOWING (spring and fall growth flush)
rather than the dataset's own once-yearly average**, informed directly by
a project stakeholder's personal, first-hand experience operating a small
sheep flock (explicitly NOT a published, peer-reviewed figure -- flagged as
expert testimony, a different and lower-confidence source category than
the rest of this appendix's citations) -- $95/acre-per-mowing-event x 2 =
**$190/acre/yr, approximately $1.02/kWdc/yr** using the same dataset's own
median land-use ratio (5.35 acres/MWdc).

This is presented as a documented, disclosed finding -- not as a change to
the model's $24/kW-yr blanket O&M figure, since vegetation management is
only one of several bundled cost categories in that comprehensive-scope
NREL ATB figure (alongside asset management, insurance, site security,
cleaning, and component failure), and isolating just the vegetation slice
with the precision this would require is not well-supported by available
data. The finding stands as qualitative record: for the assumed 90%
agrivoltaic-siting share (farmer-integrated model, not roving-grazier), the
defensible utility-borne vegetation-management floor is meaningfully lower
than the NREL/MDPI dataset's full grazing-site total ($1.02 vs. $1.55/kWdc-
yr) -- though likely still understates the true figure somewhat, since
herbicide application and site monitoring (both still reported at grazing
sites in the source data) are excluded from this floor along with
Grazing/Fencing, for conservatism rather than because they're known to be
zero.

### B.4 Storage and Gas-Price Assumptions
Sodium-ion and iron-air CAPEX/O&M carried forward unchanged from prior
sourcing. Three gas-price tiers established for Scenario 2: Base (Deloitte),
Low (EIA reference case), High (Hughes/Post Carbon Institute 2021 — flagged
as the least current of the three, retained for range context).

### B.4.1 Bernstein Research Natural Gas Outlook — Assessed as a Fourth Reference Case (Not Yet Adopted)

**Code location**: `lp_model.py`, `gas_cost_mwh_bernstein(year, high_case=False)`.
Assessed directly at user request, in the same manner as the existing
Deloitte/EIA/Hughes cases — not yet incorporated into Scenario 2's active
Base/Low/High tier structure.

**Source, cross-verified across multiple independent outlets, not a single
unverified article**: Bernstein Research's "Americas Natural Gas Outlook,"
most recently reaffirmed in the 2026 edition (December 2025) — "we
continue to have faith in five," i.e. $5.00/mcf Henry Hub as the new
structural mid-cycle equilibrium, up from a prior decade averaging closer
to $3.50/mcf. The same $5/mcf figure and underlying LNG-export/data-center
thesis is independently corroborated across Hart Energy, Oil & Gas 360,
Marcellus Drilling News, Seeking Alpha, Investing.com, TradingNews, and
Capital.com — not resting on the single originally-provided article alone.
Bullish-risk scenario, separately flagged by Bernstein itself: $8-10/mcf
"under more bullish assumptions, such as a shortfall in Haynesville
growth."

**Methodologically different in character from the other three cases,
disclosed rather than smoothed over**: Deloitte/EIA/Hughes each provide
multi-decade, rising $/MMBtu trajectories with specific year-by-year (or
CAGR-interpolated) points. Bernstein provides something different — a
single "new equilibrium"/"mid-cycle" price level, explicitly not framed by
Bernstein as a year-by-year escalation path. `gas_cost_mwh_bernstein()`
therefore returns a FLAT rate for all years, for both the base and
high case, rather than inventing a trajectory shape Bernstein's own
reporting does not support.

**Unit conversion, made explicit**: Bernstein's figure is Henry Hub
$/mcf, not $/MMBtu like the other three cases. Converted via the standard
EIA factor (1.037 MMBtu/mcf): $5.00/mcf = $4.82/MMBtu; the $8-10/mcf
upside range = $7.71-$9.64/MMBtu (midpoint $9.00/mcf = $8.68/MMBtu used
as the function's `high_case=True` value, since Bernstein gives a range,
not a single upside point).

**Comparison against the existing three cases** (all $/MMBtu):

| Year | Deloitte | EIA | Hughes | Bernstein (base) | Bernstein (high) |
|---|---|---|---|---|---|
| 2026 | 3.70 | 3.70 | 3.50 | 4.82 | 8.68 |
| 2030 | 5.40 | 3.80 | 4.27 | 4.82 | 8.68 |
| 2035 | 5.88 | 4.00 | 5.47 | 4.82 | 8.68 |
| 2040 | 6.35 | 4.20 | 7.01 | 4.82 | 8.68 |
| 2045 | 6.92 | 4.58 | 8.98 | 4.82 | 8.68 |
| 2050 | 7.50 | 4.95 | 11.50 | 4.82 | 8.68 |

**Reading the comparison, stated plainly**: Bernstein's flat $4.82 starts
*above* both Deloitte's and EIA's 2026 points — reading more bullish
near-term. But because Bernstein stays flat while Deloitte keeps climbing,
Bernstein reads *less* bullish than Deloitte by 2040 and beyond, and
Deloitte alone exceeds Bernstein's own flat rate for the entire second
half of this project's window. Bernstein's own upside case ($8.68) lands
close to, not meaningfully beyond, Hughes's existing long-run trajectory
(which reaches 8.98 by 2045 and 11.50 by 2050 on its own) — so Bernstein
does not obviously function as a new, more-extreme high case beyond what
Hughes already provides for this project. It is better understood as a
different *kind* of estimate — a near/mid-term equilibrium view — than a
natural fourth point on the same Base/Low/High trajectory spectrum
already established.

**Caveat on source reliability, disclosed rather than assumed**: analyst
commodity-price views shift substantially over time. The same Bernstein
research team held an explicitly bearish $2.50/MMBtu view for 2018 gas
prices as recently as 2017 — the opposite direction from today's
"supercycle" call. This is a current (reaffirmed December 2025),
well-corroborated view, not an infallible one.

**Status**: assessed and built into the code (`gas_cost_mwh_bernstein()`),
available for use in sensitivity testing or as an additional Scenario 2
tier if desired, but not yet adopted as an active part of Scenario 2's
Base/Low/High structure. No Scenario 2 solves have used it.

### B.5 Export Price for Post-Hoc Curtailment Revenue

**Final value: $27.00/MWh flat** ($45/MWh EIA average LMP x 0.60 midday-
discount factor), applied post-hoc to curtailed energy (bounded by the
5,000 MW/hour `EXPORT_CAP_MW` transmission ceiling already established in
the hourly LP), never fed back into the LP's own dispatch optimization —
consistent with this session's earlier, separate decision to exclude
export entirely from the LP objective.

**Full reasoning trail (worth preserving, not just the answer):** this
value went through three distinct states within this session alone,
following the same "correction history, kept for transparency" convention
already used elsewhere in this model. The prior figure was $37.80/MWh
($45 EIA LMP x 1.40 DOM-zone premium x 0.60 midday discount).

The 1.40x DOM-zone premium was removed based on a user-identified
directional error, not just a magnitude concern: the premium is a
*buy-side, import-scarcity* signal — it reflects what DOM-zone load
currently pays to import roughly 20% of its electricity under supply-
constrained conditions (see PJM's own Operating Reserve Demand Curve
mechanism, C077's companion citations). Applying an import-scarcity premium
to the *reverse* transaction (DOM selling surplus out) very plausibly gets
the sign backwards rather than merely the size: PJM's LMP/congestion
framework means a constrained zone pays more to import precisely because
transmission congestion limits inbound flow — the same congestion
mechanism would be expected to depress, not inflate, the price DOM could
realize exporting out under otherwise-similar conditions. This is the same
underlying transmission constraint already captured by this model's own
5,000 MW/hour export cap, now recognized as bearing on price direction as
well as volume.

A second, independent consideration reinforces dropping the premium:
Virginia's neighboring PJM states that DOM interconnects with (North
Carolina, New Jersey, Maryland, Delaware, Pennsylvania) each have their own
RPS or renewable-energy targets, heavily solar-weighted. Regional solar
generation is weather-correlated across a compact footprint like the
Mid-Atlantic — a sunny day producing DOM surplus is likely producing
surplus in neighboring solar-heavy zones simultaneously, making them
probable *competing sellers*, not scarcity-driven buyers, at precisely the
hours DOM has curtailed energy to sell. This would be expected to suppress
the clearing price further, not support a premium.

**A specific, credible counter-consideration was checked and found not to
apply at the relevant time horizon.** Seel, Mulvaney Kemp et al., "U.S.
Utility-Scale Solar 2025 Data Update" (Lawrence Berkeley National
Laboratory, October 2025 — see M.10 below) defines a directly relevant
"value factor" metric (solar's captured market value ÷ a flat 24x7 block's
average value) and reports PJM's 2024 value factor as slightly *above*
100% ($33/MWh solar value vs. $32/MWh flat-block value) — solar's
generation profile currently *helps*, not hurts, its captured value in
PJM, the opposite of a midday discount. This was weighed directly and set
aside for two disclosed reasons rather than silently ignored: (1) it is a
PJM-wide average, not DOM-zone-specific; (2) more importantly, it is a
2024, current-penetration snapshot, and the same LBNL report documents
value factor declining as solar's share of load grows (CAISO's own
trajectory to a 30% value factor at 30% penetration is the demonstrated
precedent within the same report). This project's checkpoints project
solar growing from roughly 15,000 MW (2030) to 142,000 MW (2045) — a
penetration trajectory the current PJM-wide, sub-saturation snapshot does
not describe. The finding is retained as a documented, disclosed
consideration, not incorporated into the final figure.

**Net result**: $45 x 0.60 = $27.00/MWh — numerically identical to this
model's original, pre-correction figure, but now reached through a
different and more defensible chain of reasoning specific to the export
(not import) transaction, rather than by omission.

### B.5.1 Post-Hoc Export Revenue: Computed Across All 16 Solved Years

**Code location**: `lp_package/compute_export_revenue.py`. Applies the
formula above (min(curtailment, EXPORT_CAP_MW) x $27.00/MWh) directly to
the already-solved hourly curtailment arrays for all four checkpoints and
all twelve intermediate years — no re-solving involved, consistent with
this being a strictly post-hoc valuation, never fed back into any LP
objective.

**Finding worth stating plainly, not just tabulating**: the fixed 5,000
MW/hour transmission cap means export's ability to offset curtailment
shrinks sharply over time, even as curtailment itself grows enormously.
Capture rate (share of a year's total curtailment actually exportable
under the cap) starts near-total at the earliest checkpoint and falls to a
small fraction by the last one, simply because curtailment volume grows
far faster than the fixed cap can absorb:

| Year | Curtailed (GWh) | Exported (GWh) | Capture rate | Revenue ($M) |
|---|---|---|---|---|
| 2030 | 1,072 | 1,064 | 99.3% | 28.7 |
| 2035 | 4,228 | 2,297 | 54.3% | 62.0 |
| 2040 | 16,130 | 4,461 | 27.7% | 120.5 |
| 2045 | 142,266 | 12,260 | 8.6% | 331.0 |

(Full year-by-year table for all 16 years, including the 12 intermediate
years, in the Activity Tracker item logging this work.)

**Total across all 16 solved years: $1,314.7M, undiscounted/nominal.** This
is the raw sum, not yet the present-value figure the SLCOE formula
actually requires — still needs discounting at the 4.5% real WACC (see
Appendix B, Assumptions) before being netted against costs in the final
calculation. Included here as the intermediate result, not the final one.

For scale: this 16-year cumulative total is smaller than a single year's
total system cost at the latest checkpoint alone (2045 objective value:
~$16.2B) — export revenue is a real, worth-including factor in this
project's SLCOE, but not a dominant one.

---

## Appendix C — Scenario 2 Methodology (new this session)

### C.1 Structural Difference from Scenarios 1/3
Solar and storage are fixed inputs (linear buildout to VCEA statutory
minimums — 16,100 MW solar/wind by 2035 per Va. Code SS56-585.5(D)(2), then
flat; 16,000 MW short-duration and 4,000 MW long-duration storage [CORRECTED
2026-08-16, was misquoted as 3,480 MW -- verified directly against the
statute text, SS56-585.5(E)(4): "4,000 megawatts of long-duration energy
storage capacity," half by Dec. 31, 2035, remainder by Dec. 31, 2045], ramping
linearly to 2045 per Va. HB895/SB448), not LP-optimized decision variables.
Only dispatch is optimized against fixed capacities.

### C.2 CCGT Sizing
Sized directly to cover each checkpoint's worst single hourly gap, crediting
storage with zero contribution — a deliberately conservative simplification
in place of a full joint optimization of CCGT size with storage
pre-positioning, which was set aside to conserve session scope.

### C.2.1 Correction: Per-Checkpoint Statutory Minimums (was: one flat figure applied to every year)

**Code location**: `lp_package/solve_scenario2.py`.

**The error, caught before completing the very first solve**: the initial
2030 run used a single, flat set of targets for every checkpoint — 16,200
MW solar, 16,000 MW Na-power, 4,000 MW iron-air — treating the *2035/2045
end-state* targets as if they applied to 2030 as well. Va. Code
§56-585.5's actual text, fetched and read in full directly
(law.lis.virginia.gov), specifies a genuinely phased schedule, not a flat
one:

**Solar/onshore wind (D.2, cumulative, Phase II Utility)**: 2024: 3,000 MW
&rarr; 2027: +3,000 (6,000 cum.) &rarr; **2030: +4,000 (10,000 cum.)** &rarr;
2035: +6,100 (16,100 cum., the full target) &rarr; no further mandated
increase through 2045.

**Short-duration storage (E.2)**: **2030: 4,000 MW** &rarr; 2045: 16,000 MW
(full target). No intermediate milestone specified.

**Long-duration storage (E.4, per 2026 Acts cc.694/695)**: 2035: 2,000 MW
(half) &rarr; 2045: 4,000 MW (full). **No 2030 milestone exists at all** —
nothing is statutorily required that early.

**Corrected 2030 inputs**: solar 10,000 MW (not 16,200), Na-power 4,000 MW
(not 16,000), iron-air 0 MW (not 4,000) — all three were wrong in the same
direction, each one a checkpoint too early relative to its actual
milestone.

**Genuine, unresolved ambiguity for 2035/2040, flagged rather than
assumed**: the statute gives no explicit milestone for Na-power between
2030 and 2045, nor for iron-air between 2035 and 2045. `solve_scenario2.py`
currently placeholders both at their nearer end-state value (2035/2040
Na-power = the full 2045 figure; 2040 iron-air = the 2035 figure) pending
an explicit decision — not run yet, deliberately, until that choice is
made rather than assumed silently.

**Corrected 2030 result** (Deloitte gas): CCGT sized at 14,852 MW (worst-
hour, zero-storage-credit) — unchanged from the pre-correction run,
because the worst hour is an overnight/near-zero-solar hour where fleet
size doesn't matter. Gas share 39.2% (up from an incorrect 28.9%),
curtailment 138.8 GWh (up from an incorrect zero) — smaller storage means
less capacity to absorb surplus even though the surplus itself also
shrank. Zero unserved energy — reliability maintained under the corrected,
smaller fleet.

### C.3 The Export Correction
An earlier version of this formulation carried over Scenario 1/3's export
mechanism without reconsidering fit. Diagnosis: CCGT was being dispatched as
a merchant generator purely for arbitrage (identical export revenue
regardless of demand or clean capacity was the tell); confirmed via zero
curtailment even with export disabled, ruling out genuine overgeneration.
Export removed entirely; gas dispatch dropped 40-53% as a result.

### C.4 Gas-Price Tier Mechanics
Because storage carries zero marginal cost in this formulation and export is
disabled, total dispatch VOLUME (aggregate gas GWh, curtailment GWh) is
mathematically invariant to the specific gas price — only cost changes.
**Correction to this section's original phrasing, verified directly rather
than assumed**: this invariance holds for the aggregate totals only, not
the specific hour-by-hour dispatch pattern. Directly tested (2030,
Deloitte vs. EIA pricing): total gas GWh matched to floating-point noise
(~1e-11), but 275 of 8,760 individual hours showed real differences up to
7,000 MW — LP degeneracy, not an error: with storage's marginal cost at
zero, multiple hour-by-hour dispatch patterns are equally optimal, and the
solver can land on a different one depending on the exact price value
passed in, even though the aggregate volume (and therefore total cost) is
identical either way. Safe to reuse the Base (Deloitte) tier's total
gas/curtailment volumes, repriced rather than re-solved, for cost/SLCOE
purposes specifically — not safe to assume the Low/High tiers' hourly
dispatch arrays are identical to Base's if hour-by-hour detail is ever
needed for its own sake.

### C.5 Full Four-Checkpoint, Three-Gas-Tier Results

**Code location**: `lp_package/solve_scenario2.py` (dispatch solves, one per
checkpoint) plus the repricing calculation described in C.4 (three gas
tiers computed from each checkpoint's single solved dispatch).

**Build inputs by checkpoint**, per the corrected statutory schedule (C.2.1):

| Year | Solar (MW) | Na-power (MW) | Iron-air (MW) | CCGT (MW, worst-hour sized) |
|---|---|---|---|---|
| 2030 | 10,000 | 4,000 | 0 | 14,852 |
| 2035 | 16,100 | 8,000 | 2,000 | 18,556 |
| 2040 | 16,100 | 12,000 | 3,000 | 22,231 |
| 2045 | 16,100 | 16,000 | 4,000 | 25,763 |

**Dispatch outcome, all four checkpoints, zero unserved energy throughout
(reliability maintained at every point)**:

| Year | Gas share | Curtailment (GWh) |
|---|---|---|
| 2030 | 39.2% | 138.8 |
| 2035 | 42.1% | 7.5 |
| 2040 | 51.0% | 0.0 |
| 2045 | 57.4% | 0.0 |

**A genuinely illustrative, expected pattern — the opposite direction from
Scenario 1, worth stating plainly rather than just tabulating**: gas share
*rises* over time under Scenario 2, while it falls sharply under Scenario
1 (59%&rarr;41%&rarr;21%&rarr;0.1% at the same four checkpoints, per A.16's
underlying data). This is exactly what "minimal compliance" should
produce: solar is statutorily flat at 16,100 MW from 2035 onward with no
further mandated increase, while demand keeps growing — a fixed clean
fleet inevitably covers a shrinking share of a growing load. Curtailment
falls to zero by 2040 for the same reason (a modest, no-longer-growing
solar fleet increasingly gets fully absorbed by growing demand, rather
than producing surplus) — a sharp, illustrative contrast with Scenario
1's 142,266 GWh of curtailment at 2045 from continuous, RPS-driven
overbuild. This contrast is precisely the comparison this project's
Scenario 1 vs. Scenario 2 structure is designed to surface.

**Gas fuel cost by checkpoint and tier** (repriced from each checkpoint's
single solved dispatch volume per C.4, not independently re-solved):

| Year | Deloitte ($M) | EIA ($M) | Hughes ($M) |
|---|---|---|---|
| 2030 | 1,631.9 | 1,187.0 | 1,317.0 |
| 2035 | 2,336.3 | 1,645.8 | 2,186.3 |
| 2040 | 3,605.4 | 2,468.6 | 3,951.9 |
| 2045 | 5,064.2 | 3,454.6 | 6,468.8 |

**Status**: gas fuel cost complete for all four checkpoints across all
three established tiers. Not yet built out: annualized capex/O&M for the
fixed solar/storage/CCGT fleet (the Scenario 1 equivalent of A.16/A.17),
curtailment/reliability findings beyond the summary table above, or a
combined Scenario 2 SLCOE/NPV figure comparable to Scenario 1's A.21.

### C.6 CCGT Capex/O&M

**Code location**: `lp_model.py`, `ccgt_capex_kw()`; `lp_package/
compute_ccgt_vintage_and_terminal.py`.

**CORRECTION (2026-08-20), prompted directly by user-flagged recent
market news**: this section originally sourced CCGT capex from Lazard's
LCOE+ v19.0 (already in this project's knowledge base) — "Gas Combined
Cycle" line, capital cost $1,450-$2,100/kW, midpoint $1,775/kW. Per direct
user instruction ("gas turbine prices have soared recently... Lazard very
likely pulled from older data"), this capex figure is now updated —
Lazard's own facility life (30 years) and fixed O&M ($10.00-$25.50/kW-yr,
midpoint $17.75/kW-yr) are RETAINED unchanged, since neither is addressed
or contradicted by the new turbine-price research, which speaks to capex
specifically.

**New capex sourcing, cross-verified across multiple independent outlets
(Bloomberg, Utility Dive, Power-Eng, APPA, Latitude Media), not resting on
one article**: gas turbine equipment and installed-project prices have
risen sharply, driven by data-center-led demand outpacing global
manufacturing capacity (110 GW of orders against 60-70 GW/yr of capacity,
per Wood Mackenzie's April 2026 report). Two scopes matter and are easy
to conflate: turbine-*equipment-only* cost (Wood Mackenzie: reaching
$600/kW by end-2027, a 195% increase since 2019) versus *full installed
project* cost (EPRI, the most recent directly-stated figure: ~$2,000/kW
to ~$3,000/kW in the six months to March 2026). These reconcile, not
conflict — turbines are 20-30% of total project cost per Wood Mackenzie's
own report, so $600/kW of equipment implies roughly $2,000-3,000/kW of
full project cost by 2027 — the same level EPRI's data shows the market
already reaching by its own more recent snapshot. A third, independent
source (GridLab/Energy Futures Group/Halcyon, Sept 2025) corroborates the
same order-of-magnitude rise, from pre-surge ($1,116-1,427/kW) to
2030-31-vintage projects ("routinely" $2,000/kW+).

**Updated methodology, `ccgt_capex_kw()`**: flat $3,000/kW for all years,
anchored to EPRI's most recent full-project figure — a 69% increase over
the superseded $1,775/kW Lazard midpoint. Not extrapolated further in
either direction beyond available sourcing. Wood Mackenzie's own report
explicitly diagnoses the current spike as a temporary manufacturing-
capacity shortfall, not a permanent structural driver, with all three
major OEMs (GE Vernova, Siemens Energy, Mitsubishi) actively expanding
capacity — no sourced basis to assume continued escalation once that
constraint eases, and this project's checkpoints (earliest: 2030) all
fall after Wood Mackenzie's own "supply crunch through 2027" window.

**A genuine, disclosed distinction from solar/storage, unchanged from the
original sourcing**: CCGT retains its own directly-sourced 30-year
facility life (Lazard), not this project's generic 25-year figure used
for solar/storage — its own CRF, not folded into the same bucket.

### C.7 Full Vintage-Tracked Capex/O&M, All Four Checkpoints

**Code location**: `lp_package/compute_ccgt_vintage_and_terminal.py`
(CCGT, updated this section) plus the pre-existing solar/Na-power/energy-
cycling components (unchanged). Same methodology as A.16/A.17: solar and
Na-power CRF-annualized with vintage-rate-locking; Na-energy and iron-air
cycling-cost-based (A.17's double-counting correction applies here too).

**Verified, not assumed**: CCGT vintage decomposition sums back to the
reported cumulative totals exactly at every checkpoint (e.g. 2045: 14,852.3
+ 3,704.0 + 3,674.5 + 3,531.9 = 25,762.8, matching the solved total to the
displayed precision).

**Updated result** ($M) — CCGT column reflects the new capex sourcing (C.6):

| Year | Solar | Na-power | CCGT | Na-energy | Iron-air | Total |
|---|---|---|---|---|---|---|
| 2030 | 1,175.7 | 18.2 | 2,999.0 | 37.5 | 0.0 | 4,230.4 |
| 2035 | 1,849.7 | 33.6 | 3,747.0 | 35.5 | 19.8 | 5,685.6 |
| 2040 | 1,845.5 | 46.6 | 4,489.0 | 16.2 | 0.4 | 6,397.7 |
| 2045 | 1,839.2 | 57.6 | 5,202.1 | 3.4 | 0.0 | 7,102.3 |

(Superseded totals, pre-turbine-price-correction: 3,113.5 / 4,290.0 /
4,725.9 / 5,164.8 — retained here for the correction trail, not for use.)

CCGT was already the largest single cost component before this
correction; it is now even more dominant, at roughly 2.7x total fuel cost
(nominal, EIA tier) across the four checkpoints combined — a direct,
sourced consequence of the current gas-turbine market, not an assumption.

### C.8 Terminal Value

Same treatment as A.19 — solar, Na-power, and CCGT all have real
remaining life beyond 2045 (CCGT's own 30-year life especially), so their
capex is credited back proportionally to what remains unrecovered at the
window's end, discounted to 2026.

**Updated result**: solar $3.273B, Na-power $0.191B, **CCGT $15.871B**
(up from a superseded $9.390B — the higher capex base means more absolute
dollars remain unrecovered at every vintage, even though the *fraction*
recovered by 2045 is similar to before). **Total terminal value: $19.335B**
(up from a superseded $12.854B).

### C.9 Final Scenario 2 SLCOE and NPV, All Three Gas Tiers

**Code location**: assembly combining C.7 (capex/O&M, updated), C.5 (gas
fuel cost by tier, unchanged), and C.8 (terminal value, updated) — same
discounting methodology as A.21 (4.5% real WACC, 2026 base year). No
export revenue term (C.3).

**Updated result, with terminal value included**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 20.987 | 1.652 | $59.42/MWh | **$4.68/MWh** |
| EIA | 18.838 | **-0.497** | $53.33/MWh | **-$1.41/MWh** |
| Hughes | 21.418 | 2.083 | $60.63/MWh | **$5.90/MWh** |

**A genuinely important, counterintuitive result, flagged directly rather
than smoothed over**: the EIA tier's SLCOE comes out *negative*. Verified
this is not a calculation error, not an artifact — CCGT capex is now
substantially higher than gas fuel cost (roughly 2.7x, nominal, for this
tier), and a large share of that capex remains genuinely unrecovered at
the 2045 window boundary given the fleet keeps growing throughout the
period. For the tier with the lowest fuel cost specifically, the capex-
only terminal value credit legitimately exceeds the tier's entire
combined (capex+fuel) present-value cost. This is a real mathematical
consequence of the methodology, not a sign it's broken — but it does
expose a genuine limitation worth stating plainly: **the terminal-value
approach works best when the analysis window captures a reasonable share
of each asset's lifetime cost.** When capex is this large relative to a
20-year window against a 30-year asset life, with heavy back-loading of
new build toward the window's end, the credited remaining value can swing
results into ranges that are difficult to interpret as a straightforward
per-MWh cost — a negative SLCOE does not mean Scenario 2's EIA-tier gas
is "free" or profitable; it means most of this scenario's CCGT capital
commitment sits beyond this project's 2026-2045 analysis horizon, and the
accounting convention that credits that back can dominate the visible
window's own numbers when capex is this concentrated. Retained and
reported honestly rather than adjusted to look more conventional.

**Comparison against Scenario 1, still directionally valid despite the
above**: even before terminal value, Scenario 2's SLCOE ($53-61/MWh, no
TV) now runs noticeably *higher* than the pre-correction figure
($43-50/MWh) and closer to (Deloitte/Hughes) or above (via EIA's
volatility) Scenario 1's own $54.59/MWh no-TV figure (A.18) — the
turbine-price correction has materially narrowed, and in places reversed,
what looked like a clear cost advantage for the minimal-compliance
approach before this correction. This itself is a legitimate, important
finding: Scenario 2's apparent cost advantage over Scenario 1 was
partly an artifact of understated CCGT capex, not fully a reflection of
its lighter clean-buildout obligation.

**Status**: Scenario 2's SLCOE/NPV now reflects current, cross-verified
turbine market pricing. Remaining, parallel to Scenario 1's own open
items: extending to 2026-2029, and reconciling this comparison further
once Appendix D's social-cost framework is applied to both scenarios
side by side. The negative-SLCOE finding for the EIA tier specifically
may also warrant a methodological discussion with the user about whether
terminal value should be capped, floored, or otherwise treated
differently when it approaches or exceeds total PV cost for a given tier
— not yet resolved, flagged here for follow-up.

### C.10 Realistic Gas Fleet Replacement: Existing Fleet Retirement + Type-Matched New Build

**SECOND CORRECTION (later session, direct owner-website verification)**: this section's
existing-fleet roster originally excluded Gordonsville and Gravel Neck entirely, and
marked Marsh Run, Louisa, Wolf Hills, Remington as "already effectively offline" and
Elizabeth River as "already retired" — all based on a generation-data note ("zero
output since Dec 2024, cause unconfirmed") that was over-interpreted as evidence of
retirement. Direct verification against each owner's own current site (Dominion's
power-stations page, ODEC's generation-facilities page, Middle River Power's own
site) confirmed all seven of these plants are still listed as active, operating
facilities — none show any indication of retirement. Corrected to the same
"confirmed still operating → retained through the full window" treatment already
used for Ladysmith/Tenaska/Chesterfield/Possum Point/Doswell; Gordonsville and Gravel
Neck added back to the roster. Existing fleet available, by type, corrected:

| Year | Existing CT (MW) | Existing CCGT (MW) | Total (MW) | (superseded total) |
|---|---|---|---|---|
| 2030 | 4,094.5 | 7,961.5 | 12,056.0 | 10,722.0 |
| 2035 | 4,094.5 | 6,986.5 | 11,081.0 | 8,387.0 |
| 2040 | 4,094.5 | 6,986.5 | 11,081.0 | 8,387.0 |
| 2045 | 0.0 | 3,774.0 | 3,774.0 | 3,774.0 |

2045 is unchanged — VCEA's 100% mandate excludes all gas capacity at that checkpoint
regardless of confirmed-operating status, so this correction only affects 2030-2040.

**New-build need, re-corrected**:

| Year | New CCGT (cumulative) | New CT (cumulative) | Fresh new CT | (superseded fresh) |
|---|---|---|---|---|
| 2030 | 0 | 2,796 | 2,796 | 4,130 |
| 2035 | 0 | 7,475 | 4,679 | 6,039 |
| 2040 | 0 | 11,150 | 3,675 | 0 |
| 2045 | 6,021 | 15,968 | 4,818 (CT) + 6,021 (CCGT) | 2,124 |

**Vintage-tracked annualized cost, re-corrected**:

| Year | Corrected | (superseded) |
|---|---|---|
| 2030 | $142.0M | $209.7M |
| 2035 | $379.5M | $516.3M |
| 2040 | $566.1M | $702.9M |
| 2045 | $2,026.5M | $2,026.5M (unchanged) |

**Terminal value**: gas fleet $10.500B (was $10.045B). **Total terminal value:
$13.964B** (was $13.509B) — terminal value rose slightly even as absolute capex fell,
because less early-build/more late-build (as a share of the smaller total) shifts
more of the capital toward less-recovered vintages, the same dynamic flagged in the
first C.10 correction.

**Final, re-corrected SLCOE and NPV**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 14.609 | 0.645 | $41.36/MWh | **$1.83/MWh** |
| EIA | 11.887 | **-2.077** | $33.65/MWh | **-$5.88/MWh** |
| Hughes | 15.053 | 1.089 | $42.61/MWh | **$3.08/MWh** |

The EIA tier's negative SLCOE is now more negative than before this correction
(-$5.88/MWh vs. a superseded -$3.96/MWh) — same underlying dynamic as flagged
previously, not resolved by this correction.

**Still outstanding**: the plant-specific NOx classification in Appendix D.2
(`PLANT_NOX_CLASS`) uses the same, now-corrected retirement years for these plants
in its own roster and has not yet been re-verified against this update — a small,
likely immaterial follow-up, since the classification (DLN vs. uncontrolled) for
each plant is unaffected by its retirement year, only which checkpoints it
contributes to.

CORRECTION, caught while building a visualization of this section's own
data (2026-08-20)**: as originally written, this section's new-CT sizing
(`new_ct = max(0, peaker_need - existing_CT)`) only credited existing CT
capacity toward the peaking need, ignoring that existing CCGT's own
excess above the baseload level is physically available to cover peaking
hours too — CCGT capacity doesn't stop existing just because it exceeds
the sustained-need calculation. At every checkpoint except 2045, existing
CCGT substantially exceeds its own baseload requirement (by 5,868 MW at
2030, for example) — capacity this methodology was wrongly leaving idle
in the peaking calculation. Fixed: new CT is now sized against the
remaining gap after ALL existing capacity (both types) plus any new CCGT
already decided, not existing CT alone. Verified directly, not assumed:
existing + new now sums to exactly the required peak at every checkpoint
(e.g. 2030: 7,744+0+2,978+4,130 = 14,852, matching peak exactly). All
figures below are the corrected values; the immediately-superseded
(buggy) figures are noted inline for the correction trail.

**Code location**: `lp_package/compute_scenario2_gas_replacement.py`. A
substantial further correction, prompted directly by user observation:
C.6-C.9 as written treated Scenario 2's *entire* required gas capacity as
brand-new CCGT build at every checkpoint, with no reference whatsoever to
the gas capacity Dominion already owns today. This section replaces that
with a physically grounded alternative.

**The user's key observation, which reshaped this methodology**: CCGT
plants are designed for sustained, near-continuous operation — cycling
them (frequent starts/stops) incurs substantially higher O&M costs. CT
(simple-cycle) units, by contrast, are specifically designed for flexible
cycling and handle it well. The right replacement principle is therefore
not "match whatever technology the retiring plant happened to be," but
"size CCGT to the sustained/baseload portion of actual need, and CT to
the intermittent/peaking remainder" — regardless of the retiring unit's
own original type.

**Baseload/peaker split, empirically derived, not assumed**: using each
checkpoint's own already-solved hourly gas dispatch, a load-duration curve
was computed directly. The split uses the 70th-percentile threshold (the
MW level sustained for at least 70% of hours) as the CCGT-sized
"baseload floor," with everything above that (the steep, brief tail) as
the CT-sized peaking need — chosen because this is visibly where each
checkpoint's own curve transitions from a gradual slope to a steep drop
toward zero. Confirmed genuinely different in shape by checkpoint, not
just in level: 2030/2035 show steep curves (near-zero by 75-80% of
hours, overwhelmingly peaker-shaped need); 2040/2045 show much flatter
curves (still 2,461-5,944 MW even at 80% of hours) — the gas fleet
increasingly behaves like real baseload as demand outgrows the
statutorily-flat solar fleet, consistent with C.5's rising-gas-share
finding.

| Year | Baseload (70th pct, MW) | Peak (MW) | Peaker need (MW) |
|---|---|---|---|
| 2030 | 1,875 | 14,852 | 12,977 |
| 2035 | 1,721 | 18,556 | 16,835 |
| 2040 | 6,153 | 22,231 | 16,078 |
| 2045 | 9,795 | 25,763 | 15,968 |

**Existing fleet, full roster (not just `driver.py`'s smaller 8-plant
overhaul/retain pool, which only covers Scenario 1's own retirement-
candidate peakers) classified CT vs. CCGT** — trusting each plant's
detailed notes over its terse type code where they conflict (the type
code reads "CT" for several plants the notes explicitly describe as
combined-cycle, e.g. Greensville County, Brunswick County). Retirement
timing uses confirmed-actual operating status where it contradicts the
30-year formula date (Chesterfield, Doswell, Possum Point, Ladysmith are
all directly confirmed via generation data to still be operating well
past their formula retirement year) — assumed to continue operating
through this project's full window absent a specific confirmed
retirement event, consistent with how this project treats these same
plants everywhere else. Doswell's mixed-type site (901 MW) split 50/50
CT/CCGT — a disclosed placeholder, not sourced data.

| Year | Existing CT available (MW) | Existing CCGT available (MW) |
|---|---|---|
| 2030 | 2,978.5 | 7,743.5 |
| 2035 | 1,618.5 | 6,768.5 |
| 2040 | 1,618.5 | 6,768.5 |
| 2045 | 0.0 | 3,774.0 |

**New-build need, by type, net of existing fleet — CORRECTED (see
correction note at the top of this section)**: CCGT sized to whatever
baseload need exceeds existing CCGT availability; CT sized to whatever
of the total peak remains after ALL existing capacity (both types) plus
any new CCGT, not existing CT alone.

| Year | New CCGT (cumulative, MW) | New CT (cumulative, MW) | (superseded, buggy New CT) |
|---|---|---|---|
| 2030 | 0 | 4,130 | 9,999 |
| 2035 | 0 | 10,169 | 15,217 |
| 2040 | 0 | 13,844 | 14,459 |
| 2045 | 6,021 | 15,968 | 15,968 |

**A genuine, worth-noting quirk, still present after the correction**:
cumulative new-CT need grows more slowly than total capacity — e.g.
2035-to-2040 (10,169 to 13,844 MW) despite the checkpoint's much larger
total capacity growth. This reflects the baseload threshold itself
growing substantially over this span (1,721 to 6,153 MW), reclassifying
capacity that would have counted as "peaking" earlier into "baseload"
later. Where this pattern actually goes slightly negative (not the case
here after the fix, but preserved as a documented edge case), the
vintage-decomposition logic floors the resulting fresh-increment at zero
rather than modeling an impossible "un-build" of already-installed
capacity.

**CT capex sourcing**: F-Class ($713/kW, $7.00/kW-yr fixed O&M) — this
project's own already-established default for new-build simple-cycle
capacity (`driver.py`'s `select_overhaul_retain()`, `NEWBUILD_UNITS[0]`,
chosen there as the cheapest of three reference units). Same 30-year
life as CCGT (`Gas_turbine_lifespans_reference.md`: CCGT 25-30yr, CT
peakers 30-45yr — using the shared, lower end of both ranges for
consistency), same CRF, own vintage-tracking and terminal-value treatment
identical in structure to CCGT's (C.6/C.8).

**Vintage-tracked annualized capex+O&M, corrected result — the scale of
the reduction is substantial, not marginal**:

| Year | Original (100% new CCGT) | Corrected (existing fleet + type-matched, bug-fixed) |
|---|---|---|
| 2030 | $2,999.0M | **$209.7M** |
| 2035 | $3,747.0M | **$516.3M** |
| 2040 | $4,489.0M | **$702.9M** |
| 2045 | $5,202.1M | **$2,026.5M** |

The reduction is large because the existing fleet (~10,700 MW combined
CT+CCGT at 2030) already covers most of the requirement, and because the
baseload/peaker split routes nearly all new-build toward the far cheaper
CT rate ($713/kW) rather than CCGT's ($3,000/kW) — the earlier C.6-C.9
figures implicitly assumed all new capacity was CCGT-grade, which this
correction shows was not warranted by the actual dispatch shape.

**Gas fuel cost, also corrected to reflect the CCGT/CT split** (same
per-hour split: dispatch up to the baseload level valued at CCGT's 6.4
MMBtu/MWh heat rate, dispatch above it at CT's 9.5 MMBtu/MWh rate — a
~48% higher fuel burn per MWh for the peaking portion, not previously
captured when all dispatch was priced at the CCGT rate; unaffected by the
new-build-sizing bug fix above, since fuel cost is computed directly from
the solved hourly dispatch, not from the new-build totals):

| Year | Deloitte ($M) | EIA ($M) | Hughes ($M) |
|---|---|---|---|
| 2030 | 2,155.7 | 1,555.6 | 1,730.9 |
| 2035 | 3,185.0 | 2,223.6 | 2,976.2 |
| 2040 | 4,401.4 | 2,995.0 | 4,830.1 |
| 2045 | 5,844.1 | 3,969.8 | 7,479.6 |

**Terminal value**: solar $3.273B, Na-power $0.191B, gas fleet (CCGT+CT
combined) $10.045B. **Total terminal value: $13.509B.**

**Final, corrected SLCOE and NPV, all three gas tiers**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 14.832 | 1.323 | $41.99/MWh | **$3.74/MWh** |
| EIA | 12.110 | **-1.399** | $34.28/MWh | **-$3.96/MWh** |
| Hughes | 15.275 | 1.766 | $43.24/MWh | **$5.00/MWh** |

**The EIA tier's SLCOE remains negative, and is now somewhat more
negative than before the bug fix** (-$3.96/MWh vs. the immediately-prior,
buggy -$1.16/MWh) — the same underlying dynamic flagged in C.9 still
applies: a meaningful share of this scenario's gas-fleet capital
commitment sits beyond the 2045 window boundary, and correcting the
new-build sizing shifted more of that commitment toward later, less-
recovered vintages rather than resolving the underlying tension. This
reinforces, rather than resolves, C.9's flagged open question about
whether terminal value needs different treatment when it approaches or
exceeds a tier's total PV cost.

**Status**: this is Scenario 2's most physically-realistic gas-cost
methodology to date, now also verified internally consistent (existing +
new capacity sums exactly to each checkpoint's required peak). Superseded
figures retained throughout this section and C.6-C.9 for the full
correction trail, not for use. Same remaining open items as C.9:
2026-2029 extension, and the EIA-tier negative-SLCOE methodological
question.

---

### C.11 Turbine Procurement Lead Time: Feasibility Check on 2030's New-Build

Prompted directly by user question: given confirmed current gas turbine lead times
(C.6-adjacent research, this session — 5-7 years for heavy-duty CCGT frames, 2-4
years for simple-cycle units specifically, the relevant case here), is the corrected
2030 new-build requirement (2,796 MW fresh, C.10) actually achievable in time?

**Timing check**: exactly 4 years separate today (August 2026) from the 2030
checkpoint. At the confirmed simple-cycle lead-time range (2-4 years), turbines
ordered starting now would be ready anywhere from 2028 (fast end) to exactly 2030
(slow end) — tight, with no margin for delay, but not infeasible on its face. This
is a materially different conclusion than for the original, larger 4,130 MW figure
(pre-C.10-correction), which would have required orders placed essentially before
this project's own analysis began.

**Resolved as feasible**, on two grounds: (1) the timing arithmetic itself is
consistent with a 2030 in-service date if procurement starts promptly, and (2)
real-world precedent — Dominion has already demonstrated willingness and ability to
place large new simple-cycle turbine orders on a comparable timeline, via the
Chesterfield Energy Reliability Center (944 MW, 4-unit simple-cycle, SCC-approved
November 2025, per this project's own earlier tracking, A.8.5) — user-reported
turbine ordering activity for that project predates the SCC approval by a year or
more, consistent with normal parallel permitting/procurement practice. CERC itself
is a separate, specific project and is not counted toward this analysis's own
modeled 2,796 MW requirement — it is cited here only as evidence that turbine
procurement on this scale and timeline is something Dominion has actually done, not
a hypothetical capability.

**Disclosed caveat**: this conclusion assumes procurement begins essentially
immediately and experiences no material slippage (permitting, interconnection
queue, or further supply-chain tightening) — a real risk given the tightness of the
margin, not a certainty. No quantitative adjustment made to Scenario 2's SLCOE/NPV
on this basis; C.10's figures stand as the final result for this checkpoint.

### C.12 Full 20-Year Extension — Correcting a Major, Previously Undisclosed Gap

**The gap**: every Scenario 2 SLCOE/NPV figure through C.11 was built from
the 4 checkpoints (2030/2035/2040/2045) only — discrete years, individually
discounted, with **no dispatch or build-out information for the other 15
of 20 modeled years**. This was not previously flagged as a limitation in
this appendix. It surfaced only when directly asked how yearly gas
consumption and new-turbine timing between checkpoints had been captured
— they hadn't been, at all, for Scenario 2 (unlike Scenario 1, which
genuinely solved all 12 intermediate years).

**Corrected**: solved all 12 intermediate years (2031-2034, 2036-2039,
2041-2044) plus 2026-2029, using `solve_scenario2_year()` (already
year-parameterized, unmodified) with the VCEA statutory solar/storage
targets linearly interpolated between their own defined milestones —
solar flat after 2035 (no further statutory milestone), Na-power
interpolated 2030-2045, iron-air interpolated 2035-2045 (zero before,
consistent with the existing checkpoint treatment). 2026-2029 uses the
statute's own earlier milestones (2024: 3,000 MW, 2027: 6,000 MW
cumulative, Va. Code §56-585.5 D.2) rather than extrapolating backward
from 2030 alone. All 20 years connect smoothly — no discontinuities at
the original checkpoint boundaries (e.g., 2034's 17,770 MW peak leads
into 2035's 18,556 MW checkpoint; 2044's 25,082 MW leads into 2045's
25,763 MW).

C.10's existing-fleet-crediting and baseload/peaker-split methodology
(including the CCGT-excess-covers-peaking correction) was then applied
to all 20 years, not just 4 — every year independently verified
(existing + new sums exactly to that year's own peak, all 20/20 years).

**Result — a complete reversal of the prior conclusion**:

| Gas tier | 4-checkpoint approximation (superseded) | Full 20-year (corrected) |
|---|---|---|
| Deloitte | $1.83/MWh | **$35.54/MWh** |
| EIA | **-$5.88/MWh** | **$29.01/MWh** |
| Hughes | $3.08/MWh | **$35.91/MWh** |

**Mechanism**: the 4-checkpoint approximation counted cost at only 4
discrete years while still crediting the *full* 30-year terminal value
against that badly undercounted total. The EIA tier's negative SLCOE —
raised and investigated repeatedly across this session as a genuine,
if uncomfortable, finding — turns out to have been entirely an artifact
of this undercounting, not a real result. With the full 20-year cost
stream properly captured (16 additional years of real gas capex and
fuel cost that Scenario 2 actually incurs), the EIA tier is an ordinary
positive number.

**Terminal value, corrected to include solar/Na-power** (previously gas
only): gas $9.676B, solar $2.219B, Na-power $0.172B — **total $12.067B**
(down from a superseded, gas-only $13.964B, since properly distributing
capex across the full 20-year vintage stream — rather than concentrating
it artificially at 4 points — reduces how much sits in the
highly-creditable late-vintage position).

**Downstream implications, not yet resolved**: every comparison built on
the superseded 4-checkpoint Scenario 2 figures is now invalid, including
Scenario 1B vs. Scenario 2 framing (Appendix N) and the Social Cost of
Carbon/Greenhouse Gases and Health Impacts work (Appendix D), which drew
on the same 4-checkpoint dispatch data. Both are flagged for a follow-up
correction pass, deliberately not done in the same turn as this one per
direct user direction (pause, document, come back).

Scripts: `solve_scenario2_intermediate_years.py`,
`solve_scenario2_2026_2029.py`,
`compute_scenario2_gas_replacement_20yr.py`,
`compute_scenario2_20yr_full_slcoe.py`.

### C.13 Solar Degradation — a Gap Present Since Scenario 2's First Solve

**The gap**: Scenario 1/1B's solar is vintage-tracked and properly
degraded (0.5%/yr, `solar_degradation_factor()`) throughout this
project. Scenario 2's statutory VCEA solar target (`vcea_solar_mw`) was
used directly, undegraded, in every dispatch solve built this session —
only its small pre-2026 legacy baseline (`exist_solar`) was ever
degraded. Confirmed directly in code:
`solar_degradation_factor()` is referenced only within `lp_model.py`'s
own LP problem-builder and `exist_solar_mw()` — never in `driver.py` or
`solve_scenario2.py`. Flagged by direct user question ("would be quite
obvious to a modeler").

**Fix**: vintage-decomposed the statutory nameplate solar schedule into
yearly fresh increments — critically, using the SIMPLE year-over-year
difference in the statutory MW figure itself (not Scenario 1's
degradation-backed-out approach), since VCEA's targets are raw,
undegraded cumulative nameplate build requirements by construction, not
LP-derived totals that already implicitly reflect degradation the way
Scenario 1's do. Each vintage then degraded forward to compute each
year's effective (as opposed to nameplate) capacity, used in place of
the raw statutory figure for dispatch and worst-hour CCGT sizing;
nameplate MW is unchanged and still used for capex accounting (VCEA
compliance is a nameplate-installed requirement, not an effective-output
one).

| Year | Nameplate (MW) | Effective (MW) | Shortfall |
|---|---|---|---|
| 2030 | 10,000 | 9,865.9 | 1.3% |
| 2035 | 16,100 | 15,661.0 | 2.7% |
| 2040 | 16,100 | 15,273.3 | 5.1% |
| 2045 | 16,100 | 14,895.3 | 7.5% |

**Result — a small, genuine correction, not a dramatic one**: the
worst-hour CCGT-sizing calculation (`peak_g`) is completely unaffected
at every year — the worst hour is an overnight/zero-solar hour, so
`vcea_solar_mw * solar_cf` is zero at that hour regardless of which MW
figure is used, meaning capacity requirements and the resulting capex
stream are essentially unchanged. Annual gas *generation* (all other
hours, where solar is actually producing) rises modestly at every year
(e.g. 2045: 107,020→109,359 GWh; gas share 57.5%→58.7%), since less
actual solar output means slightly more must come from gas across the
year.

| | Superseded (undegraded) | Corrected (degraded) |
|---|---|---|
| Deloitte SLCOE | $35.54/MWh | $35.50/MWh |
| EIA SLCOE | $29.01/MWh | $28.96/MWh |
| Hughes SLCOE | $35.91/MWh | $35.87/MWh |
| Social Cost of Carbon | $57.12/MWh | $57.25/MWh |
| Health Impacts | $3.52/MWh | $3.52/MWh |

All 20 years of dispatch re-solved and all downstream figures (gas
capex, terminal value, SLCOE, Social Cost of Carbon/Health Impacts)
recomputed against the corrected data — not a partial patch. Terminal
value: gas $9.676B→$10.060B, total $12.067B→$12.451B.

Scripts: `fix_scenario2_solar_degradation.py`,
`resolve_scenario2_20yr_degraded_solar.py` (re-solves all 20 years),
plus re-runs of `compute_scenario2_gas_replacement_20yr.py`,
`compute_scenario2_20yr_full_slcoe.py`, and
`compute_scenario2_tier12_20yr.py` against the corrected dispatch data.


## Appendix D — Tiered Social Cost Analysis

*(Originally carried forward from the existing white paper section's A.4
as a brief framework summary; substantially expanded this session with
sourced rates, worked calculations, and results for Scenarios 1 and 2.
Retitled from "Framework" to "Analysis" since this section now contains
applied results, not just a methodology description.)*

### D.1 Framework and Sourcing

Three-tier externality framework: Social Cost of Carbon / Social Cost
of Greenhouse Gases (climate, monetized — renamed this session per
direct user direction, replacing the earlier internal "Tier 1"
shorthand as the primary label; #9 has the full naming history and
statutory reasoning), Health Impacts (regional health, monetized;
formerly "Tier 2"), Tier 3 (air toxics, deliberately qualitative —
never monetized or summed into either dollar total; this label is
retained as-is, per direct user direction).

**Social Cost of Carbon / Social Cost of Greenhouse Gases.** Rates
sourced directly from EPA's *Report on the Social Cost of Greenhouse
Gases: Estimates Incorporating Recent Scientific Advances* (November
2023, Docket EPA-HQ-OAR-2021-0317), fetched and read directly this
session — Table ES.1, 2.0% near-term Ramsey discount rate, 2020 dollars
per metric ton:

| Emission year | SC-CO2 | SC-CH4 | SC-N2O |
|---|---|---|---|
| 2020 | $190 | $1,600 | $54,000 |
| 2030 | $230 | $2,400 | $66,000 |
| 2040 | $270 | $3,300 | $79,000 |
| 2050 | $310 | $4,200 | $93,000 |

2035 and 2045 rates linearly interpolated between adjacent EPA anchor
points (not extrapolated from a different vintage):

| Checkpoint | SC-CO2 | SC-CH4 | SC-N2O |
|---|---|---|---|
| 2030 | $230 | $2,400 | $66,000 |
| 2035 | $250 | $2,850 | $72,500 |
| 2040 | $270 | $3,300 | $79,000 |
| 2045 | $290 | $3,750 | $86,000 |

**CPI re-basing, this session**: the table above is EPA's own 2020$;
this project's WACC/SLCOE use a 2026 base year. Re-based to 2026$ using
a BLS-sourced deflator of 1.2902 (29.02% cumulative inflation, 2020
annual average CPI-U of 258.811 to July 2026's 333.918, the most recent
available) before use in any calculation — full sourcing and the second,
related BenMAP correction in #9.

**Correction to this project's own prior sourcing**: `whitepaper_draft.md`
(an earlier, separate draft of the actual white paper document, distinct
from this working appendix set) carried a SC-CO2 schedule of $190 (2026)
→ $230 (2035) → $280 (2045) → $310 (2050) — internally consistent-looking,
but its year labels are shifted roughly 5-6 years from EPA's own table
(EPA has $190 at 2020 and $230 at 2030, not 2026/2035). That schedule's
specific $/MWh results ($74-228/MWh across scenarios) are themselves
stale, from an earlier, different modeling pass predating this project's
rigorous LP work — not reused here. This appendix uses EPA's own table
directly, interpolated to our exact checkpoint years, rather than
propagating the earlier, shifted schedule forward.

**Emission factors**: AP-42 Compilation of Air Pollutant Emission
Factors, Vol. I, Section 3.1, Stationary Gas Turbines (C028), natural
gas-fired, uncontrolled: CO2 110 lb/MMBtu, CH4 (combustion) 0.0086
lb/MMBtu, N2O 0.003 lb/MMBtu (low-confidence rating in the source),
PM2.5 0.0066 lb/MMBtu, SO2 0.0034 lb/MMBtu, NOx 0.32 lb/MMBtu
(uncontrolled) or 0.099 lb/MMBtu (lean-premix/DLN, low-NOx combustors).

**Upstream methane leakage**: 2.3% of gas produced escapes unburned
before combustion (`whitepaper_draft.md` assumption, not independently
re-verified this session — carried forward as a disclosed, unverified
input). Converted via 1.037 MMBtu/Mcf energy content and an approximate
19.3 kg CH4/Mcf pipeline-gas density.

**Health Impacts — regional health.** EPA Sector-based PM2.5 Benefit-per-Ton
(BenMAP), Electricity Generating Units category, 2016 dollars (C033,
verified full table read directly): PM2.5 $140,000/ton, SO2 $40,000/ton,
NOx $6,000/ton — 40-60% lower than the area-source figures used
elsewhere in this project, consistent with tall-stack dispersion reducing
ground-level concentration impact per ton. **CPI re-based to 2026$ this
session** (see #9): deflator 1.3913 (39.13% cumulative, 2016 annual
average CPI-U of 240.007 to July 2026's 333.918) — a larger correction
than the SC-GHG table's own, given the ten-year gap to this rate's own
2016$ vintage.

**NOx factor selection** (this session's direction, applied to both
scenarios): uncontrolled (0.32 lb/MMBtu) for dispatch served by the
existing fleet, DLN/low-NOx (0.099 lb/MMBtu) for dispatch served by
new-build capacity, blended by each checkpoint's existing/new MW capacity
share as an energy-share proxy.

**Tier 3 — air toxics, qualitative only.** Formaldehyde (0.00071
lb/MMBtu) and benzene (0.000012 lb/MMBtu), both AP-42 (C028). Both are
IARC Group 1 confirmed human carcinogens (C029). Formaldehyde carries a
turbine-specific NESHAP limit of 91 ppbvd at 15% O2 (40 CFR Part 63
Subpart YYYY, C030). EPRI field testing (GE LM6000 simple-cycle turbine
with SCR and oxidation catalyst) found formaldehyde emissions rise
specifically at less-than-80%-load operation (C031) — directly relevant
to any fleet, like Scenario 2's new CT build, that is sized for
intermittent, partial-load, peaking duty rather than steady baseload
operation. Nationally, roughly half of average air-toxics cancer risk is
attributed to formaldehyde, though ~90% of that is from atmospheric
secondary formation rather than direct source emission (2014 NATA, C032)
— presented as national context, not a fleet-specific attribution claim.
Deliberately never monetized or combined with the Social Cost of Carbon/
Greenhouse Gases or Health Impacts dollar totals, per this project's
standing convention.

**Tier 3 update, literature search performed this session (C094-C097)**:
a follow-up search for recent developments surfaced several genuinely
new items, all early-to-mid 2026 unless noted, none monetized here,
consistent with the standing Tier 3 convention.

- **EPA finalized NSPS amendments for stationary combustion turbines**,
  effective January 15, 2026 (C094) — directly confirms combustion
  controls (DLN) as the "best system of emission reduction" for new,
  modified, or reconstructed turbines, with SCR added for one
  subcategory. Current, direct regulatory confirmation of this analysis's
  own new-build-is-DLN assumption (D.2), not merely an inference from
  industry norms.
- **Two new, independent Virginia-specific academic sources** (C095):
  a VCU study (Feb 2026, Pitt et al.) spatially mapping air pollution
  from 138 Northern Virginia data centers, finding their aggregate
  emissions — primarily from backup diesel generators, a different
  source category than this analysis's CT/CCGT fleet — can exceed
  nearby gas power plants'; and a first-of-its-kind peer-reviewed review
  (Frontiers in Climate, Feb 2026, Gour/Ortiz/Maibach, George Mason)
  of Virginia data center health implications broadly (air, water,
  noise, land use).
- **A governance finding, not an emissions finding, but relevant
  context**: a POLITICO/E&E News investigation (July 2026, C096), based
  on internal emails obtained via public records request, found Virginia
  DEQ moved quickly to challenge the Cork/Dominici Vantage health study
  (C024) after it was shared with regulators, rather than treating it as
  independent input — relevant to how much weight the regulatory
  environment itself places on this category of finding, distinct from
  the finding's own substance.
- **A new, previously untracked project**: Remington Technology Park
  (Fauquier County) is reportedly proposing 13 on-site gas turbines
  (C096) — noted as an example of the broader trend continuing, not
  incorporated into this project's own plant roster or dispatch modeling.
- **A new, specifically air-permit-focused legal challenge**: the
  Southern Environmental Law Center has filed an appeal against the
  Chesterfield Energy Reliability Center's DEQ air permit specifically
  (C096) — distinct from, and in addition to, the SCC siting-approval
  reconsideration already tracked in this project (Appendix A.8.5).
- **Not "lately" by this project's own window, but not previously
  cited**: an EDF report (Sept 2024, C097) found EPA's own national Risk
  and Technology Review modeled only 15% of actual gas-turbine EGUs
  operating nationally (273 of an estimated ~1,750) — a genuine gap in
  the federal regulatory analysis's own scope, suggesting the true
  national air-toxics burden from gas turbines is understated in EPA's
  own official review, not just in this project's necessarily partial
  treatment.

None of the above changes any Social Cost of Carbon/Greenhouse Gases or
Health Impacts monetized figure or is intended to; presented as
qualitative context update only, per the standing Tier 3 convention.

### D.2 Existing/New Fleet Split by Scenario, and Plant-Specific NOx Controls

Applying the checkpoint-solved hourly gas dispatch, split at the 70th-
percentile load-duration threshold (this session's established baseload/
peaker method, Appendix C.10) to separate CCGT-rate dispatch (6.4
MMBtu/MWh) from CT-rate dispatch (9.5 MMBtu/MWh):

**Scenario 1**: **existing/new MW share corrected this session,
superseding an earlier "zero new-build throughout" claim.** That earlier
claim held under Scenario 1's own pre-correction dispatch (verified
against the demand basis and dispatch mechanism in use at the time), but
was checked directly against this session's own corrected dispatch
(demand basis, SLCR, reserve margin — Internal Debugging Log #24/#26/
#29) before being relied on further, rather than carried forward
unchecked. It no longer holds: corrected gas dispatch reaches the full
capacity cap — existing fleet plus the 2,862 MW overhaul/retain pool —
at every checkpoint, not just the existing-fleet-only bound. The
existing/new split is now genuinely `schedule_b_baseline_mw(year)` /
2,862.0 MW, giving an existing share of 76.6% for 2026-2044 (9,362 /
12,224) and 39.4% at 2045 (1,860 / 4,722, following the VCEA-driven
Schedule B step-down) — not 100%/0% as previously stated.

**Scenario 2**: uses the corrected, individual-plant-retirement-tracked
existing/new split from Appendix C.10:

| Year | Existing share | New share |
|---|---|---|
| 2030 | 72% | 28% |
| 2035 | 45% | 55% |
| 2040 | 38% | 62% |
| 2045 | 15% | 85% |

**Plant-specific NOx control classification (this session, replacing an
earlier existing/new binary assumption)**: a direct literature search,
prompted by user question, found that the "existing = 100% uncontrolled"
assumption used in an earlier pass of this analysis materially
overstated actual NOx emissions — most of the existing CCGT fleet is
already DLN-equipped, in several cases via documented retrofit, not
original-build assumption:

| Plant | MW | NOx control | Evidence basis |
|---|---|---|---|
| Greensville County | 1,605 | DLN | Confirmed — DEQ/RBLC permit records explicitly cite dry low-NOx burners + SCR |
| Possum Point | 573 | DLN | Confirmed — GE press release: Dominion installed "GE DLN combustion hardware" in a 2015 Advanced Gas Path retrofit at this plant specifically |
| Bear Garden | 622 | DLN | Confirmed — same GE press release, same 2015 AGP/DLN retrofit program |
| Brunswick County | 1,376 | DLN | Strong inference — same Dominion program, era (2016), and M501J turbine family as Greensville; not independently confirmed by name |
| Warren County | 1,349 | DLN | Strong inference — same basis as Brunswick County |
| Potomac Energy Center | 793 | DLN | Strong inference — repeatedly described as "advanced emissions-control technology," modern (2017) Siemens SGT6-5000F turbines, a DLN-standard class |
| Tenaska Virginia | 975 | DLN | Weak inference only — no plant-specific statement found; GE 7F.04 turbines, 2004 commissioning, an era when DLN was already standard industry practice for new CCGT, but this is an industry-norm inference, not a confirmed fact about this specific plant |
| Chesterfield, Doswell, Ladysmith, Marsh Run, Louisa, Wolf Hills, Remington | 386/901/782/550/525/285/619 | Uncontrolled (conservative default) | No evidence found either way. These are the older, lower-utilization simple-cycle peakers (Ladysmith's EOH of 16,718 the clearest example) where an expensive DLN retrofit is least likely to have been economically justified — an inference, not a finding |

**Resulting existing-fleet blended NOx factor, by checkpoint** (weighted
by which specific plants remain operating, per their own retirement
year, not a flat existing/new split):

| Year | Blended existing NOx EF (lb/MMBtu) |
|---|---|
| 2030 | 0.170 |
| 2035 | 0.154 |
| 2040 | 0.154 |
| 2045 | 0.099 (only Greensville, Brunswick, Potomac Energy Center remain — all DLN) |

Substantially below the uncontrolled factor (0.32) used in the prior
pass of this analysis, and approaching the DLN factor (0.099) directly
by 2045 as the DLN-confirmed plants increasingly dominate the surviving
fleet.

### D.3 Results

**MAJOR CORRECTION (this session)**: both scenarios' own figures below
are now fully current — Scenario 1's own from an earlier pass this
session (Internal Debugging Log #24/#26/#29/#32/#35/#36), Scenario 2's
own from a full dispatch and downstream rebuild completed this same
session (#38-#42), including two simultaneous-dispatch fixes (Bath,
then Na, the latter requiring a direct literature search and KKT/
reduced-cost verification before resolving), a reserve-margin check
(passes at all four checkpoints with substantial margin, no build
adjustment needed — a genuinely different finding from Scenario 1,
where the LP had to be explicitly constrained), and a corrected
existing/new-fleet split for the NOx-blend calculation (an initial pass
wrongly assumed 100% new-build, caught and corrected before presenting
results here). Both EPA rate tables re-based to this project's 2026
base year (#9/#35) for both scenarios.

**Emissions and monetized cost, by checkpoint** (both scenarios shown
at their 4 checkpoints for table continuity; both scenarios' own PV
figures below reflect the genuine full 20-year calculation, not an
extrapolation from these four rows alone):

| Scenario | Year | Gas (MWh) | CO2 (t) | CH4 total (t) | N2O (t) | Social Cost of Carbon ($M) | Health Impacts ($M) |
|---|---|---|---|---|---|---|---|
| 1 | 2030 | 48,458,654 | 20,827,010 | 167,539.6 | 568.01 | 6,180.3 | 521.3 |
| 1 | 2035 | 44,051,286 | 23,016,797 | 185,155.0 | 627.73 | 7,424.1 | 554.4 |
| 1 | 2040 | 28,253,645 | 14,762,530 | 118,754.9 | 402.61 | 5,142.6 | 355.6 |
| 1 | 2045 | 188,877 | 98,688 | 793.9 | 2.69 | 36.9 | 2.1 |
| 2 | 2030 | 43,859,100 | ~22,918,000 | ~184,300 | ~625 | ~6,546.2 | ~501.3 |
| 2 | 2035 | 58,737,900 | ~30,700,000 | ~247,000 | ~837 | ~9,670.3 | ~621.5 |
| 2 | 2040 | 84,433,900 | ~44,140,000 | ~355,000 | ~1,203 | ~13,760.8 | ~802.9 |
| 2 | 2045 | 109,388,400 | ~57,180,000 | ~460,000 | ~1,559 | ~18,353.0 | ~922.7 |

Scenario 2's own CO2/CH4/N2O tons above are shown approximately (~),
back-calculated from this session's own SC-carbon/health dollar figures
rather than re-extracted from the raw hourly arrays as a separate step
— the dollar figures themselves are the genuinely verified, directly-
computed values; the tons are provided for row-format consistency with
Scenario 1's own display above, not independently re-verified to the
same precision.

**Present value (WACC 4.5%, base year 2026)** — all figures below are
the genuine, full-20-year total for each scenario, not derived from the
four-checkpoint table above. **Social Cost of Carbon (statutory,
CO2-only) shown as its own column, separate from Social Cost of
Greenhouse Gases (the broader, multi-gas figure) — per Virginia Code
§56-598(2)(d)/§56-585.1(A)(6)'s own requirement that these be reported
separately, not combined into one (#9's own full statutory reasoning)**:

| Scenario | PV Social Cost of Carbon | $/MWh | PV Social Cost of GHG | $/MWh | PV Health Impacts | $/MWh |
|---|---|---|---|---|---|---|
| 1 | $71.701B | $39.84 | $78.577B | $43.66 | $5.740B | $3.19 |
| 1B | $72.329B | $40.19 | $79.276B | $44.05 | $5.775B | $3.21 |
| 2 | $119.071B | $66.16 | $131.090B | $72.84 | $8.486B | $4.72 |

Scenario 1B's own Social Cost of Carbon and Social Cost of GHG sit only
marginally above Scenario 1's own — consistent with N.4/N.5's own
finding that Scenario 1B's relaxed 5%-gas ceiling at 2045 is largely
moot in practice, since the physical gas fleet's own hard capacity cap
binds before the statutory percentage does. Scenario 2's much higher
gas share (39-59%, sustained throughout the full window, vs. both
Scenario 1 and 1B's decline to near-zero by 2045) shows up almost
entirely in both climate figures — roughly 65-70% higher than Scenario
1/1B's own totals — while Health Impacts, though still meaningfully
higher for Scenario 2, diverges less sharply, since it depends on
short-lived pollutants tied to the existing-fleet NOx blend rather than
cumulative GHG stock, and all three share much of the same underlying
existing-plant roster.

**Total societal SLCOE** (direct financial SLCOE + Social Cost of
Greenhouse Gases + Health Impacts; Tier 3 excluded from the dollar
total by design; the broader SC-GHG figure used here, not the narrower
SC-CO2, since this line is meant to capture the full climate cost).
**Scenario 2's own direct SLCOE below was corrected after this table
was first built** — a real, confirmed CCGT capex bug (a stale $1,775/kW
constant used instead of this project's own correct, cross-validated
$3,000/kW figure, a 1.69x understatement on Scenario 2's single largest
cost component) was found and fixed; see Internal Debugging Log #49 for
the full incident and the centralized `assumptions.py` module built in
response to it:

| Scenario | Direct SLCOE | + Social Cost of GHG + Health Impacts | Total societal |
|---|---|---|---|
| 1 | $42.45/MWh | +$46.85 | **$89.30/MWh** |
| 1B | $42.14/MWh | +$47.26 | **$89.40/MWh** |
| 2 (Deloitte gas) | $48.99/MWh | +$77.56 | **$126.55/MWh** |
| 2 (EIA gas) | $43.77/MWh | +$77.56 | **$121.33/MWh** |
| 2 (Hughes gas) | $49.43/MWh | +$77.56 | **$126.99/MWh** |

**A genuinely important pattern, worth stating plainly rather than
smoothing over**: on a direct-financial basis, Scenario 2 now sits
*above* Scenario 1 under all three gas cases — the corrected CCGT
capex removed what had briefly looked like a direct-cost advantage for
Scenario 2 under two of the three gas cases; that finding did not
survive the capex correction and should not be cited. Scenario 2's
total societal cost remains substantially *higher* than Scenario 1's
(or 1B's) under all three gas cases — now $121-127/MWh vs.
$89.30-89.40/MWh, a wider gap than previously reported, not a
narrower one — driven by both the direct-cost gap (now real, not
narrowed) and the climate-cost gap (unchanged) working in the same
direction, rather than partially offsetting as the pre-correction
figures suggested. Scenario 1 and Scenario 1B remain essentially tied
on a total-societal basis (within $0.10/MWh), consistent with N.5's own
finding — unaffected by the Scenario 2 correction, since neither uses
CCGT capex at all. **Scenario 1's own total-societal advantage over
Scenario 2 is real, now fully verified on all sides including this
correction, and larger than this project's own most recent prior
estimate, not smaller.** The underlying reason has not changed from
this project's own original characterization: Scenario 2 sustains
substantial gas generation throughout the full 20-year window by
statutory design, while Scenario 1 (and, in practice, 1B too)
approaches true zero by 2045 — both the direct-cost and climate-cost
gaps between Scenario 1/1B and Scenario 2 are real and now consistently
point the same direction.

**Total societal SLCOE, with RGGI folded into the direct-cost side**
(new, this session — closes the open item tracked in Appendix P.4/entry
#43, where RGGI had been built into each scenario's own direct SLCOE
but never carried through into a distinct total-societal-with-RGGI
figure). RGGI is a real, currently-billed carbon-market cost, additive
to — not a substitute for — the Social Cost of GHG externality
estimate above, which represents the broader, un-priced societal value
of the same emissions rather than what a generator is actually charged
per ton; the two are shown combined here for a genuinely complete
"most costs accounted for" figure, not because either alone was
insufficient on its own terms:

| Scenario | Direct SLCOE (w/ RGGI) | + Social Cost of GHG + Health Impacts | Total societal (w/ RGGI) |
|---|---|---|---|
| 1 | $46.22/MWh | +$46.85 | **$93.07/MWh** |
| 1B | $45.94/MWh | +$47.26 | **$93.20/MWh** |
| 2 (Deloitte gas) | $56.70/MWh | +$77.56 | **$134.26/MWh** |
| 2 (EIA gas) | $51.48/MWh | +$77.56 | **$129.04/MWh** |
| 2 (Hughes gas) | $57.15/MWh | +$77.56 | **$134.71/MWh** |

The ordering and the size of the gap between Scenario 1/1B and Scenario
2 are essentially unchanged by including RGGI — RGGI adds roughly
$3.8-4.5/MWh to every scenario's own total (proportional to each
scenario's own gas volume, largest in absolute terms for Scenario 2)
without altering which pathway costs more or by roughly how much.

### D.4 Disclosed Gaps and Limitations

- **Scenario 2's own approximate CO2/CH4/N2O tons in D.3's own table**
  (back-calculated from the SC-carbon/health dollar figures, not
  independently re-extracted from the raw hourly arrays to the same
  precision as Scenario 1's own row): a minor, disclosed precision gap,
  not a gap in the dollar figures themselves, which are the genuinely
  verified values.
- **Plant-specific NOx classification confidence varies** (D.2): direct
  evidence exists for Greensville County and Possum Point/Bear Garden
  (the latter two via a specifically-named 2015 retrofit program);
  Brunswick County, Warren County, and Potomac Energy Center rest on
  strong circumstantial inference (same era, vendor, or program) rather
  than plant-specific confirmation; Tenaska Virginia rests on weak,
  industry-norm inference only. The uncontrolled classification for the
  older peaker fleet (Chesterfield, Doswell, Ladysmith, Marsh Run,
  Louisa, Wolf Hills) is an absence-of-evidence default, not a confirmed
  finding — a genuine retrofit at any of these plants would lower the
  Health Impacts figure further.

- **"Density/frequency sensitivity" for Health Impacts**: referenced in
  this section's original brief summary, but the specific adjustment
  formula was not recoverable from any source located this session,
  despite a direct literature search. The general concept (benefit-per-
  ton varies meaningfully by source location and population density) is
  well-established in the literature (e.g. the EGU-specific vs.
  area-source distinction already embedded in C033's own figures), but
  this analysis uses EPA's flat, national EGU rates rather than a
  location-adjusted version. A genuine limitation, not a judgment call.
- **Upstream CH4 leakage (2.3%)** is carried forward from
  `whitepaper_draft.md` without independent re-verification this
  session.
- **NOx existing/new blending** uses MW capacity share as a proxy for
  energy-dispatch share, not a true hourly-resolved attribution (the LP's
  gas dispatch variable does not itself distinguish which physical unit
  serves a given hour).
- **N2O** is now fully sourced (this session, resolving a prior gap) —
  no remaining omission on this point.
- Tier 3 remains deliberately unmonetized; the qualitative findings in
  D.1 should not be read as implying any specific dollar magnitude.

---

## Appendix E — DER Owner Economics

Ownership-split allocation methodology (80/10/10 utility/rooftop/parking-lot),
the Recommended VA Program composition (locational value adder, D-REC, and
event-based compensation), and the floor-price transition structure are
*(carried forward from the existing white paper section's A.5 and C.2-C.5,
relabeled and consolidated. No content changes.)*

**ELCC/capacity treatment — UPDATED, no longer "no content changes" (2026-08-16).**
VPP/owner-economics capacity revenue was originally computed using illustrative
flat placeholder ELCC assumptions (solar 40%, storage 95%) rather than PJM's
actual published class ratings. This has since been corrected in the
`DER_Owner_Economics` workbook tab itself (marked inline as "[CORRECTED]... 
DISCLOSED FIX APPLIED") to use PJM's real, current 2026/27 BRA class ratings
(see A.12 for the authoritative sourced table: Tracking Solar 11%, 4-hr
Storage 50%, 6-hr Storage 58%, 8-hr Storage 62% -- all materially lower than
the original placeholders). This appendix text had not yet caught up to that
workbook correction until this update; it now points to A.12 as the single
source of truth for current ELCC values rather than restating them here, to
avoid the two drifting out of sync again as PJM's own published ratings
change year to year (the 2026/27 values above already differ from 2025/26 --
see A.12's full BRA-over-BRA table).

Both directions of this correction push the same way: since capacity revenue
is a subtraction from cost (utility side) or an addition to cash flow (owner
side), the flat placeholders overstated capacity revenue in both scenarios.
Correcting to PJM's real, lower figures raises Scenario 1's SLCOE (less
capacity revenue offsetting new-build capex) and pushes Scenario 3's owner
NPV further negative (a smaller capacity-credit component on top of the
already-negative wholesale-compensation finding), not less negative.

**Not yet done, flagged rather than silently assumed away:** PJM's real ELCC
is not flat over a 25-year horizon either -- it declines with cumulative
penetration (see A.12's citation to Advanced Energy United/Ascend Analytics:
storage ELCC potentially falling from ~57% toward ~20% within a single BRA
cycle as more storage clears the market; NREL's own national projections
show solar's median capacity credit falling from ~21% in 2026 to ~3.5% by
2050). Given this project's own Scenario 1 storage buildout is exactly the
kind of large-scale addition that would drive this decline, using a single
corrected-but-still-constant ELCC value across the full 25-year horizon is a
real, disclosed simplification -- directionally conservative in the sense
that it likely still overstates capacity revenue in the model's later years,
compounding rather than offsetting the corrections above. A fully rigorous
treatment would tie ELCC to this project's own cumulative buildout at each
checkpoint rather than holding it constant; this has not been built.

**Double-counting verification (2026-08-16, prompted by a direct question
about whether owner/farmer-side benefits are counted twice into the
ratepayer-facing SLCOE).** This project's stated priority is ratepayer
benefit as the primary analysis; DER-owner economics (this appendix) and
agrivoltaic farmer lease income (the separate Agrivoltaics appendix) are
explicitly secondary, informational content, not intended to net against
or modify the primary ratepayer number. Verified directly against the
workbook rather than assumed: **zero formula cross-references exist in
either direction between the `Scenario3` and `DER_Owner_Economics` tabs.**
`DER_Owner_Economics`'s capacity payments, VPP revenue, and owner NPV
calculations are structurally isolated from Scenario3's ratepayer-facing
SLCOE/Net Cost -- there is no live double-counting mechanism, because
these are two fully independent calculations, not one feeding the other.
This is the correct architecture, not a lucky accident: Scenario3's core
SLCOE reflects the total physical system cost (how much solar/storage
gets built and what it costs), which does not change based on who legally
owns which share of the 80/10/10 split -- only `DER_Owner_Economics`'s
distributional question (what would a hypothetical owner's cash flow look
like) is affected by ownership, and that question was never wired back
into the ratepayer number.

**Agrivoltaic vs. non-agrivoltaic lease treatment: already satisfied by
construction, no fix required.** Per explicit project direction, agrivoltaic
leases should be treated identically to non-agrivoltaic leases from the
ratepayer perspective. Verified: the model's solar O&M/land-cost assumption
($24/kW-yr, B.2) is a single, blanket figure applied uniformly to all
solar regardless of agrivoltaic status -- there is no agrivoltaic-specific
adjustment anywhere in the LP or the ratepayer-facing SLCOE calculation.
Agrivoltaic status is farmer-benefit-relevant information (the separate
Agrivoltaics appendix), not a ratepayer-cost differentiator, and the model
already reflects that correctly.

**Owner-side wholesale arbitrage revenue is a transfer payment, not new
system value -- a framing clarification, not a numerical fix.** Per
explicit project direction: wholesale arbitrage revenue captured by a DER
owner represents value that "would go to some other generator anyway" if
this specific DER did not exist -- a transfer among generation market
participants determined by which resource happens to serve the marginal
MWh, not new value the DER's existence creates. `DER_Owner_Economics`'s
owner-revenue calculations (Section H) use a wholesale-equivalent energy
price without this distinction stated explicitly; a reader could
otherwise misread owner NPV as representing new societal/system value
rather than a distributional transfer. This is a different mechanism from
the NSPM's wholesale market price effects (MPE) principle above (MPE
concerns how demand reduction shifts the clearing price paid by ALL
buyers -- a real, additive system effect; this concerns WHICH specific
generator captures an existing margin -- a transfer). Both are legitimate
BCA considerations under NSPM guidance, but they should not be conflated
with each other, and neither changes any figure already in this model --
only how the owner-side numbers should be interpreted.

**Regulatory basis for VPP/wholesale-market-participation assumptions:**
FERC Order No. 2222 requires all RTOs/ISOs to permit DER aggregation
participation in wholesale markets. For PJM specifically (Docket
ER22-962), FERC's own explainer documents a staged implementation: Capacity
Market participation targeted for February 1, 2027; Energy and Ancillary
Services for February 1, 2028. This timeline has a real history of
slippage (originally targeted February 2026, delayed twice), so should be
read as PJM's current target as of this writing rather than a firm
commitment -- but it is the actual regulatory basis for why VPP/wholesale
participation is a realistic modeling assumption for PJM-territory DERs
going forward, not merely a hopeful construct.

---

## Appendix F — Known Limitations

*(Carried forward from the existing white paper section's D.2, relabeled.
No content changes — this is the annual-model-era limitations list; note it
predates and does not yet reflect this session's bug findings, which live in
Appendix A.7 instead.)*

---

## Appendices G+ — DER Interconnection and Market Structure (placeholder)

*(Source: `Virginia_Energy_Plan_Input.docx`. Full text not yet pulled into
this document. Original Appendix C, "DER Energy Calculations," has been
removed per prior agreement. Listed here in their original relative order,
renumbered starting from G.)*

- **G** — Direct Transfer Trip (DTT) Considerations
- **H** — Why Wholesale Prices Vary Across Dominion's Transmission Network
- **I** — Approaches by Other Utilities (NYISO and others)
- **J** — DER Circuit Analysis Tools (hosting-capacity software)
- **K** — DER Background and the 6% Cap / Reverse-Flow Challenges
- **L** — *(content not yet reviewed — original Appendix G)*

---

## Appendix N — Scenario 1B

Scenario 1B: identical to Scenario 1 (utility solar, colocated firming
storage, PJM market arbitrage) for 2026-2044, full VCEA/RPS compliance
throughout that period. Diverges only at 2045+, where up to 5% gas is
permitted instead of chasing VCEA's ~100% mandate — testing whether a
small, deliberate compliance exception avoids the expensive marginal
clean-capacity buildout Scenario 1's own 2045 checkpoint required.

### N.1 Existing Fleet Capacity Bound, and Its Reconciliation

Scenario 1's 2045 checkpoint solves respect a hard gas capacity bound of
`schedule_b_baseline_mw(2045)` (1,860 MW, the VCEA-driven Schedule B
step-down — Chesterfield, Doswell, Possum Point only) plus the 2,862 MW
peaker pool (`driver.py`'s `POOL`) — 4,722 MW total. An initial check
this session found this bound might be stale, based on a generation-data
note ("zero output since Dec 2024, cause unconfirmed") for all 8 pool
plants. Direct verification against each owner's own current site —
Dominion (for Remington, Gordonsville, Elizabeth River, Darbytown,
Gravel Neck), ODEC (for Marsh Run, Louisa), and Middle River Power (for
Wolf Hills) — confirmed all 8 plants are still listed as active
facilities (C098-C100). The 4,722 MW bound
stands as originally established; no adjustment needed for Scenario 1B
specifically (this same correction was separately, and more
consequentially, applied to Scenario 2's Appendix C.10, Activity Tracker
item 75).

### N.2 Capacity Sweep: Finding the Cost-Minimizing New-Build Size

**A methodological pitfall, caught and corrected**: an initial approach
solved the 2045 checkpoint with the gas capacity bound removed entirely,
treating the LP's own chosen peak (17,704 MW) as the required new-build
size (12,982 MW beyond the existing fleet). This significantly
overstated the true requirement — the uncapped LP has no capex penalty
for gas within its own objective (only marginal fuel cost), so it had no
reason to economize on capacity once given free rein.

**Corrected approach**: swept multiple capacity caps, computing true
total system cost (LP objective + externally-priced new-build capex) at
each:

| Total gas capacity | New build | @ $1,200/kW | @ $2,000/kW | @ $2,500/kW | @ $3,000/kW |
|---|---|---|---|---|---|
| 4,722 MW (existing only) | 0 | $10,065.2M | $10,065.2M | $10,065.2M | $10,065.2M |
| 6,000 MW | 1,278 MW | $9,406.5M | **$9,469.3M** | **$9,508.5M** | **$9,547.7M** |
| 7,000 MW | 2,278 MW | **$9,362.2M** | $9,474.0M | $9,544.0M | $9,613.9M |
| 8,000 MW | 3,278 MW | $9,416.2M | $9,577.2M | $9,677.8M | $9,778.5M |
| 12,000 MW | 7,278 MW | $9,722.8M | $10,080.3M | $10,303.7M | $10,527.1M |
| 17,704 MW | 12,982 MW | $10,182.9M | $10,820.5M | $11,219.0M | $11,617.5M |

The cost-minimizing point holds remarkably stable at **6,000-7,000 MW
total (1,278-2,278 MW new)** across the full $1,200-3,000/kW capex range
tested — not sensitive to exactly where within that band the true
current simple-cycle rate falls. **Locked in: 6,000 MW total capacity
(1,278 MW new simple-cycle CT), $2,000/kW central capex assumption**
(the midpoint of the tested range, consistent with this project's own
Wood Mackenzie-sourced equipment-to-full-project-cost ratio for CCGT,
C.6, extended here to simple-cycle by the same underlying supply-chain
logic, C101).

### N.3 Turbine Procurement Lead Time: Feasibility Check

Confirmed current gas turbine lead times (C102-C105): 5-7 years for
heavy-duty CCGT frames (GE Vernova, Siemens, Mitsubishi all report
multi-year backlogs into 2029-2031), but materially shorter — 2-4 years
— for simple-cycle units specifically, the relevant case for this
scenario's new-build.

**Timing check**: exactly 4 years separate today (August 2026) from the
2030-equivalent question that matters here — the 2045 checkpoint itself
is 19 years out, comfortably beyond any lead-time constraint. (The
tighter, genuinely constrained case was Scenario 2's 2030 checkpoint,
addressed separately in Appendix C.11 — not a live issue for Scenario
1B, whose only new-build lands at 2045.)

### N.4 Full SLCOE/NPV Build

**Fully rebuilt this session, replacing an earlier attempt that
overshot** — flagged directly by the user before being propagated
further. The first attempt linked Scenario 1B's own 2045 checkpoint
back to Scenario 1's own 2040 (skipping the shared 2041-2044 window
entirely) and computed the resulting "fresh increment" via simple
subtraction — a formula that produced a physically nonsensical, wildly
oversized 2045 buildout, since 2041-2044 are genuinely identical
between the two scenarios (same RPS target every year through 2044) and
should not have been bypassed.

**The fix — and a real, separate bug it surfaced.** The physically
correct approach links 2045 to 2044 (not 2040) through this project's
own `run_solve()`/`prior_*` linking mechanism, which enforces
monotonicity as a genuine LP bound rather than a post-hoc subtraction
that can go negative. Testing this directly surfaced a real, previously
unnoticed bug: `run_solve()`'s own VCEA-storage-floor logic was
unconditionally overwriting whatever lower bound `build_problem()` had
already set from the prior checkpoint, rather than combining the two.
This never affected any of this session's own regular Scenario 1
checkpoints (their own RPS-driven build always exceeded the VCEA floor
anyway, confirmed by re-solving Scenario 1's own established 2045
checkpoint under both the old and fixed logic and getting a
byte-identical result) — but it was a real bug for Scenario 1B's own,
relaxed 2045 target, where the VCEA floor sits below what 2044 has
already built. Fixed: both storage floors now take the max of the VCEA
statutory floor and whatever the linking mechanism already requires,
rather than silently discarding the higher of the two.

**Result: Scenario 1B's own 2045 checkpoint requires ZERO new solar or
storage build.** 2044's own, already-built capacity already exceeds
what the relaxed, 5%-gas target needs — the LP correctly chooses to add
nothing further. Gas dispatch still pins the physical gas-fleet
capacity cap exactly (4,722 MW, the same cap Scenario 1 itself is bound
by) — but only reaches 1.63% of 2045 demand, not the full 5% the
statute would allow, because the physical fleet itself (sized down by
the VCEA's own Schedule B retirement schedule) simply cannot generate
more than that by this point in the window. **The 5% statutory ceiling
is, in practice, largely moot for Scenario 1B at 2045** — the binding
constraint is physical fleet capacity, not the RPS percentage.

**2045 dispatch cost, from the corrected hourly arrays**:

| Component | Scenario 1 | Scenario 1B |
|---|---|---|
| Na cycling | $359.2M | $347.3M |
| FE cycling | $84.5M | $84.1M |
| Gas fuel | $12.4M | $200.2M |
| Export revenue | $335.5M | $292.6M |
| Gas share of demand | 0.10% | 1.63% |

**Full 20-year result:**

| | Scenario 1 | Scenario 1B |
|---|---|---|
| PV net cost, no TV | $131.845B | $121.950B |
| Terminal value credit | $55.456B | $46.112B |
| **PV net cost, with TV** | **$76.389B** | **$75.839B** |
| **SLCOE (with TV)** | **$42.45/MWh** | **$42.14/MWh** |

**A materially different, more physically coherent conclusion than the
original, pre-session finding** ("Scenario 1B is more expensive... the
terminal-value convention penalizes Scenario 1B for building less at
2045"). That earlier finding was itself an artifact of comparing
different-vintage, uncorrected dispatch data — not a robust structural
feature of the methodology. On today's corrected basis, Scenario 1B's
own terminal value is smaller (2045 contributes nothing new to credit
back), but its own PV cost before terminal value is smaller too, by a
comparable amount — the two effects largely offset, landing the two
scenarios within $0.31/MWh of each other. The underlying reason both
figures converge is the same one identified above: since the physical
gas fleet's own hard cap binds before the RPS percentage ceiling does,
Scenario 1B's own relaxation barely changes what actually gets built or
dispatched relative to Scenario 1.

### N.5 Social Cost of Carbon/Greenhouse Gases, Health Impacts, and Total Societal SLCOE

**Fully rebuilt this session, on the same corrected 2045 basis as N.4.**
2026-2044 reused directly from Scenario 1's own already-corrected
figures (#9/D.3) — genuinely identical by construction, not an
approximation. Only 2045 differs, computed from the corrected,
zero-new-build hourly result described in N.4.

| | Scenario 1, 2045 (corrected) | Scenario 1B, 2045 (corrected) |
|---|---|---|
| Gas (MWh) | 188,877 | 3,043,582 |
| Social Cost of Carbon | $36.9M | $595.0M |
| Health Impacts | $2.1M | $33.3M |

**Full PV-weighted, total societal SLCOE:**

| | Direct SLCOE | Social Cost of GHG | Health Impacts | **Total societal** |
|---|---|---|---|---|
| Scenario 1 | $42.45/MWh | $43.66/MWh | $3.19/MWh | **$89.30/MWh** |
| Scenario 1B | $42.14/MWh | $43.81/MWh | $3.20/MWh | **$89.15/MWh** |

**Conclusion, genuinely different from every earlier version of this
comparison**: Scenario 1B and Scenario 1 now land within $0.15/MWh of
each other on total societal cost — essentially tied, not a clear
advantage in either direction. This supersedes both the original,
pre-session finding (Scenario 1B clearly more expensive) and this
session's own earlier, since-corrected intermediate figure ($90.49/MWh,
built on the since-fixed monotonicity bug). Relaxing VCEA compliance to
allow 5% gas at 2045 does not meaningfully change total cost either
way, under this project's own methodology — because the physical gas
fleet's own capacity, not the statutory percentage, is what actually
constrains Scenario 1B's own dispatch at that point.



**Code location**: `lp_package/demand_shape_interpolation.py` (full module, not just
one function). This section and that file are a matched pair per this
project's standing documentation convention -- each is written to be readable
on its own, and each points back to the other.

## Appendix O — Intermediate-Year Demand Shape: Data-Center-Driven Flattening Methodology

### O.1 The Problem

This project's only real, sourced hourly load *shape* (as opposed to annual
total) comes from a Dominion-provided stakeholder hourly file that, on the
user checking their own records against stakeholder correspondence, turned
out to be **2023 IRP vintage**, not 2024 as originally labeled (the March
2024 date is when Dominion's answers arrived, not the IRP year the questions
were about -- see Activity Tracker item 54's seventh addendum for the full
correction).

Using that single, fixed shape unmodified for every intermediate year (2026-
2045) would miss something real and quantifiable: data centers run a
near-constant 24x7x365 load profile ("data centers have a constant 24x7x365
energy profile," Dominion Energy Virginia, 2025 IRP Update, p. 18), and their
share of Virginia electricity sales has grown substantially and is projected
to keep growing throughout this project's full modeling horizon. A load
curve with a large and growing flat, always-on component should itself get
flatter over time -- not just larger. A static 2023 shape scaled up to 2045's
annual total would understate how flat 2045's real hourly curve would
actually be, with direct consequences for this project's storage-sizing and
dispatch-timing conclusions in the later checkpoints specifically.

### O.2 Data Source: Commercial Share as a Data-Center Proxy

Dominion does not publish data-center load as its own separate line in
either IRP filing consulted for this project -- the closest available proxy
is the **Commercial** rate class, which the Company's own 2025 IRP Update
confirms is where data centers are concentrated ("the Company also has a
high concentration of data centers among its commercial customers... data
centers are extremely energy intensive").

Two sourced tables, both **Virginia-only** (not combined VA+NC DOM LSE --
see the correction note in O.5 below):

- **2018/2019 baseline** (pre-boom reference point, not itself used in the
  flattening formula, retained for historical context): Dominion Energy
  Virginia, "2018 Integrated Resource Plan" (filed May 1, 2018), Appendix
  2B. Commercial share: 39.8% (2018), 41.9% (2019). Citation C074.
- **2020-2045** (the series actually used): Dominion Energy Virginia, "2025
  Integrated Resource Plan Update" (Oct 15, 2025), Appendix 2B-2 -- the same
  table already cited for this project's Virginia-only demand totals
  (Activity Tracker item 54, Appendix M.9, citation C071), reused here for a
  second purpose. Commercial share: 49.3% (2023) rising to 73.6% (2045).

### O.3 Methodology

**Decomposition**: each year's hourly demand is modeled as a blend of two
components -- a "traditional" component following the base 2023 shape
(genuine daily/seasonal peakiness), and a "data-center-like" component,
perfectly flat across all hours in the year.

**Blend weight (alpha)**: the *incremental* commercial share above the base
shape's own 2023 vintage, not the full commercial share -- the base shape
already implicitly reflects however flat or peaky 2023's actual load mix
was, so using the full share would double-count that already-present
portion. `alpha(year) = max(0, commercial_share(year) - commercial_share(2023))`.

**Formula**:
```
demand(t) = ANNUAL_TOTAL(year) x [(1-alpha) x s_base(t) + alpha x (1/N)]
```
where `s_base` is the base shape normalized to sum to 1.0, `N` is the number
of hours in the year, and `ANNUAL_TOTAL(year)` is that year's real,
Virginia-only Appendix 2B-2 total -- so the annual total is always exactly
correct regardless of alpha; only the hour-to-hour distribution shifts.

**Alpha values at the four solved checkpoints:**

| Year | Commercial share | Alpha |
|---|---|---|
| 2030 | 59.1% | 0.098 |
| 2035 | 66.1% | 0.167 |
| 2040 | 70.5% | 0.212 |
| 2045 | 73.6% | 0.243 |

For the 15 unsolved intermediate years, alpha is computed directly from that
year's own real commercial-share value (all years 2018-2045 are individually
sourced from the same two tables, not interpolated a second time on top of
an already-derived quantity).

### O.4 Verification Against Real Data

Tested directly against the user's uploaded file's actual 2024 hourly
values (the file's earliest available year, used as the closest proxy for
the underlying 2023 vintage -- the file itself contains no true 2023 row).
Unflattened peak/average ratio: 1.534. After blending:

| Year | Peak/Average ratio | Change |
|---|---|---|
| 2030 | 1.482 | −3.4% |
| 2035 | 1.444 | −5.9% |
| 2040 | 1.421 | −7.4% |
| 2045 | 1.404 | −8.5% |

A real, measurable flattening effect -- meaningful but not extreme, consistent
with even 2045 still being roughly three-quarters traditional-shaped load.

### O.5 Correction Log (kept for transparency, per this project's established convention)

An earlier draft of `demand_shape_interpolation.py` mislabeled the 2025 IRP
Update source as **Appendix 2B-1** ("Total (DOM LSE) Sales," the combined
VA+NC table) rather than **Appendix 2B-2** (Virginia-only). Caught and fixed
same session, before this methodology was finalized, by directly
re-extracting both tables from the raw filing text and cross-verifying via
an independent row-sum check (Appendix 2B-1's own stated total, 82,157 GWh
at 2015, matches summing its own Residential + Commercial + Industrial +
Public Authority + Street/Traffic + Sales-for-Resale columns to within
rounding -- confirming which numeric block genuinely belongs to which
appendix).

**Practical impact of the error was small**: the true combined-table
commercial share runs about 1.0-1.4 percentage points lower than the
Virginia-only share used, fairly consistently across years -- and because
alpha is a *difference* from the 2023 baseline, this mostly cancels out
rather than compounding. The numbers actually used in the formula above were
never wrong; only their citation was. The corrected labeling (Virginia-only)
is, if anything, the more appropriate one for this project given its
established Virginia-only principle (Activity Tracker item 54) -- so this
correction improves consistency rather than requiring a substantive change.

### O.6 Limitations (disclosed explicitly, not discovered later)

1. **Commercial share is a proxy, not a direct data-center measurement.**
   The Commercial rate class includes real non-data-center load (offices,
   retail) without a flat 24x7 profile. This likely means alpha
   *understates* the true data-center-driven flattening effect, not
   overstates it -- ordinary commercial load dilutes the proxy downward.
2. **The linear blend formula is a reasonable, simple choice, not a
   uniquely-derived one.** No attempt was made to fit a more complex
   functional form given the sourcing available.
3. **No sourced basis exists beyond 2045** for either commercial-share
   table -- this methodology should not be extended past that year without
   new sourcing.
4. **`BASE_SHAPE_YEAR` (2024, the uploaded file's earliest row) is a proxy**
   for the true 2023 IRP vintage -- the file itself contains no actual 2023
   row to use directly.

---

## Appendix M — Reference Literature (new this session)

*(External sources gathered to inform this project's methodology, distinct
from the C001-C059 dataset/assumption citations tracked separately in
`build_citations.py`. Added as a standing, updatable list per project
decision to maintain a shared record of what's been consulted.)*

### M.1 Integrated Resource Planning Practice

**Biewald, B., Glick, D., Kwok, S. et al. (2024).** *Best Practices in
Integrated Resource Planning: A guide for planners developing the
electricity resource mix of the future.* Synapse Energy Economics /
Lawrence Berkeley National Laboratory. https://escholarship.org/uc/item/8x83n1jf

Directly relevant to this project's core storage strategy. Best Practice 17
("Model battery energy storage options") explicitly validates a
dual short/long-duration approach, citing iron-air by name as a
cost-effective option for longer-duration back-up and reserves distinct
from short-duration lithium-ion's role -- independent confirmation of this
project's Na-ion/iron-air split, not merely a coincidental parallel. Also
useful for Best Practice 18 (consistent treatment of emerging technologies)
as a disclosure-and-transparency standard this project's own approach
(disclosed simplifications throughout) already aligns with.

### M.2 Solver Documentation

**HiGHS Documentation — Feasibility and Optimality.**
https://ergo-code.github.io/HiGHS/stable/guide/kkt/

Directly explains the KKT feasibility/optimality machinery this project
used to verify true LP optimality at a simultaneous-dispatch hour (Internal
Debugging Log #20, MILP trial context). Also directly relevant to two
earlier, separately-diagnosed issues this session: the "HiGHS solutions"
section explicitly describes how a large objective coefficient paired with
a near-zero reduced cost can mask genuine non-optimality behind a reported
"optimal" status -- the exact failure mode this project found and fixed via
the BUILD_SCALE correction, now independently confirmed as a known,
documented HiGHS behavior rather than a project-specific quirk.

### M.3 Broader Modeling Challenges

**Anderson, E., Ferris, M., Philpott, A. et al. (2025).** "Ten challenges
for mathematical modeling of the green-energy transition." *Current
Sustainable/Renewable Energy Reports*, 12, 26.
https://doi.org/10.1007/s40518-025-00274-9

Challenge 1 explicitly frames the curtailment/storage-capacity tradeoff
this project investigated at length (Internal Debugging Log #16/#18/#20)
as a recognized, general modeling challenge, not an isolated bug hunt.
Challenge 10 (computation and validation for large models) is directly
relevant to this project's own MILP-tractability finding (#20.1).

**Korovushkin, V., Boichenko, S., Artyukhov, A. et al. (2025).** "Modern
Optimization Technologies in Hybrid Renewable Energy Systems: A Systematic
Review of Research Gaps and Prospects for Decisions." *Energies*, 18(17),
4727. https://doi.org/10.3390/en18174727

**Barrera-Singaña, C., Comech, M.P., Arcos, H. (2025).** "A Comprehensive
Review on the Integration of Renewable Energy Through Advanced Planning and
Optimization Techniques." *Energies*, 18(11), 2961.
https://doi.org/10.3390/en18112961

Both reviews formalize the decision-variables/objectives/constraints
framework this project has been using throughout (see the LP Model
Reference Document built this session) as the standard structure for this
class of problem, and both catalog MILP vs. LP-relaxation tradeoffs
directly relevant to the simultaneous-dispatch investigation (#20 series).

### M.4 Simultaneous Charge/Discharge ("SCD") — A Named, Recognized Problem

*(Located via a targeted search prompted directly by this project's own
#20 investigation. This is a well-established, named problem in the
literature -- "simultaneous charging and discharging" (SCD) or the
"battery complementarity constraint" -- not something unique to this
project's model. Worth stating plainly: every genuine fix this project
tried (MILP/binaries, netting) has a direct, named counterpart in this
literature, confirming the difficulty was real rather than a symptom of
an implementation error.)*

**Nazir, N. and Almassalkhi, M. (2021).** "Guaranteeing a Physically
Realizable Battery Dispatch Without Charge-Discharge Complementarity
Constraints." *IEEE Transactions on Smart Grid.*
https://madsalma.github.io/pubs/2021_tsg_ccBatt.pdf

The most directly actionable find of this search -- a purely linear
formulation (no binaries, no complementarity constraint) that does not
prevent simultaneous dispatch from occurring, but mathematically
guarantees the resulting SoC trajectory cannot violate physical bounds
regardless. Works by solving with TWO parallel SoC-tracking constraints:
a "relaxed" model (equivalent to this project's current formulation, proven
to always UNDERESTIMATE true SoC) and a "simplified" single-net-input model
using an averaged efficiency (proven to always OVERESTIMATE true SoC).
Bounding both keeps the true, physically-realizable SoC within limits by
construction. Reports 10-200x speedup over MILP in their own benchmarks.
Directly confirms this project's own finding from the netting investigation
(#20.3): model mismatch/conservativeness "depends largely on the charge and
discharge efficiencies... if the round-trip efficiency is low, then the
model mismatch increases" -- explicitly flagging pumped-hydro and hydrogen
storage (~60% RTE) as cases where their method becomes too conservative to
be useful, a caution directly relevant to this project's iron-air storage
specifically (RTE below Na-ion's 90%). Tested against this project's own
model this session, for Scenario 2's own Na-storage problem specifically
(Internal Debugging Log #40) -- rejected there too, for the same reason
originally found: the LP still chose to land exactly on a relaxed SoC
floor rather than being freed from the underlying pressure toward low
SoC, showing the boundary condition alone was not the root cause.

**Two further sources, located via a fresh, targeted search this session** (Internal Debugging Log
#40), prompted directly by Scenario 2's own Na-storage simultaneous-dispatch finding persisting
after the SCD literature's own previously-catalogued options had already been tried and found
insufficient. Author names not independently confirmed via the search snippets retrieved -- cited by
title/URL only, per this project's own standing sourcing convention (never invent an attribution):

"Operational Valuation for Energy Storage under Multi-stage Price Uncertainties."
https://arxiv.org/pdf/1910.09149

"A Lagrangian Policy for Optimal Energy Storage Control." https://arxiv.org/pdf/1901.09507

Both give the same sufficient condition for simultaneous charge/discharge to occur: the Lagrangian
dual (shadow price) on stored energy must be negative -- "we have an intention to store as little
energy as possible," using round-trip efficiency loss specifically to dispose of energy the
optimizer is otherwise forced to hold, most classically arising from negative real-time prices in
market-facing formulations (this project's own problem has no explicit price signal, but the same
mechanism arises from a hard equality boundary condition combined with no export/disposal valve).
Directly confirms and sharpens this project's own earlier KKT/reduced-cost finding (#20, #40) rather
than contradicting it -- both point to the same underlying phenomenon, genuine LP degeneracy driven
by a locally-negative shadow price, not a modeling error.

**Morales, J.M.** "Linear and Second-order-cone Valid Inequalities for
Problems with Storage." https://arxiv.org/pdf/2506.21470

Derives linear inequalities that are facets of the storage feasible
region's convex hull -- tightens the relaxation without full
complementarity or binaries. A second, related but distinct linear-only
candidate.

**Duan, C., Jiang, L., Fang, W., Wen, X., Liu, J.** "Improved Sufficient
Conditions for Exact Convex Relaxation of Storage-Concerned ED."
https://arxiv.org/pdf/1603.07875

Provides sufficient conditions under which a relaxed (no-complementarity)
LP's own optimal solution is automatically guaranteed complementarity-
respecting, without adding any constraint at all -- directly the same
category of check as this project's own KKT verification (#20, MILP-trial
context), formalized as reusable sufficient conditions rather than a
single point-check.

**Han, D., Jiang, N., Dey, S.S., Xie, W.** "Regularized MIP Model for
Integrating Energy Storage Systems..." https://arxiv.org/pdf/2402.04406

A "regularized" MIP with zero integrality gap versus its own LP relaxation
under mild conditions -- potentially a more tractable middle ground between
this project's full-MILP trial (#20.1, proven correct but too slow) and a
pure LP relaxation. Not yet evaluated for tractability at this project's
scale.

### M.5 Multi-Storage Coordination Under Uncertainty — Two Additional Sources

*(Provided directly by the user after the ScienceDirect and PMC links from M.4 could not be retrieved automatically -- the ScienceDirect article as a pasted excerpt, the PMC article as an attached PDF. Replaces the earlier "could not retrieve" note.)*

**"Two-stage stochastic optimization of integrated energy systems with hydrogen and battery
storage under renewable uncertainty."** *International Journal of Hydrogen Energy* (in press,
2026). https://www.sciencedirect.com/science/article/abs/pii/S036031992601387X (author names not
independently confirmed via the excerpt provided or subsequent search; title and journal confirmed)

Develops a hydrogen-centered integrated energy system (HIES) coordinating hydrogen storage (HESS),
battery storage (ESS), and dual-fuel CHP units, solved via a two-stage stochastic program (day-ahead
dispatch, then scenario-based recourse) using Vine Copula-MCMC-generated representative renewable
scenarios and a metaheuristic (scent-guided differential PSO) solver. Relevant less for its specific
solution method (stochastic + metaheuristic, a different paradigm from this project's deterministic LP)
than as a concrete example of the general challenge Anderson et al. (M.3) call out as Challenge 7 --
representing long-term uncertainty -- and as a second, independent example (alongside Bamisile et al.
below) of coordinating two structurally different storage types with different duration/response
characteristics, the same core design choice underlying this project's Na-ion/iron-air split.

**Bamisile, O., Cai, D., Adun, H., Dagbasi, M., Ukwuoma, C.C., Huang, Q., Johnson, N., Bamisile, O.
(2024).** "Towards renewables development: Review of optimization techniques for energy storage and
hybrid renewable energy systems." *Heliyon*, 10, e37482. https://doi.org/10.1016/j.heliyon.2024.e37482

A large (200-article) systematic review (PRISMA methodology) of HRES+ESS optimization, covering storage
technology taxonomy, optimization method categories (conventional/metaheuristic/hybrid), and a detailed
catalog of objective functions and constraints across 20+ specific studies (their Table 4). Two direct,
useful cross-checks against this project's own model:

- **Independent confirmation of the corrected DoD convention.** One cataloged study's battery
  constraint is given explicitly as `EBATT_min = (1 - DOD) x EBATT_max` -- i.e., the floor sits at
  `(1-DOD)` of capacity, confirming the standard convention (reserve at the bottom, not the top) this
  project corrected to earlier this session (Internal Debugging Log #17), independent of the Sandia
  methodology citation already in use.
- **Confirms LP is a recognized, if less common, category.** Their conventional-methods taxonomy
  explicitly lists "linear programming techniques" as one path among several (alongside dynamic
  programming and multi-objective strategies) -- consistent with this project's own finding
  (Section 8.1 discussion in the two MDPI reviews, M.3) that LP/MILP guarantees global optimality but
  metaheuristics dominate this literature's actual sample for tractability at scale, the same trade-off
  this project weighed directly in the MILP trial (#20.1).

---

### M.6 "Unintended Storage Cycling" (USC) — A Named Phenomenon Specifically Tied to Renewable-Target Constraints

*(Located via a broader literature search, deliberately not limited to any single solver's practice,
per direct instruction. This is a distinct, more specific literature thread than M.4's general "SCD"
material -- USC is specifically about simultaneous dispatch caused by renewable-share/RPS-style
constraints, exactly this project's own RPS mechanism, rather than LP relaxation looseness in general.)*

**Kittel, M. and Schill, W-P. (2022).** "Renewable Energy Targets and Unintended Storage Cycling:
Implications for Energy Modeling." *iScience*, 25(4), 104002. https://doi.org/10.1016/j.isci.2022.104002

The originating paper for the USC term and the "SLCR" (Storage Loss Coverage by Renewables) constraint
reformulation -- ties a renewable-share constraint's required generation to storage losses incurred, so
that USC-driven losses can no longer hide from the constraint's own accounting. Key empirical finding
directly relevant to this project's own checkpoint structure: USC "grows disproportionately" with
renewable penetration and does not occur at all below roughly 40% renewable share -- this project's
2045 checkpoint (99.9%+ clean target) sits at the most extreme end of the range their paper identifies
as worst-case. Personally tested against this project's model (Internal Debugging Log #20.7): SLCR did
NOT reduce simultaneous dispatch here (marginally increased it, 644.5M vs. 532.8M MWh phantom volume),
traced to a real, identified reason -- their mechanism specifically targets gaming a BINDING gas
allowance, and this project's 2045 target leaves almost no such allowance to game (confirmed post-trial
at 0.064% gas, tighter than the 0.08% target itself). Flagged as possibly still relevant at less extreme
checkpoints (2030/2035/2040) where a genuine, larger gas allowance exists -- not yet re-tested there.

**Parzen, M., Kittel, M., Friedrich, D., Kiprakis, A.E. (2023).** "Reducing energy system model
distortions from unintended storage cycling through variable costs." *iScience*, 26(1), 105729.
https://doi.org/10.1016/j.isci.2022.105729

Companion paper to the above, from the same research thread, testing a different remedy: correctly-
calibrated variable costs (not structural constraint changes). Empirically tested threshold, specific
and quotable: full USC removal in their PyPSA-Eur case study required a variable cost additive of at
least 10 EUR/MWh -- and they explicitly note the required threshold scales with solver precision, citing
100 EUR/MWh under looser solver accuracy settings. Directly relevant, NOT YET TESTED: this project's own
option 3/4 attempt (Internal Debugging Log, cycling-cost-on-both-sides test) used only $2.67/MWh split
across both charge/discharge sides for Na-ion -- an order of magnitude below this paper's own validated
minimum. The earlier option 3/4 "no effect" finding may reflect an insufficiently large cost, not a
genuine failure of the underlying approach -- a real candidate for re-testing at the properly-scaled
value before concluding cost-based fixes don't work here.

**Independent, practitioner-level confirmation (not an academic source, but a real production tool):**
GitHub, blue-marble/gridpath, Issue #839, "Add constraint to prevent simultaneous charge and discharge
from a storage project." https://github.com/blue-marble/gridpath/issues/839

A GridPath user modeling pumped hydro storage reports the exact mechanism this project independently
diagnosed: "the curtailment cost is more expensive than the cost to operate PSH discharge so it is
cost-optimal to 'dump' wind or solar energy by charging and discharging storage. The energy is 'dumped'
in the efficiency loss of the PSH pumps and generators." Confirms this project's core diagnosis
(curtailment-cost-vs-cycling-cost imbalance driving the phenomenon) was independently arrived at by a
different practitioner, in a different real-world tool, using different language -- not a project-
specific artifact.

**PyPSA mailing list, practitioner discussion** (Google Groups, pypsa, March 2021).
https://groups.google.com/g/pypsa/c/mg8xQD91di4

A PyPSA maintainer's own recommended practice: "you could set a small marginal cost on both links to
discourage simultaneous charging/discharging... It obviously depends on your model, but the need for
curtailment is one situation where this can occur." Same underlying approach as this project's own
option 3/4 (cost on both sides), offered informally by the tool's own maintainers as standard practice
-- consistent with, not contradicting, the Parzen et al. calibration finding above.

### M.7 A Pure-LP Tighter Reformulation — No Binaries, Proven Convex-Hull-Optimal for One Period

**Elgersma, M.B., Morales-España, G., Aardal, K.I., Helistö, N., Kiviluoma, J., de Weerdt, M.M. (2024).**
"Tight MIP Formulations for Optimal Operation and Investment of Storage Including Reserves."
arXiv:2411.17484. https://arxiv.org/pdf/2411.17484

Distinct in kind from every option this project has tried (MILP/binaries, netting, RBD, SLCR) --
derives the exact convex hull of the single-period storage operation problem, and shows the resulting
"TO-LP" reformulation (a pure constraint rewrite: bounding `e[t-1]` by the CURRENT period's
charge/discharge rather than bounding `e[t]` directly, no binary variables needed for the LP relaxation
itself) provably tightens the standard formulation. Own case study results are a genuine, if partial,
improvement: simultaneous-dispatch periods roughly halved (663 to 363 of 1,460 periods) and the phantom-
volume metric also roughly halved, with no MILP-scale computational cost. NOT YET TESTED against this
project's model -- flags one real caveat worth checking first: their tightness guarantee assumes power
rating doesn't exceed what's needed to fill/drain the full usable capacity range in one hour (roughly
`P_rated <= capacity/(η·Δt)`), an assumption this project's Na-ion build (PNA_ often far exceeding
ENA_/duration, given both are chosen independently by the LP) may violate, which could weaken the
guarantee's practical effect here even if implemented correctly.

**Related, not yet reviewed in full:** Elsaadany, M., Almassalkhi, M.R., Tindemans, S.H. (2025). "Linear
Model of Aggregated Homogeneous Energy Storage Elements with Realizable Dispatch Guarantees."
https://arxiv.org/html/2501.04508 -- cited within Elgersma et al. as the "composite battery systems"
exception to standard SCD reasoning (multiple physical sub-units genuinely CAN charge and discharge
simultaneously in aggregate, since different sub-units can be in different states at once). Possibly
relevant given utility-scale Na-ion/iron-air installations are physically composed of many discrete
units, not one monolithic device -- a reframing (aggregate dispatch guarantees, not single-unit
complementarity) not yet explored for this project.

---

### M.8 Storage Under-Utilization at High VRE Penetration — Why Curtailment Despite Headroom Is Expected, Not a Defect

**López Prol, J. and Schill, W-P. (2020).** "The Economics of Variable Renewables and Electricity
Storage." arXiv:2012.15371. https://arxiv.org/pdf/2012.15371

A review synthesizing multiple independent, peer-reviewed lines of evidence (different models,
different methods: price-taker arbitrage models, time-series models, capacity-expansion models) that
directly resolves this project's separate "headroom despite curtailment" pattern (Internal Debugging Log
#21), distinct from the simultaneous-dispatch issue (#20 series). Key finding, quoted directly: "storage
is never deployed to fully take up renewable surplus generation in a least-cost solution, as this would
require excessive and under-utilized investments into storage power and, even more so, storage energy
capacity... there will accordingly always be some level of renewable curtailment, absent geographical
balancing, flexible Power-to-X, or other low-cost flexibility options." Synthesizes and cites directly:

- **Schill, W-P. (2014).** "Residual load, renewable surplus generation and storage requirements in
  Germany." Energy Policy 73, 65-79. Finds storage needs "substantially decrease if small levels of VRE
  curtailment are allowed," and that rare, extreme surplus events -- not typical days -- determine
  storage sizing, so forcing zero curtailment causes storage needs to increase disproportionately.
- **Zerrahn, A., Schill, W-P., Kemfert, C. (2018).** "On the economics of electrical storage for
  variable renewable energy sources." European Economic Review 108, 259-279. Confirms with an
  open-source model that a mix of VRE curtailment and storage deployment minimizes overall system costs
  -- not either alone.
- **Sinn, H-W. (2017).** "Buffering volatility: A study on the limits of Germany's energy revolution."
  European Economic Review 99, 130-150. A particularly strong data point precisely because it set out to
  argue the opposite: a priori ruling out renewable curtailment as a test case, and finding storage needs
  would "very substantially increase" as a result -- reinforcing the same conclusion from the direction
  most likely to contradict it.
- **Denholm, P. and Hand, M. (2011).** "Grid flexibility and storage required to achieve very high
  penetration of variable renewable electricity." Energy Policy 39, 1817-1830. Gives a concrete
  benchmark: even at 80% VRE penetration, keeping curtailment below 10% requires storage sized to
  roughly one full day of average demand -- curtailment at high VRE shares is the literature's norm, not
  an exception requiring correction.

**Resolution for this project:** confirms this project's own earlier, independently-derived finding
(Appendix A.9, curtailment cheaper than buying enough storage to fully avoid it) as an instance of this
same, broader, peer-reviewed principle rather than a project-specific artifact or an unresolved defect.
The mechanism transfers directly: storage capacity gets sized for its everyday role (arbitrage, smoothing
dispatchable full-load hours), not for rare extreme-surplus hours; on those hours the battery has SoC
headroom it was never sized to use, and using it would mean paying a full charge+discharge cycling cost
to serve demand already met more cheaply elsewhere -- making direct curtailment the genuinely
cost-minimizing choice. No further model change made on this basis; the SLCR $5-40/MWh working range
(2045 Scenario 1 final value: $5/MWh) stands as the resolved state, with remaining curtailment and SoC
headroom understood as expected, documented behavior.

---

### M.9 Virginia-Only Demand Data — Dominion's Own 2025 IRP Update, Appendix 2B-2

**Dominion Energy Virginia (Virginia Electric and Power Company). "2025 Integrated Resource Plan
Update." Filed with the Virginia State Corporation Commission (Case No. PUR-2025-00184) and the
North Carolina Utilities Commission, October 15, 2025. Appendix 2B-2: "Virginia Sales (GWh) by
Customer Class," p. 89.**

The demand basis this project's SLCOE/NPV work uses going forward, and the resolution of one of the
three open dimensions on Activity Tracker item 54 (vintage / methodology / geography -- geography is
now resolved by this citation; the other two remain open).

**Why this specific table, not the more commonly-cited "DOM LSE" figures already used elsewhere in
this project's demand work:** PJM's own transmission-zone map shows the "DOM" zone spanning both
Virginia and North Carolina -- Dominion Energy Virginia's own retail service territory is only the
Virginia portion of that zone. Every "DOM LSE" figure examined earlier in this project's demand
investigation (the 2025 IRP Update's own Figure 2.1.9 Company Load Forecast table, a stakeholder-
obtained 2024 hourly load file, PJM's 2026 Load Forecast Report) is the *combined* VA+NC total, not
Virginia alone -- confirmed directly by the filing's own text: Dominion "operates generation,
transmission, and distribution systems to serve approximately 2.8 million electric customers located
across approximately 30,000 square miles of Virginia and North Carolina." Appendix 2B-2 is the
filing's own Virginia-only breakout, distinct from Appendix 2B-1 (the combined DOM LSE total) and
2B-3 (North Carolina only).

**Annual energy, Virginia-only (GWh), key years from the full 2015-2045 table:**

| Year | GWh |
|---|---|
| 2025 | 95,246 |
| 2030 | 110,864 |
| 2035 | 136,645 |
| 2040 | 162,077 |
| 2045 | 186,462 |

**Implied North Carolina share** (this table vs. the combined DOM LSE total already cited elsewhere
in this project): 5.8% (2025), narrowing to 3.1% (2040-2045) -- smaller in magnitude than the other
open dimensions on item 54 (vintage divergence up to ~15%; DOM Zone-vs-DOM-LSE gap up to ~107%),
and directionally sensible: Northern Virginia's data-center growth outpaces Dominion's smaller North
Carolina territory, so Virginia's share of the combined total grows over time.

**Important limitation, stated directly in the filing immediately below the table:** *"Appendix 2B-2
has been provided with the 2025 Company Load Forecast instead of the 2025 PJM Load Forecast because
PJM does not provide forecasted sales or customer counts broken down by rate class."* A Virginia-only
cut of the PJM-derived forecast -- the version the SCC actually directs Dominion to use for portfolio
planning -- does not appear to exist as a published figure at all, since PJM's own underlying data
doesn't break out by state. The Company and PJM-derived forecasts are stated elsewhere in the same
filing to be "in general alignment" (2025 PJM Derived: 2.5%/3.5% CAGR for DOM LSE peak/energy;
2025 Company: 2.3%/3.3% CAGR, same scope and window) -- so this is likely a small, bounded gap
rather than an unresolved discrepancy, but it hasn't been directly confirmed for the Virginia-only cut
specifically.

**Status at time of citation:** used as the working demand basis for this project's SLCOE/NPV
calculations because it is the most directly-sourced, Virginia-specific figure available, and the
next IRP filing (2026) is not expected for several months. The vintage question (this is 2025-vintage
data; a 2024 stakeholder file and PJM's own 2026 report remain separate, unreconciled vintages -- see
Activity Tracker item 54) is not resolved by this citation and should be revisited if a newer,
directly Virginia-scoped source becomes available.

---

### M.10 Solar "Value Factor" — Measured PJM Data, Used to Stress-Test (Not Adopt) the Export-Price Discount

**Seel, J., Mulvaney Kemp, J., Cheyette, A., Gorman, W., Darghouth, N., Robson, D., Rand, J., Jeong,
S. "U.S. Utility-Scale Solar 2025 Data Update." Lawrence Berkeley National Laboratory, October 2025.
utilityscalesolar.lbl.gov**

Cited in Appendix B.5 (export price) as a specific, credible source located and checked in place of
this project's earlier, un-pinned-down "documented in NREL/LBNL solar value reports" citation --
included here because it was a genuine, weighed consideration in reaching the final export-price
figure, not because it was ultimately adopted.

Defines a **value factor**: the ratio of solar's actual generation-weighted captured market value to
a flat 24x7 block's average value at the same location -- exactly the concept this project's export-
price "midday discount" factor is attempting to approximate. National average value factor, 2024:
80%. Regional range is wide: as low as 30% in CAISO (at 30% solar penetration, the report's clearest
illustration of penetration-driven value decline), as high as 181% in SPP (1% penetration). **PJM
specifically is reported slightly above 100%** -- $33/MWh solar value vs. $32/MWh flat-block value in
2024 -- with the report explicitly listing PJM among regions where solar's generation profile *helps*
rather than hurts its relative value.

**Why this was not adopted despite being directly on-point:** two disclosed limitations, both noted
at time of decision rather than found later. (1) PJM-wide, not DOM-zone-specific -- no strong reason
to expect DOM to differ sharply, but not a direct measurement either. (2) A 2024, current-penetration
snapshot -- the same report documents value factor declining as solar's regional load share grows,
with CAISO's trajectory as the clearest within-report precedent. This project's own checkpoints
project solar growing roughly 15,000 MW (2030) to 142,000 MW (2045), a penetration path well beyond
what PJM's current, sub-saturation value factor describes. Retained here as a documented,
directly-relevant data point for future reference (e.g., if this project ever builds a
penetration-dependent export-price curve rather than a flat rate), not as a citation supporting the
model's current $27.00/MWh figure.

---



## Appendix P — Solve Procedure and Requirements

### P.0 Purpose and Scope

Over the course of this project, a completed scenario solve has on
several occasions been found, after the fact, to be missing something a
competent modeler would ordinarily catch immediately — solar output not
degraded over time, no formal reserve margin enforced, a scenario's
dispatch and cost figures represented by only a handful of sample years
rather than the full analysis window, existing generating capacity
miscredited or omitted, and a capacity-sizing approach that let an
optimizer choose an unrealistically large build because nothing in its
own objective penalized doing so. Each time, correcting the gap meant
re-running the affected dispatch simulations, recomputing every
downstream figure (capital cost, fuel cost, terminal value, levelized
cost, social cost), and revising every document built on top of those
figures.

This appendix exists to prevent that cycle from recurring. It sets out,
in one place, the standing requirements every scenario solve in this
project is expected to satisfy, along with the reasoning behind each
one. It is meant to be checked *before* a solve is presented as final,
not consulted only after a gap is discovered. A reader unfamiliar with
this project's internal history should be able to use this appendix, on
its own, to understand what "a complete and correct solve" means here
and why each requirement exists.

Where a requirement is currently unmet by work already in this project,
that is stated plainly in P.4 below, rather than implied to be resolved.

### P.1 Terminology: What "a Solve" Refers To

This project uses linear programming (LP) — a mathematical optimization
method — to determine, for a given target year, either the least-cost
mix of generation and storage capacity needed to reliably meet demand,
or (where capacity is fixed by an external schedule) the least-cost way
to operate a given, already-fixed set of resources hour by hour. The
word "solve" is used at four different levels of granularity in this
appendix, and the distinction matters: treating a smaller-scope solve as
though it satisfies a larger-scope requirement is precisely how a
partial fix has previously been mistaken for a complete one.

**Year-solve.** One run of the hourly dispatch optimization — 8,760
hours, one per year — for a single calendar year, producing that year's
own hour-by-hour results: how much power comes from gas generation,
how much surplus generation is curtailed (discarded because it cannot
be used, stored, or exported), how storage charges and discharges each
hour, and whether any demand goes unserved. This is the atomic unit of
computation in this project. Every year from 2026 through 2045 is, or
should be, backed by exactly one year-solve.

Within a year-solve, a further distinction matters, particularly for
P.2 #1 and #5 below:

- **Checkpoint solve**: a year-solve in which the optimizer itself
  decides both how much new capacity to build (solar megawatts [MW],
  battery storage MW and megawatt-hours [MWh] of energy capacity) *and*
  how to dispatch it, simultaneously, as joint decisions. Scenario 1 and
  Scenario 1B use checkpoint solves at four milestone years: 2030, 2035,
  2040, and 2045. For Scenario 2, where the build-out follows a
  statutory schedule rather than optimizer choice, the analogous case is
  simply a year at which that schedule sets a new capacity milestone.

- **Dispatch-only solve**: a year-solve in which capacity is fixed
  before the optimization begins — either by interpolating between two
  adjacent checkpoint years, or by reading a value directly off a
  statutory schedule — and the optimizer decides only hour-by-hour
  dispatch (for example, whether to draw from gas generation or from
  storage in a given hour) given that fixed capacity. Every year between
  checkpoints (for example, 2031 through 2034) is handled this way.
  "Dispatch-only" describes what the optimizer is deciding, not a lower
  standard of rigor: a dispatch-only solve is still a genuine,
  independent 8,760-hour optimization, not an approximation or an
  interpolation of results from other years. The requirement in P.2 #1
  that dispatch and cost not be interpolated refers to exactly this
  distinction — capacity may be interpolated between checkpoints, but
  the dispatch and cost that result from that capacity must be
  separately, genuinely computed for every year.

**Scenario-solve** (or "the full solve"). The complete set of all 20
year-solves for a given scenario, together with every calculation built
on top of them: cost accounting that assigns each year's new capacity
to the price it was actually built at ("vintage-tracked" capital cost,
described further in P.2 #6), credit for the residual value of assets
still in service beyond the end of the 20-year study window ("terminal
value," P.2 #6), tiered social/environmental cost estimates, and the
final system-levelized-cost-of-energy (SLCOE) and net-present-value
(NPV) results. This is what is meant when this project refers to "the
Scenario 1 solve" or "re-solving Scenario 2" without naming a specific
year.

**Re-solve.** Re-running some subset of year-solves — and, necessarily,
recalculating everything downstream that depends on them — after a
correction. The correct scope of a re-solve depends entirely on the
scope of what changed, and should be stated explicitly before work
begins rather than assumed:

- A correction to a single year's own input (for example, that year's
  specific statutory capacity milestone) requires re-solving only that
  year, plus recalculating whatever downstream figures depend on it.
- A correction to machinery shared across every year's calculation (for
  example, how solar output is adjusted for panel aging — see P.2 #2)
  requires re-solving *every* affected year, not a single one. Both of
  this project's most substantial corrections to date — extending
  Scenario 2 from four sample years to a genuine 20-year solve, and
  correcting how solar output was aged over time — fell into this
  second category, and both required a complete re-solve of every
  affected year (see Appendix C.12 and C.13).

### P.2 General Procedure — Requirements Applying to Every Scenario and Every Solve

#### #1. Time coverage

A scenario-solve must cover all 20 years of the analysis window
(2026-2045), not a subset of checkpoint years — that is, it must be
assembled from 20 individual year-solves, not from only the checkpoint
years. Every one of those 20 year-solves must be genuine and
independent, establishing that year's own fuel cost, emissions, and gas
share of generation. Built capacity may be interpolated between
checkpoints for cost-accounting purposes (an established convention in
this project), but the dispatch results and costs produced by each
year-solve may not themselves be interpolated, nor may a scenario-solve
substitute a handful of sample years' results for genuine results in
every year. This project's clearest illustration of why this matters:
an earlier version of Scenario 2's cost estimate, assembled from only
four year-solves (the checkpoint years alone) rather than all 20,
differed from the correct, fully-solved result by a factor of 15 to
20 — an error invisible until every year was actually, independently
solved (Appendix C.12).

Where a scenario-solve is extended backward (for example, to add
2026-2029) or forward beyond an existing set of checkpoints, the
governing statute's or schedule's own earlier or later milestones
should be used for the newly added year-solves where such milestones
exist, rather than a flat extrapolation from the nearest checkpoint.

#### #2. Solar output degradation

Solar panels lose a small fraction of their generating capability every
year they are in service — a standard, well-documented industry effect,
modeled in this project at 0.5% per year. This degradation must be
applied to whichever capacity figure is actually used in dispatch and
reliability calculations. The un-aged, "nameplate" capacity figure
remains the correct one to use for capital-cost accounting and for
checking compliance with any statutory build requirement — aging
applies only to the generation/reliability side of the calculation,
never to "how much had to be built."

**[If Scenario 1 or 1B: this happens automatically. Solar is a decision
the optimizer makes for itself, and this project's vintage-tracking
already ages each year's construction correctly before that year's
total is reported — no separate step is required.]**

**[If Scenario 2, or any future scenario built the same way (solar
capacity following an externally-set schedule rather than an optimizer
decision): the *effective*, aged capacity must be separately calculated
and used in place of the raw scheduled figure wherever solar output is
calculated — this does not happen automatically the way it does for
Scenario 1/1B.]**

Where a year-solve needs to determine how much *new* capacity was added
in a given year (as distinct from the total capacity in place), two
different calculation methods apply depending on what the underlying
capacity figure represents, and using the wrong one produces a subtle,
easy-to-miss error:

**[If Scenario 1 or 1B:** the reported cumulative total for a year
already reflects aging, since the optimizer's own dispatch calculation
ages prior construction before that year's total is reported — so the
new addition for a year is found by aging the *prior* year's total
forward and subtracting that aged figure from the current year's
total.**]**

**[If Scenario 2, or any future scenario with an externally-set
statutory schedule:** the cumulative total is instead a flat, unaged
requirement by construction — so the new addition for a year is simply
that year's scheduled figure minus the prior year's scheduled figure,
with no aging involved in the subtraction itself.**]**

Applying the first method to a schedule of the second type silently
reconstructs the original, unaged total with no net effect from aging
at all — this exact error occurred once in this project's history and
must not recur (Appendix C.13).

#### #3. Reserve margin

Every year-solve should enforce a formal reserve-margin requirement: that
total available firm generating capacity exceed peak demand by a
specified percentage, providing a buffer against generator outages,
demand forecast error, and weather worse than whatever single year was
modeled. This project's implementation targets PJM Interconnection's
own Installed Reserve Margin (IRM) requirement, **17.7% — settled as
this project's own value by direct decision, given PJM's own margin
running persistently above its stated soft cap and other supporting
reasons** — applied at the hour of peak net demand (demand remaining
after nuclear generation, existing solar, and wind are accounted for)
— the hour of greatest adequacy risk in a system trending toward high
renewable penetration.

**Mechanism tested and verified on two checkpoints; not yet applied
project-wide.** The constraint (`add_reserve_margin_constraint()`) has
now actually been invoked, for the first time, against Scenario 1's
2030 and 2045 checkpoints (`solve_2030_reserve_margin_test.py`,
`solve_2045_reserve_margin_test.py`). One real implementation gap was
caught and corrected in the process, not left silent: the constraint
function credits only the fresh solar-build variable's own contribution
at the peak hour, with no parameter for a prior-checkpoint carry-forward
— at a linked checkpoint (2045, linked to 2040), this would have
artificially undercounted already-available capacity and made the
constraint stricter than it should be. Corrected by manually crediting
the carry-forward's own peak-hour contribution to the constraint's
right-hand side before solving.

**Result — the constraint's impact is genuinely checkpoint-dependent,
not uniform:**

- **2045**: constraint is present but **not binding** — the build is
  identical to the existing, no-reserve-margin baseline to many decimal
  places (85,198.4 MW solar, 51,743.6 MW Na-power, both exactly
  matching). Scenario 1's own, already-extreme 99.92%-clean requirement
  at this checkpoint already over-builds far enough that 17.7% reserve
  margin is satisfied incidentally.
- **2030**: constraint is **genuinely binding**. Na-power build jumps
  from 68.0 MW (no reserve margin) to 5,080.6 MW — solar is unchanged.
  This is mechanistically sound, not an artifact: the peak-net-demand
  hour is an evening/night hour where solar contributes nothing
  regardless of how much capacity exists, so only dispatchable storage
  can close the reserve-margin gap at that specific hour.

**Implication, stated plainly rather than assumed:** a full re-solve
campaign — every checkpoint, every intermediate year, across Scenario
1, 1B, and 2 — would materially change some, though evidently not all,
of this project's existing results. Given the scale of that undertaking
(dozens of year-solves, each requiring its own re-verification), this
is treated as a distinct, separately-scoped piece of future work rather
than something completed incidentally alongside this mechanism test.
See P.4.

#### #4. Gas generating fleet (any scenario using gas capacity, existing or newly built)

- Existing gas generating capacity must be verified directly against
  each plant owner's own current, published information — not inferred
  from indirect signals such as a plant showing no measured output over
  some recent period, which typically reflects the plant being held in
  low-utilization standby rather than genuinely retired, unless
  retirement is independently confirmed. Wherever a plant's status is
  corrected in one part of this project's calculations, the same
  correction must be checked and applied everywhere else that plant is
  referenced (for example, a plant's operating status affects both how
  much existing capacity is credited toward meeting demand, and what
  pollution-control classification is assumed for it in the social-cost
  calculations — both must reflect the same, correct status).
- When sizing new gas capacity, an existing combined-cycle gas turbine
  plant's (CCGT's) capacity beyond what is needed to meet sustained,
  continuous ("baseload") demand should be credited toward meeting
  short-duration peak demand as well — that capacity does not stop
  existing simply because a baseload-only calculation does not need all
  of it.
- It must be verified directly, not assumed, that existing capacity plus
  newly built capacity sums exactly to the total capacity required at
  every single year, not only at the original checkpoint years.
- New gas capacity must be cost-accounted at the price that prevailed in
  the year it was actually built, not re-priced at a later year's
  current cost — the same principle applied to solar and storage.
- New gas capacity must be checked against realistic equipment
  procurement lead times: as of this project's most recent sourcing,
  approximately 2 to 4 years for simple-cycle combustion turbines, and 5
  to 7 years for larger combined-cycle units — both figures currently
  tight and reportedly still lengthening. Any new-build requirement
  falling inside this lead-time window relative to when construction
  would need to begin should be explicitly flagged.
- Nitrogen oxide (NOx) emissions should be estimated using each plant's
  actual pollution-control equipment status — specifically, whether it
  is equipped with dry low-NOx (DLN) combustion technology, which
  substantially reduces NOx emissions relative to uncontrolled
  combustion — rather than a single, uniform assumption applied to the
  entire fleet. The confidence level behind each plant's classification
  (directly confirmed, strongly inferred, weakly inferred, or no
  evidence either way) should be disclosed.

#### #5. Capacity sizing when a resource faces no cost penalty within the optimizer's own objective

If a resource — typically gas capacity — is left uncapped, or capped
only loosely, within an optimization whose cost-minimization objective
does not actually charge for that resource's own construction cost, the
optimizer's chosen output for that resource is not a valid estimate of
the truly cost-optimal build size. The optimizer has no mathematical
reason to economize on a resource it is not being charged for within
its own objective function, and so may choose a far larger amount than
a genuinely cost-optimal build would require. The correct approach is
to determine optimal sizing separately, by testing multiple candidate
capacity levels against the true total system cost — the optimizer's
own objective value plus the construction cost of that capacity, priced
externally — rather than reading the unconstrained optimizer's own
chosen output directly as the answer.

#### #6. Terminal value

Any asset whose useful operating life extends beyond the end of this
project's 2045 study window (25 years for solar and battery storage; 30
years for gas generating equipment) should have the unrecovered portion
of its construction cost credited back against total system cost as
"terminal value" — representing the real, ongoing value of an asset that
will keep operating productively after the study window ends. This
credit must be calculated for every year's construction individually
across the full 20-year build-out, not concentrated at only a handful of
checkpoint years, which would artificially inflate the credit available
at those specific points relative to a build spread more evenly across
the full period.

This mechanism has a known, disclosed limitation worth remaining alert
to: because only a small fraction of a late-built asset's operating life
has elapsed by the time the study window ends, most of that asset's
construction cost is still "creditable" as terminal value. This can make
building a larger amount of expensive, long-lived capacity right at the
end of the study window appear less costly overall than building less —
purely as an artifact of how much life remains uncounted at the window's
edge, not necessarily because building more was genuinely the cheaper
choice. This is not established to be a modeling error, but it is a real
feature of the convention, and should be explicitly flagged whenever it
materially affects a comparison between scenarios (as it does in the
comparison between Scenario 1 and Scenario 1B — see Appendix N.4).

#### #7. Demand and weather-year basis

The same, current demand forecast should be used consistently across
every year-solve — this project's Virginia-only demand total, adjusted for
the flattening effect of data-center load growth described in Appendix
O — rather than an outdated or scenario-specific demand source. The
same, established historical weather year (a full year of actual
recorded solar, wind, and hydroelectric conditions from 2016-2017)
should likewise be used consistently, unless a different weather year is
being deliberately tested as its own, explicitly labeled stress-test
case.

#### #8. Export and curtailment treatment

**Export revenue must never appear inside any year-solve's own
optimization objective, in any scenario.** This is a deliberate,
standing, project-wide rule, not a choice made independently for each
scenario. Surplus generation the optimizer cannot otherwise use (for
example, solar output on a low-demand day exceeding what can be
consumed or stored) becomes curtailment — a quantity the optimizer
tracks but is not paid for. If export revenue were instead included
within the optimizer's own objective, the optimizer would have a direct
financial incentive to build or dispatch more generating capacity than
demand actually requires, specifically to capture that revenue — turning
what is meant to be a least-cost-to-serve-demand calculation into
something closer to a profit-maximizing merchant generation calculation.
Where export revenue is relevant to a scenario's final results, it must
instead be calculated separately, after the optimizer has already
finished solving, by applying an export price to whatever curtailed
energy resulted from the optimizer's own dispatch decision (subject to a
transmission/interconnection export volume limit) — entirely outside,
and with no influence upon, the optimization itself.

This project's own history contains a direct illustration of why this
rule exists. An earlier version of the Scenario 2 calculation
mistakenly included export revenue inside that scenario's optimization
objective, carried over from Scenario 1/3's code without reconsidering
whether it belonged there. The result was that the optimizer began
operating gas generating capacity as a profit-seeking merchant
generator rather than solely to serve demand — identifiable at the time
because the resulting export revenue came out identical at every
checkpoint regardless of demand level or how much clean generating
capacity was available, which is not a physically sensible outcome. This
was a coding error corrected on discovery, not a considered,
scenario-specific policy choice — the same rule applies, and always was
intended to apply, to every scenario alike.

**[If Scenario 1 or 1B: the LP-building function retains an optional,
disabled-by-default parameter that would allow export revenue inside
the objective, kept only for testing purposes — production solves must
leave it disabled.]**

**[If Scenario 2: the LP-building function contains no export-revenue
mechanism at all — there is no parameter to disable, since the
mechanism was removed entirely after the incident described above.]**

**A separate, genuinely scenario-specific difference** — not to be
confused with the rule above — is whether curtailed energy is monetized
after the fact at all, once export revenue has correctly been kept out
of the optimization itself.

**[If Scenario 1 or 1B: results do include a post-hoc export-revenue
calculation applied to curtailed energy.]**

**[If Scenario 2: results do not include this calculation, and this is
a deliberate decision, not an oversight. Scenario 2 curtails energy
only at the 2030 checkpoint (121 thousand MWh total, confined to 65
hours out of that year's 8,760), an amount small enough, relative to
the scale of this project's overall results, that building and
maintaining a separate post-hoc export mechanism for Scenario 2 was
judged not worth the added complexity.]**

#### #9. Social Cost of Carbon, Social Cost of Greenhouse Gases, Health Impacts, and Tier 3 (air toxics)

Every scenario-solve must calculate the Social Cost of Carbon, the
Social Cost of Greenhouse Gases, and Health Impacts, and must disclose
Tier 3 findings even though Tier 3 is not converted to a dollar figure.
These are this project's standing framework for the costs a scenario's
gas generation imposes beyond its direct financial price — costs real
to the people and climate affected by that generation, but not
reflected in a fuel bill. Full methodology, sourcing, and plant-specific
detail live in Appendix D; this section states only the requirement
that every scenario-solve must satisfy.

**Naming, per direct user direction this session (supersedes this
project's earlier internal "Tier 1/Tier 2" shorthand as the primary,
reader-facing labels — the three-tier structure is retained only as an
internal organizing principle, cross-referenced below):**

- **Social Cost of Carbon** — Virginia's own statutory concept (Va. Code
  §56-598(2)(d)/§56-585.1(A)(6)), carbon-dioxide-only, addressed
  individually because the statute specifically calls it out by name.
  This project's own "Virginia SC-CO2" (naming history below).
- **Social Cost of Greenhouse Gases** — the broader, multi-gas figure:
  carbon dioxide, methane, **and nitrous oxide (N2O)** — stated
  explicitly here because this is easy to mistype as nitrogen oxides
  (NOx), a criteria pollutant tracked separately under Health Impacts,
  not a greenhouse gas. Both figures — Social Cost of Carbon and Social
  Cost of Greenhouse Gases — are required, reported side by side, not
  one in place of the other.
- **Health Impacts** (formerly "Tier 2") — fine particulate matter,
  sulfur dioxide, and nitrogen oxide emissions from the same gas
  dispatch, monetized using the EPA's own published benefit-per-ton
  figures for the electric generating sector. Nitrogen oxide emissions
  specifically must use the plant-specific pollution-control
  classification required by #4, not a single fleet-wide assumption.
- **Tier 3 (disclosed, not monetized)**: additional, harder-to-monetize
  effects — for example, elevated cancer risk from air toxics such as
  formaldehyde and benzene, and findings from the current public-health
  and regulatory literature on gas-fired generation sited near
  residential areas — must be identified and cited, even though this
  project does not convert them to a dollar figure. Confirmed directly,
  not merely inherited: no sufficiently robust, defensible dollar-per-
  ton figure exists for these effects at this project's level of
  sourcing, so including an invented one would create false precision
  rather than genuine insight. Tier 3 is excluded from this project's
  dollar-denominated "total societal cost" figures by design, and that
  exclusion should be stated plainly wherever a total societal cost
  figure is presented, not left implicit.

**Scope, confirmed directly with the user rather than assumed: natural
gas emissions and impacts only, no diesel.** Checked before treating
this as a new restriction — it was already true of the existing
methodology, not a change. AP-42 emission factors are already Section
3.1 (stationary GAS turbines, not diesel/reciprocating engines); the
BenMAP rates are already the EGU category. The LP model itself never
dispatches diesel either — no diesel variable exists anywhere in this
project's own LP formulation.

**Social Cost of Carbon must be reported as its own, separate figure
from Social Cost of Greenhouse Gases — not combined into one — per
Virginia law.** Virginia Code §56-598(2)(d) and §56-585.1(A)(6) require
the State Corporation Commission to separately consider a Virginia-
specific "social cost of carbon" — a distinct, carbon-dioxide-only
concept — when evaluating applications to construct new generating
facilities. **Naming note**: an earlier draft of this appendix called
this statutory concept "Virginia SCC" — since corrected, given this
project's audience explicitly includes State Corporation Commission
staff and this Commission's own acronym must stay unambiguous
throughout. The Virginia Code itself never abbreviates the concept (it
spells out "the social cost of carbon" in full at every use); the
Commission's own filings likewise default to the universal-but-now-
conflicting "SCC," and Virginia's Department of Energy has no distinct
acronym of its own. Following down to the next available source, this
project adopts the U.S. EPA's own, current (2021-onward) Interagency
Working Group terminology, which already distinguishes the single-gas
and multi-gas versions of this concept by name: **"SC-CO2"** for the
carbon-dioxide-only metric, **"SC-GHG"** for the combined multi-gas
concept. This project refers to Virginia's own statutory concept as
**"Virginia SC-CO2"**, to keep it clearly disambiguated from **"SCoC"**,
the generic economic term for the social cost of carbon dioxide
emissions used throughout this appendix and the broader literature.

The statute directs the Commission to determine Virginia SC-CO2 using
the best available science, citing the 2016 Interagency Working Group
technical support document as guidance — not this project's usual
2023-updated EPA source for SCoC. **As of this project's most recent
sourcing, the Commission has never actually set a Virginia-specific
rate**, despite the requirement dating to 2020; in practice, Virginia
utilities have used an assumed federal placeholder figure roughly a
quarter the size of the 2023 EPA estimate. Absent an actual Commission
determination, this project uses the EPA's 2023 SCoC schedule's own
carbon-dioxide-only rate as the best available proxy for Virginia
SC-CO2 — the same underlying rate used for the CO2 portion of Social
Cost of Greenhouse Gases, simply reported as its own line — with this
choice of proxy stated explicitly wherever Virginia SC-CO2 is
presented, not left implicit. Should the Commission ever set an actual
Virginia-specific rate, that rate should replace this proxy.

At the executive-summary and technical-summary level (as opposed to
this appendix's own, full detail), a brief footnote explaining this
proxy choice is sufficient — full statutory citation and reasoning
belong here, not repeated at every level of summary.

**Both undiscounted and NPV figures are required, reported side by
side, per direct user decision this session — researched rather than
assumed which convention state IRPs actually use.** Physical emissions
(tons) are reported undiscounted essentially universally across
surveyed state IRPs (Indiana Michigan Power's own IRP, PG&E's own IRP),
consistent with discounting being a time-value-of-money concept that
does not apply the same way to a physical quantity. Once monetized into
dollars, practice genuinely diverges: Kansas City Power & Light
(Missouri) folds monetized environmental cost directly into the same
discounted NPV of revenue requirements used to rank competing plans;
Glendale Water & Power's own IRP explicitly excludes emissions costs
from its own "20-year present value" figure, reporting them separately
instead. No single settled convention was found. This project reports
both: the undiscounted total as the primary/headline figure (the more
universal convention, and the one most directly comparable to how
physical emissions are reported), and an NPV figure at this project's
own established 4.5% real WACC and 2026 base year as a secondary
figure, specifically for direct comparison against SLCOE's own
discounting — neither is presented as the sole correct figure.

**Both rate tables this section depends on required a base-year
correction, found and fixed this session, prompted by a direct user
question about inflation treatment.** This project's WACC is explicitly
real (constant-dollar), which is the correct convention and avoids
needing to separately model general inflation — confirmed directly, not
an oversight. But the two EPA rate tables underlying these figures are
each anchored to a different, earlier reference year than this
project's own 2026 base year, and "real 2020$" is not the same
reference point as "real 2026$" without an explicit conversion. The
EPA's own SC-GHG table is denominated in 2020$; the EPA's own BenMAP
benefit-per-ton rates are denominated in 2016$. Both re-based to 2026$
using deflators sourced directly from the U.S. Bureau of Labor
Statistics (not estimated, and not pulled from a secondary calculator):
2020 annual average CPI-U = 258.811; 2016 annual average CPI-U =
240.007; most recent available (July 2026, not seasonally adjusted)
CPI-U = 333.918 (BLS CPI Summary, July 2026 release). Deflators: 1.2902
(2020→2026, 29.02% cumulative) for the SC-GHG table; 1.3913 (2016→2026,
39.13% cumulative) for the BenMAP rates. The second mismatch was caught
only because the Health Impacts total failed to move at all after the
first correction was applied — worth checking why a number didn't
change, not just confirming a fix ran without error.

Both Social Cost of Carbon/Greenhouse Gases and Health Impacts are
subject to the same full-window coverage requirement as #1: they must
be calculated across all 20 years of a scenario-solve, not from a
subset of checkpoint years. **This requirement is now genuinely met for
Scenario 1**, as of this session — all 20 years (four checkpoints plus
sixteen non-checkpoint years) computed on corrected demand, SLCR, and
(checkpoints) reserve margin throughout, not approximated from a
subset. Scenario 2 has not yet received the same full-20-year
recalculation on a corrected basis; treat its own figures as still
reflecting the project's prior, four-checkpoint-only methodology until
explicitly redone.

**Current Scenario 1 totals, 20-year, all corrections applied (undiscounted / NPV at 4.5% real WACC, 2026$):**

| Figure | Undiscounted | NPV |
|---|---|---|
| Social Cost of Carbon (CO2 only) | $97.965B | $71.701B |
| Social Cost of Greenhouse Gases (CO2+CH4+N2O) | $107.481B | $78.577B |
| Health Impacts (PM2.5+SO2+NOx) | $7.702B | $5.740B |

See P.4 for Scenario 2's own, still-outstanding recalculation status.

#### #10. Land acreage

Every scenario-solve must calculate the physical land area its
generation and storage build-out requires, for every year of the
20-year window, not only at a single point in time — land requirements
grow year over year exactly as generating capacity does, and a figure
reported only at 2045 would understate the land committed at every
earlier year along the way.

- **Solar**: this project uses **6.93 acres per MW (AC)** as its
  primary land-use figure, sourced from a 2024 Virginia-specific study
  of utility-scale solar development in the Commonwealth — preferred
  over a generic national average because it reflects actual Virginia
  siting conditions and project experience, not a broader, less
  directly applicable figure. This falls within, and is corroborated
  by, the wider published range for utility-scale solar nationally
  (roughly 5-9 acres/MW across NREL and industry sources, depending on
  fixed-tilt vs. tracking technology and whether direct or total land
  area is being measured). Applied to whichever solar capacity figure
  a scenario's own build-out produces at each year — nameplate, not
  degraded/effective capacity (#2), since land is committed based on
  what was physically built, not on how much output it currently
  generates.
- **Onshore wind, battery storage, and new gas capacity**: this
  project's only wind resource (Coastal Virginia Offshore Wind) is
  offshore and does not have a comparable land-acreage requirement in
  the same sense — though onshore interconnection and substation
  infrastructure should be separately, if only qualitatively, noted.
  Battery storage and gas generating equipment both have substantially
  smaller land footprints per MW than solar; figures for both should be
  sourced and disclosed with the same rigor as the solar figure above
  before being included in any land-acreage total, rather than assumed
  or omitted.
- **Agrivoltaic and dual-use land (Scenario 3-specific)**: Scenario 3's
  own definition calls for a substantial share of its non-urban solar
  build-out to use agrivoltaic arrangements (solar co-located with
  continued agricultural use of the same land). Whether this project
  treats agrivoltaic acreage as equivalent to standard, exclusive-use
  solar acreage, or as a distinct, dual-use category with a different
  land-impact accounting, is a methodology decision that must be made
  and disclosed explicitly when Scenario 3's own land-acreage figures
  are calculated — not left as an implicit assumption. See P.3 for
  Scenario 3's own index entry once this is resolved.

Reported land acreage should be presented alongside, not instead of,
MW/MWh capacity figures — acreage is an additional, disclosed impact
metric, not a replacement for the capacity figures this project already
reports throughout.

#### #11. Verification required before any solve is presented as final

- Zero demand goes unserved, unless an unserved-demand shortfall is
  itself the deliberate subject of the analysis.
- Existing plus newly built capacity sums exactly, not approximately, to
  whatever peak or baseload requirement that capacity is meant to cover
  — and once the #3 reserve-margin requirement is properly enforced,
  that requirement itself is the reserve-margin-inclusive target
  ((1+IRM) times peak demand), not raw peak demand alone. Reserve margin
  is a multiplier applied to the requirement being checked against, not
  a separate quantity added to existing and new capacity on the other
  side of the comparison.
- Results for a newly solved year connect smoothly to already-solved
  adjacent years, with no unexplained jump at a checkpoint boundary.
- Every cost component — construction cost, operating and maintenance
  cost, fuel cost, storage cycling cost, export revenue, and terminal
  value — is counted exactly once: neither omitted nor double-counted.
- Zero hours of simultaneous charge and discharge, for every storage
  type — see #13.
- Every cached input file's own totals verified directly against its
  current, authoritative source before use — not assumed correct
  because the file already existed — see #14.

#### #12. Documentation

- Update the relevant appendix section.
- Present the actual script or scripts that produced the figures being
  reported, so that the written narrative and the code that generated it
  can each be checked against the other.
- Add source citations for any newly used external information.
- Update the companion SLCOE spreadsheet wherever a figure there is
  affected, and verify the update by recalculating the spreadsheet
  independently rather than trusting an unverified formula.
- Update any internal reference document for which the correction
  affects data that document is the authoritative source for (for
  example, the master gas-plant status file).
- Log the change in this project's activity tracker.
- Record the issue in this project's internal debugging log: the problem
  as originally identified, each fix attempted (including any attempt
  that failed, was incomplete, or was itself later found to contain an
  error — this project's history includes real examples of a first fix
  attempt introducing a new problem while resolving the original one),
  and the fix that was ultimately verified successful. This log is a
  working record distinct from the activity tracker: the activity
  tracker records completed, verified outcomes for external reference,
  while the debugging log preserves the fuller, messier process — including
  dead ends — so that a later reviewer (or a later solve encountering a
  similar-looking problem) can see what was already tried, not only what
  finally worked.
- Note explicitly whether the change warrants an update to the
  project's white paper, rather than updating it automatically for every
  incremental finding.
- If a new, generally applicable requirement was identified in the
  course of this solve — not merely a one-off, scenario-specific fix —
  add it to this appendix's General Procedure section, not only to the
  specific scenario's own appendix.

#### #13. Storage dispatch degeneracy (simultaneous charge and discharge)

A linear program has no inherent reason to avoid a physically
impossible state — a given storage resource charging and discharging in
the same hour — unless something in the problem's own cost structure or
constraints actively prevents it. Energy-balance accounting is
indifferent to this: charge and discharge terms cancel identically in
the balance equation regardless of their individual magnitude, so an LP
solver can produce large, simultaneous, offsetting flows that are
mathematically valid but represent no real operational behavior.

**This project's own history contains an extensive, hard-won record of
what does and does not fix this**, worth treating as settled rather
than re-investigated from scratch at any future checkpoint or scenario
(full detail: Internal Debugging Log #5, #12, #19-20.7):

- **Structurally rigorous fixes exist (true complementarity via binary
  variables) but are not viable at this project's problem scale.**
  Proven correct (zero violations, true optimality) on a 30-day test
  window, but took ~470 seconds for one storage type over 1/12th of a
  year — extrapolated to a full year across all three storage types,
  this would plausibly take multiple hours per solve, incompatible with
  a normal workflow requiring several solves per checkpoint.
- **Economic deterrents sized to discourage, not structurally prevent,
  the behavior have a mixed record and must be verified directly, not
  assumed to work by design.** A small charging-side cost incentive did
  nothing; a large one caused solver timeout without reliably fixing the
  pattern either. Post-hoc netting (removing equal charge/discharge
  amounts after solving) is energy-balance-safe in principle but proved
  physically inapplicable at this project's actual scale — the
  phantom-cycling volume involved was found to be over 280 times the
  built battery's own capacity, far beyond what any repair algorithm
  could absorb. A published, purpose-built linear reformulation (Nazir &
  Almassalkhi 2021, "RBD") was tried and rejected — its safety margin,
  which scales with round-trip efficiency, proved too severe at this
  project's storage efficiencies and caused the optimizer to abandon
  Na-ion storage entirely rather than tolerate the tax.
- **The mechanism actually in standing use in this project's own
  `build_problem()`**: real, sourced discharge-side cycling costs
  (Sandia methodology, cycle-life data) for all three storage types.
  This is not a cost-based deterrent in the same speculative category as
  the rejected attempts above — it reflects a genuine, physically real
  cost (accelerated degradation from cycling) that happens to also
  suppress the degenerate behavior as a side effect, not a tie-breaker
  invented solely to force a particular dispatch pattern.

**Standing requirement**: any new solve — including, but not limited to,
Scenario 3's own build, which introduces storage dispatch in a new
context (DER-owner-operated distributed storage, potentially under
different dispatch incentives than this project's existing
utility-scale-only storage) — must directly verify zero hours of
simultaneous charge and discharge for every storage type before being
presented as final, per #11 below. This must be checked directly against
the solved hourly output (`charge[t] > 0 and discharge[t] > 0`
simultaneously, for any hour), not assumed from the presence of a
cycling-cost term alone — the cost term's effectiveness at a new
checkpoint's specific parameterization is an empirical question, not a
mathematical guarantee, per the SLCR trial's own finding (Internal
Debugging Log #20.7) that a mechanism's effectiveness can vary by
checkpoint depending on which constraints are actually binding there.

#### #14. Input data verification — cached files must be checked against their own current, sourced generation logic before use

A persisted input file (an `.npz`, a `.csv`, or any other cached data
product) being already present, already used in a prior checkpoint, or
already described in an appendix as established is not, by itself,
evidence that the file is correct. This project's own history shows
files can silently go stale relative to the sourced logic that is
supposed to generate them — the underlying source table or function
gets corrected, but the already-saved file built from an earlier version
of it is never regenerated, and nothing forces the two to be checked
against each other again.

**The motivating finding.** All four of Scenario 1's checkpoint demand
files (`checkpoint_2030_demand_v2.npz` through `checkpoint_2045_46_
demand_v2.npz`) were found, this session, to disagree with this
project's own current, correctly-sourced annual-total table
(`demand_shape_interpolation.py`'s `_COMMERCIAL_AND_TOTAL_GWH`, Appendix
O) by between 6% and 30%, with the direction and magnitude of the
disagreement varying by year — not a uniform scaling error, and not
something a quick plausibility check would have caught. Direct
investigation (comparing each file's own normalized hourly shape against
what today's `flattened_hourly_demand()` produces) confirmed the
underlying shaping logic itself was not at fault — the files' own
hour-by-hour distribution pattern matched almost exactly (well under
0.01% divergence in every case checked). The discrepancy was isolated
entirely to the annual-total value that had been passed in in each
file's own original build — most likely an earlier, since-superseded
demand-forecast vintage that was never reconciled against this project's
later, corrected source table. **This means every Scenario 1 checkpoint
result — build sizes, dispatch, Social Cost of Carbon/Greenhouse Gases,
Health Impacts, SLCOE — computed from these
files throughout this project's history was built on demand this
project's own current sourcing does not support.** See P.4 for the
resulting re-solve status.

**Standing requirement.** Before any solve uses a cached input file for
a project-wide, sourced quantity (demand totals, weather-year capacity
factors, existing-generation capacity, or any other input this project
maintains its own authoritative table or generation function for), the
file's own totals must be checked directly against that current,
authoritative source — not assumed consistent because the file already
exists or was used in an earlier, already-completed checkpoint. Where a
generation function exists (as it does for demand, via
`flattened_hourly_demand()`), the check should compare both the
aggregate total (a single sum) and, where feasible, the normalized shape
against a freshly-generated reference — the demand finding above
specifically depended on checking both, since the shape matching so
closely was what made "stale total, not stale logic" the correct
diagnosis rather than a deeper bug.

### P.3 Scenario-Specific Requirements — Index

Each scenario's own methodology creates requirements beyond the parts
of P.2 above that apply uniformly to every scenario. Rather than
duplicating that scenario-specific content in a separate section, it is
placed inline within P.2, directly next to the general rule it modifies
or adds to, marked with a bracketed **[If Scenario ...: ...]** note.
Keeping the exception next to the rule it modifies, rather than in a
separate section, is meant to prevent the two from drifting apart as
this appendix is revised — an editor changing a general rule is far
more likely to notice and update an adjacent scenario-specific note
than one located several sections away.

This section serves as an index only: for each scenario, which
sections of P.2 currently contain a bracketed note affecting it. It
does not restate what those notes say — follow the section reference to
read the note itself, in context, next to the general rule.

- **Scenario 1 / 1B**: #2 (solar degradation happens automatically via
  vintage tracking); #8 (export-revenue parameter present but disabled
  by default; post-hoc export-revenue calculation included).
- **Scenario 2**: #2 (solar degradation must be separately calculated,
  since capacity follows an externally-set schedule rather than an
  optimizer decision); #8 (no export-revenue mechanism exists in the
  LP at all; no post-hoc export-revenue calculation applied, a
  deliberate decision given the small, single-checkpoint scale of its
  curtailment).
- **Scenario 3**: no bracketed notes yet — scenario not yet built. Once
  built, this index should be updated at the same time any new,
  scenario-specific bracketed notes are added to P.2, consistent with
  #12's requirement that new general requirements be added to this
  appendix as part of documenting the work that discovered them.

### P.4 Disclosed Gaps Against This Procedure, as of This Appendix's Creation

- **Reserve margin (#3) — value settled, mechanism tested, project-wide
  application still open.** 17.7% IRM settled by direct user decision.
  Mechanism verified on two test cases (Scenario 1's 2030 and 2045
  checkpoints): non-binding at 2045, genuinely binding at 2030 (Na-power
  build increases roughly 75x at that checkpoint alone). This confirms a
  full re-solve — every checkpoint and intermediate year, across
  Scenario 1, 1B, and 2 — would materially change some, not all, of this
  project's existing results. Not yet undertaken, given its scale;
  logged here as the next, distinct piece of work rather than assumed
  complete because the mechanism itself now works.
- **Scenario 1B vs. Scenario 2 comparison (Appendix N)**: still based on
  Scenario 2 figures that predate the corrections in Appendix C.12 and
  C.13. This has been deliberately deferred to a dedicated pass rather
  than addressed incidentally, and is not an oversight.
- **Plant retirement-year cross-reference (#4)**: the retirement years
  used in this project's social-cost NOx classification have not yet
  been checked against the corrected plant roster used for gas capacity
  crediting elsewhere in the project. Believed likely immaterial (the
  classification of which plants have DLN pollution controls is
  unaffected either way), but not yet formally verified.
- **Scenario 1's own reserve-margin status**: covered by the general #3
  gap above. Scenario 1's checkpoint solves were established earlier in
  this project's history and have not yet been individually re-audited
  against this appendix.
- **Social Cost of Carbon / Social Cost of Greenhouse Gases / Health
  Impacts, Scenario 1's own full 20-year figures (#9): now complete.**
  All 20 years computed on fully corrected dispatch (demand basis, SLCR,
  reserve margin for the four checkpoints; statutory RPS share, SLCR,
  corrected demand shape for the sixteen non-checkpoint years), with
  both EPA rate tables re-based from their own original vintages (2020$
  and 2016$ respectively) to this project's 2026 base year using
  BLS-sourced deflators. Both undiscounted and NPV figures reported, per
  direct user decision (state-IRP practice researched, found genuinely
  mixed, both treatments presented rather than one chosen unilaterally).
  Current results in #9 above. **Scenario 1B and Scenario 2 still not
  done** — both remain on the project's prior, four-checkpoint-only
  methodology and the original, un-rebased EPA rate vintages until
  explicitly recalculated on the same corrected basis as Scenario 1.
- **RGGI compliance cost, this session: implemented for Scenario 1.**
  Virginia rejoined the Regional Greenhouse Gas Initiative (RGGI) on
  July 1, 2026 — a market-priced, cap-and-trade compliance cost gas
  generators must actually pay, genuinely distinct from Social Cost of
  Carbon and Social Cost of Greenhouse Gases, which are externality/
  social-cost estimates, not real, billed expenses. RGGI cost is folded
  into direct financial SLCOE's own numerator (alongside gas and cycling
  cost, offset by export revenue) — not #9's dollar total.

  **Single figure, RGGI's own published Cost Containment Reserve
  trigger-price schedule** ($18.22/ton in 2026, then $19.50 escalating
  7%/year from 2027)*. An initial two-tier approach (this schedule
  alongside the actual, current market-clearing price) was tried and
  set aside — both tiers landed close enough together ($46.22 vs.
  $46.96/MWh) that presenting both risked reading as false precision
  rather than genuine bounding, and the two also cross in direction over
  the window (the schedule's own mechanical compounding eventually
  exceeds a held-flat market price), which added explanatory overhead
  without adding much real information. One figure, with the caveat
  below, communicates the same substance more clearly.

  **\* RGGI's own actual, current market-clearing price already runs
  above this schedule** — the most recent auction (Auction 72, June
  2026) cleared at $35.00/ton, well above the $18.22-$19.50 trigger,
  reflecting real scarcity from Virginia's re-entry and a newly
  tightened regional cap, not a hypothetical outcome. The figure below
  should be read as a plausible, published lower reference, not a
  prediction that RGGI cost will stay this low.

  **Result, Scenario 1**: SLCOE with RGGI (regulatory-schedule tier):
  $46.22/MWh, vs. $42.45/MWh without RGGI.

  **Result, Scenario 1B**: SLCOE with RGGI: $45.94/MWh, vs. $42.14/MWh
  without RGGI — reused Scenario 1's own RGGI cost directly for
  2026-2044 (identical dispatch by construction), recomputed only 2045
  from 1B's own dispatch. Total 1B RGGI cost $9.799B undiscounted (vs.
  Scenario 1's own $9.701B) — slightly higher single-year RGGI cost at
  2045 than Scenario 1's own, but still outweighed by zero new build
  needed there, so 1B stays marginally below Scenario 1 even with RGGI
  included.

  **Result, Scenario 2: all three gas cases.** Same regulatory-schedule
  price, Scenario 2's own, much larger CO2 tonnage throughout the window
  (sustained 39-59% gas share vs. Scenario 1's decline to near-zero):
  total RGGI cost $24.118B undiscounted, roughly 2.5x Scenario 1's own
  figure. **These SLCOE-without-RGGI figures were corrected after the
  RGGI addition was first built**, once a real, confirmed CCGT capex
  bug was found and fixed (Internal Debugging Log #49) — the RGGI cost
  itself ($24.118B) is unaffected by the capex correction, since it
  depends only on gas dispatch volume, but the SLCOE it's added to
  moved up with the corrected capex:

  | Gas case | SLCOE without RGGI | SLCOE with RGGI |
  |---|---|---|
  | Deloitte | $48.99/MWh | $56.70/MWh |
  | EIA | $43.77/MWh | $51.48/MWh |
  | Hughes | $49.43/MWh | $57.15/MWh |

  **Status: all three scenarios (1, 1B, 2) now have RGGI folded into
  their own SLCOE, and D.3's own table now shows the resulting
  total-societal-with-RGGI figure explicitly, as its own distinct line
  — this open item is now closed, not still pending.**
- **Land acreage (#10)**: newly added requirement, not yet calculated
  for any scenario. Solar land-use figure sourced (6.93 acres/MW,
  Virginia-specific); battery storage and new gas capacity figures not
  yet sourced; Scenario 3's agrivoltaic dual-use land accounting not
  yet decided. Deliberately deferred alongside the items above, for the
  same reason — land acreage should be calculated against each
  scenario's final, post-reserve-margin build-out, not recalculated
  twice.
- **Multi-year weather-year min-max robustness finding — RESOLVED for
  the hard-constraint, 2045-checkpoint case (this session); narrower
  scope remains open.** The finding that 2016-17 is the min-max-robust
  choice among 2016-17/2013-14/2012-13 has now been genuinely re-solved
  and cross-tested at this project's current, Virginia-only demand
  basis, using primary-source SAM data provided directly for this
  purpose (three reference solar locations plus CVOW wind, 2012-2014).
  Full detail and results in Appendix A.2. Confirmed: 2016-17 remains
  the unique zero-unserved-energy design against both other tested
  years, at the hard (0.08% gas) constraint, 2045 checkpoint. This
  closes the verification gap this item originally logged.
  **Narrower scope still open, explicitly not claimed as covered**: this
  re-verification has not been repeated for the soft (5% gas) constraint
  case, nor for checkpoints other than 2045. The original (DOM-LSE-basis)
  finding reported all three designs mutually robust under the soft
  constraint; there is no specific reason to expect that to change at
  current demand, but it has not been directly re-confirmed and should
  not be presented as verified until it is.
