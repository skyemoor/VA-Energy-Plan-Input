# The Scenario 3 Model — Structure and Assumptions, for Senior Technical Staff

*Built directly from `lp_model.py`'s own `build_problem()` function — every element below is a
real, current part of the code, verified against it directly, not a simplified restatement.
Structure follows the translation framework in `LinearProgrammingPresentation.docx` (objective →
decision variables → constraints → cost weighting → presenting results), applied to this
project's actual formulation. Audience: senior technical staff — this assumes familiarity with LP
formulation generally (objective functions, decision variables, constraints) and focuses on what's
specific to this project's own implementation, not general optimization concepts.*

## 1. Objective

The model minimizes total annualized cost for a single checkpoint year, composed of two terms:

**CAPEX**: the annualized capital cost of new build — new solar nameplate capacity, plus the
power and energy capacity of sodium-ion and iron-air battery storage. Capital cost is converted to
an annual-equivalent figure via a capital recovery factor (`CRF = WACC(1+WACC)^25 / ((1+WACC)^25 -
1)`, WACC = 4.5% real, 25-year amortization), so it can be compared directly against one year's
operating cost within the same objective.

**O&M**: one year's operating cost — gas fuel burn (where the scenario allows gas at all),
unserved-energy penalty, curtailment cost, and per-cycle wear cost on each of the three storage
types' discharge.

**Note on NPV**: this objective is *not* itself a multi-year NPV or discounted-cash-flow
calculation. The 20-year discounted SLCOE figure this project reports is built afterward, by a
separate step that combines and interpolates between multiple checkpoint-year solves.


## 2. What a linear program actually is, briefly, before the specifics below

For staff whose background is energy management rather than mathematical optimization
specifically: a linear program (LP) is a formal method for finding the best value of some
quantity — here, total cost — by choosing a set of numbers (the "decision variables") subject to
a set of rules those numbers must obey (the "constraints"), where both the thing being optimized
and every rule are expressible as straight-line (linear) relationships among those numbers — sums
and multiples, not squared terms, not if/then branching, not one decision variable multiplied by
another.

