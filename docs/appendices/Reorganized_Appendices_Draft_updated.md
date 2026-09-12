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
Three hydrological years (April-March, avoiding mid-winter-event splitting)
were independently solved and cross-tested: 2016-17 (captures the Dec
2016-Feb 2017 sustained low-insolation event), 2013-14 (Polar Vortex), and
2012-13 (the most severe short-window insolation lull in the sample). Applying
Zeyringer et al.'s (2018, *Nature Energy*) min-max robustness criterion,
2016-17 is the unique design with zero unserved energy against both other
tested years' weather — the archetype finding (2016-17 = sustained-drought,
energy-driven; 2013-14/2012-13 = acute-stress, power-driven) held up under a
full re-solve at corrected costs and demand.

### A.3 The Demand-Baseline Correction
A stale cached demand series (built early in this project, never refreshed
when the annual model's own demand trajectory was later revised) understated
every hourly-LP result by roughly 18-20% until caught and corrected via a
targeted sanity check, then a full 36-solve re-verification. Root cause fixed
at the source data level to prevent silent recurrence.

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
inequality (`nuclear[hour_of_maximum_net_demand] + gas_capacity_cap + CVOW_MW x wind_cf[hour_of_maximum_net_demand]
+ storage_power_MW + solar_MW x solar_cf[hour_of_maximum_net_demand] >= (1+IRM) x
demand[hour_of_maximum_net_demand]`) and the checkpoint is re-solved; the peak-net-demand hour
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

### C.3 The Export Correction
An earlier version of this formulation carried over Scenario 1/3's export
mechanism without reconsidering fit. Diagnosis: CCGT was being dispatched as
a merchant generator purely for arbitrage (identical export revenue
regardless of demand or clean capacity was the tell); confirmed via zero
curtailment even with export disabled, ruling out genuine overgeneration.
Export removed entirely; gas dispatch dropped 40-53% as a result.

### C.4 Gas-Price Tier Mechanics
Because storage carries zero marginal cost in this formulation and export is
disabled, dispatch volume is mathematically invariant to the specific gas
price — only cost changes. This allows the Low (EIA) tier to reuse the Base
(Deloitte) tier's solved dispatch figures directly, repriced rather than
re-solved.

---

## Appendix D — Tiered Social Cost Framework

*(Carried forward from the existing white paper section's A.4, relabeled.
No content changes.)*

Three-tier externality framework: Tier 1 (climate, EPA pre-2025 SC-GHG
methodology), Tier 2 (regional health, EPA benefit-per-ton with
density/frequency sensitivity), Tier 3 (air toxics, deliberately qualitative,
never monetized or summed into either dollar total).

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
