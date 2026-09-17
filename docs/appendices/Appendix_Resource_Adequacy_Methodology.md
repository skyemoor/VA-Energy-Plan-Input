# Appendix — Resource Adequacy Methodology

**Extracted 2026-09-14 from `Reorganized_Appendices_Draft.md`, where it existed only inside a 4,682-line composite file.** That draft also carried stale copies of five appendices that have their own authoritative files; this one had no standalone version at all, which made it invisible to the index, untestable, and impossible to revise without editing a file about something else.

Lettering is deliberately omitted here. The scheme is being reworked into reader order (methods, scenarios, topics, reference) and a letter baked into the filename now would be wrong twice.

> **PARTLY SUPERSEDED 2026-09-14.** This predates the loss-of-load and unserved-energy metrics now
> in `lp_package/reliability_metrics.py`, and the distinction this project now draws between
> CAPACITY PLANNING (is enough built — installed reserve margin against accredited capacity) and
> RESOURCE ADEQUACY (does it serve load — loss-of-load hours, unserved energy, event count and
> duration, per NERC 2026).
>
> `docs/Common_Reference.md` sections 2 and 3 carry the current position, including what is
> deliberately not claimed: these are realisations under one weather year with no forced-outage
> draws, so they are not LOLE or expected unserved energy, and conditional value at risk is not
> offered. **This appendix remains the fullest account of the accreditation and reserve-margin
> method** and should be merged with those sections rather than replaced by them.

---

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