Given that structure, a solver (this project uses SciPy's `linprog`, with the HiGHS algorithm)
can search the entire space of numbers that satisfy every constraint simultaneously and guarantee
it has found the genuinely best one — not just a good one, not a local improvement, but the actual
optimum given the stated rules. This exact-optimum guarantee, and the ability to do this search
efficiently even with many thousands of variables (this project's own formulation has on the order
of 8,760 hours times roughly 14 operating choices per hour, plus 4 build choices), is specifically
a property of the *linear* structure — it's also why the constraints below matter as much as they
do: the solver will find and exploit any loophole the linear formulation leaves open that reduces
cost, even one that's physically nonsensical, unless a rule explicitly closes it off. Several items
in section 5 below (the simultaneous charge/discharge issue, the curtailment-cost degeneracy) are
direct examples of exactly that happening in this project's own solves.

For this project specifically: the decision variables are "how much to build" and "how to operate
every hour," the thing being minimized is total cost, and the constraints are the physical and
legal rules — energy balance, storage physics, the RPS cap — the system has to obey regardless of
what's cheapest. The rest of this document is the specifics of each of those three pieces.

## 3. Decision variables

**Build variables** (4, chosen once per checkpoint solve, not per-hour):
- New solar nameplate MW
- Sodium-ion power (MW) and energy (MWh) capacity
- Iron-air energy (MWh) capacity

**Per-hour operating variables** (~14 per hour, repeated across all 8,760 hours of the solved
year):
- Gas dispatch (MW) — in scenarios/years where the gas-allowance cap is nonzero; pinned to zero
  outright in scenarios that exclude gas entirely
- Charge/discharge for each of three storage types: Bath County pumped-hydro, sodium-ion,
  iron-air
- Unserved energy (should converge to ~0 given the penalty weighting — see section 4)
- Curtailment
- Export (bounded to `(0,0)` by default — see section 4; a real, tested variable, not a stub)

## 4. Constraints, by what each one enforces

**Energy balance** (equality, one row per hour): supply (solar + gas + net storage discharge)
must exactly equal demand each hour, with unserved/curtailment/export as the slack variables on
either side.

**Storage state-of-charge dynamics** (equality, per storage type, per hour): SoC tracks
consistently hour-to-hour net of round-trip efficiency losses on the charging leg. End-of-horizon
SoC is enforced as an inequality floor (`SoC[T-1] >= SoC[0]`), not an exact equality — changed this
session per direct user proposal, addressing a real root cause identified in the literature: an
equality constraint can force the LP to actively dispose of energy it would rather retain, and
simultaneous charge/discharge (burning energy via round-trip loss) is the only way to reduce SoC
without touching the instantaneous energy balance. A floor still guarantees the year doesn't end
depleted relative to where it started, without forcing disposal of a surplus the LP would prefer to
carry forward.

**Depth-of-discharge floors**: sodium-ion restricted to [20%, 100%] of nameplate energy capacity
(`NA_DOD_FLOOR`); iron-air unrestricted (0-100%, `FE_DOD = 1.0`), consistent with sourced chemistry
behavior — iron-air is deep-discharge tolerant, sodium-ion is not.

**Power-rate limits and anti-simultaneity**: charge/discharge bounded by each storage type's own
built power capacity; simultaneous charge and discharge of the same storage type in the same hour
is explicitly blocked as a hard constraint, not left to cost-based discouragement alone — confirmed
necessary via direct testing (a 2035 checkpoint solve showed 17 hours of simultaneous Na-ion
dispatch even with the cycling-cost penalty already active before this constraint was added).

**Bath County one-cycle-per-day**: a named operational constraint specific to that facility,
reflecting its actual physical operating pattern, not a cost-driven simplification.

**RPS/gas-allowance cap** (inequality on cumulative gas dispatch): cumulative annual gas
generation is capped at a specified share of total clean generation for the year — this is the
mechanism through which the statutory VCEA/RPS constraint enters the LP as hard math. In gas-free
scenarios, the gas bound collapses to zero rather than invoking this constraint at all.

## 5. Objective coefficients and what they're calibrated to do

**Unserved energy: $100,000/MWh.** Deliberately set high enough that the solver will structure
around it before accepting any unserved demand in a genuinely feasible scenario, without being
literally infinite (which would break solvability in an infeasible one).

**Curtailment: $100/MWh.** Corrected this session's predecessor work from an earlier $0.01-$1.0/MWh
token cost, confirmed via direct testing to have been insufficiently differentiated from a
zero-cost charge variable — the resulting ~1e10 coefficient-ratio problem created a genuine,
reduced-cost-confirmed LP degeneracy (charging into curtailed surplus and discarding it were
computed as cost-equivalent). Direct testing at $1 vs. $100 vs. $5,000/MWh (build size pinned at
its own solved optimum) showed $1 left both Na-ion and iron-air SoC topping out around 71-72% of
cap despite massive simultaneous curtailment, while $100 (confirmed by $5,000 producing no further
change) drove both to 100% utilization with zero additional capacity built — a 43.7% curtailment
reduction from utilization alone, at no capital cost. $100/MWh is independently defensible on its
own terms too (same order of magnitude as gas cost and the export price), not solely a
tie-breaking artifact.

**Gas: the real, time-varying Deloitte-derived $/MWh trajectory for the checkpoint year**
(`gas_cost_mwh(year, heat_rate=SIMPLE_CYCLE_HEAT_RATE)`), not a flat figure held constant across
the study horizon. Verified this session against the actual piecewise-linear interpolation: the
year-over-year increase within each inter-checkpoint segment is genuinely, continuously linear (not
punctuated/stepped), confirmed by direct inspection of year-over-year deltas in the live workbook.
Heat rate matters here specifically: Scenario 3/1/1B/3B/3C are simple-cycle only (9.5 MMBtu/MWh),
distinct from Scenario 2's combined-cycle rate (6.4) — a heat-rate mismatch here previously
understated simple-cycle fuel cost by ~48% across every checkpoint solved before a mid-session
correction; confirmed this session that `driver.py`'s `run_solve()` already calls the function with
the correct rate, so no re-solve was needed on this specific point.

**Storage discharge cycling costs**: real, sourced replacement-cost-per-lifetime-throughput
figures, not a zero or placeholder cost for "already-paid-for" stored energy. Na-ion and iron-air
use the Sandia BESS Cycling Price Model methodology; Bath County uses a DOE/PNNL (Mongird et al.
2020) PSH-specific figure ($7.50/MWh, computed at Bath's own 80% round-trip efficiency).

**Bath County charging-side term: removed (2026-09-04), tested directly rather than assumed
either way.** An earlier -$2.00/MWh charging-side term (mirroring the same-style term already
removed from Na-ion/iron-air once their discharge-side costs were shown to fully resolve
simultaneous dispatch on their own) remained on Bath specifically. Direct synthetic-data testing
this session found: three identical solves with the term present gave the exact same objective
value each time (no Na/Fe-style non-reproducibility for Bath's version) — but removing it also left
build sizes completely unchanged and did not resolve the residual simultaneous-dispatch issue it
was added for (215 vs. 197 hours out of 8,760, both far from zero either way). Removed for
consistency with the Na/iron-air precedent once shown not to be earning its keep, per direct user
confirmation — not because it was shown harmful.

**Iron-air resilience tilt: 3% (`RESILIENCE_TILT_PCT = 0.03`), reinstated 2026-09-04** following
conclusion of an internal trial (Internal Debugging Log #20.6) that required observing the model's
unbiased build choice. This is a small, disclosed, one-directional cost credit breaking a confirmed
near-cost-tie between Na-ion and iron-air build sizes (forcing +5,000 MW Na-ion costs only ~$5M/yr
net against a ~$21B total — genuine indifference, not a rounding artifact). **Documentation split,
resolved this session**: the narrative-facing benefits discussion states iron-air's long-duration
resilience value to host customers and society qualitatively — consistent with how NSPM's own
benefit-cost framework treats resilience (materially attributable to host customers/society, not
to a utility's own centralized build decision). The 3% figure itself is disclosed only in this
technical documentation, not cited in the narrative, since it's a tie-breaking device sized for
that purpose specifically, not an independent valuation of resilience in dollar terms. Also
disclosed, unresolved by design: this tilt is explicitly one-directional — it doesn't credit
sodium-ion's own unpriced fast-response/frequency-regulation value, which argues the opposite
direction.

**Export: bounded to zero by default.** A tested, functioning variable, not a stub — but the
model's standing configuration assumes no wholesale export revenue. This covers only the LP's own
simple curtail-or-export choice each hour. The fuller disposition question — what happens to
surplus generation, particularly from utility-scale solar/battery assets outside the DER-owner
arbitrage compensation framework this project uses elsewhere — is resolved in a calculation
subsequent to this LP, not settled by the LP's own solve, and remains a separate, open discussion
item independent of this on/off switch.

## 6. Items this review resolved, worth carrying forward as the record of what's settled and why

**Bath County's rigid 480 MW discrete pumping blocks**: real (Bath's ~3,000 MW capacity divides
into roughly six ~480 MW units, matching its physical configuration), not modeled as a discrete/
mixed-integer constraint. Resolved as immaterial: max possible rounding gap (~240 MW, half a
block) is small against total system storage/solar flexibility. This model has no geographic/nodal
structure at all — a single system-wide pool, not discrete regions — so the resolution isn't about
nearby resources specifically, it's that total system-wide flexibility, wherever it nominally
sits, already dwarfs this gap.

**Urban/suburban DER-owner overgeneration vs. utility-scale overgeneration — not a contradiction,
once precisely scoped.** Two claims that read as being in tension were actually about different
asset populations throughout: DER-owner arbitrage assets (rooftop/canopy, urban/suburban,
participating in market arbitrage) are absorbed by local demand; utility-scale solar/battery
facilities are a separate matter entirely, outside this project's arbitrage-compensation framework.
Germany's own negative-price/overgeneration experience — verified directly rather than accepted on
assertion, corroborated by multiple independent sources — is attributable specifically to an
insufficient-storage gap (itself substantially policy-driven: guaranteed fixed feed-in tariffs
removed the market incentive to pair solar with storage), not an inherent property of high solar
penetration. This project's own firmed (storage-paired) design does not share that structural gap.

**Distribution-upgrade cost for bi-directional-flow capability**: $500/kW accepted; circuit-count
convention set directly by assumption — 5% of the narrowed urban/suburban, non-data-center-
dedicated circuit subset (1,360-3,200 circuits) will require upgrade, yielding 68-160 circuits,
136-800 MW, **$68M-$400M total**, borne on the utility side (parallel to the transmission-avoidance
treatment elsewhere in this project's compensation structure). This assumption substitutes directly
for empirical feeder-level verification, which is not obtainable — Dominion's own hosting-capacity
tool is a real, existing resource but is architected as an interactive, single-address lookup map,
not a bulk, circuit-by-circuit dataset. Given that data constraint is structural, not a temporary
research gap, a direct, disclosed assumption is the correct closure, not a placeholder.

**Dominion's 15%-of-peak-load screening threshold — sourcing substantially strengthened.**
Previously attributed only to a third-party solar-industry site. Traced this session to FERC Order
No. 792 (2013) itself, which states directly that "the existing 15 Percent Screen... approximates a
50 percent minimum load screen," and that FERC's own adopted standard is actually 100% of minimum
load (having explicitly rejected more conservative 33%/67% alternatives). A federal order is
stronger sourcing than a Dominion-specific filing would likely have provided regardless.

**Minimum-daytime-load window, if used in future feeder-level or hosting-capacity work**: adopt a
UTC-anchored 15:00-19:00 UTC window, not a literal "hour 10-14" read against local-clock
timestamps. Virginia's longitude offset from the Eastern Time meridian is a minor correction
(~10 min for Richmond); Daylight Saving Time is the dominant effect (a full hour, in effect for
the higher-solar-output ~8 months of the year) — a flat local-clock window would miss true solar
noon by a full hour for most of the year. In local clock terms, this UTC window is 10am-2pm EST in
winter, 11am-3pm EDT during DST.

## 7. Presenting results (per the uploaded framework's Step 3)

- **Recommended build**: state exact MW/MWh figures directly — this audience does not need the
  decision-variable values translated into narrative first, but should get the specific build
  numbers, not just "solar and storage."
- **Cost outcome**: annualized total and the resulting $/MWh, with the single-year-vs.-20-year-SLCOE
  distinction (section 1) stated explicitly rather than assumed understood.
- **Binding constraints / shadow prices**: report directly — e.g., the gas-allowance cap's own
  shadow price as $/MWh of relaxation value, not translated into a lay metaphor for this audience.
