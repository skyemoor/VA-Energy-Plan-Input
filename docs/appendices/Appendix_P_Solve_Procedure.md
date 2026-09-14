# Appendix P — Solve Procedure and Requirements (WORKING DOCUMENT)

*This is a separate, editable working copy of Appendix P, pulled directly
from Reorganized_Appendices_Draft.md (lines 3582-4360 at time of
extraction). Created so Appendix P can be iterated on independently --
including open questions like the #-vs-section-symbol formatting
question raised earlier this session -- without editing the large,
heavily cross-referenced main appendix file directly, and without risk
of disturbing the many existing cross-references throughout that
4,000+-line document.*

**Status: this is the working copy, not the authoritative version.**
The main Reorganized_Appendices_Draft.md still holds the current,
official Appendix P. Changes made here need to be explicitly synced back
to the main file once finalized -- this file will not update
automatically. Treat divergence between this file and the main
document's own Appendix P as expected during active work, not an error.

**Open, unresolved question carried over from this session**: the main
document's own Appendix P still uses the section-symbol style ("§1"
through "§13") throughout its own headings below (structurally
load-bearing, with cross-references to it from elsewhere in the main
document). This working copy has NOT yet had that formatting changed —
pending a decision on whether to reformat Appendix P's own headings the
same way Scenario3_Scope_and_Gaps.md already was (to "#1" style), and if
so, whether that change should be made here first (low-risk, since this
copy isn't cross-referenced from elsewhere yet) before deciding whether
to carry it back to the main document (higher-risk, given the existing
cross-references there).

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
P.2 §1 and §5 below:

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
  interpolation of results from other years. The requirement in P.2 §1
  that dispatch and cost not be interpolated refers to exactly this
  distinction — capacity may be interpolated between checkpoints, but
  the dispatch and cost that result from that capacity must be
  separately, genuinely computed for every year.

**Scenario-solve** (or "the full solve"). The complete set of all 20
year-solves for a given scenario, together with every calculation built
on top of them: cost accounting that assigns each year's new capacity
to the price it was actually built at ("vintage-tracked" capital cost,
described further in P.2 §6), credit for the residual value of assets
still in service beyond the end of the 20-year study window ("terminal
value," P.2 §6), tiered social/environmental cost estimates, and the
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
  example, how solar output is adjusted for panel aging — see P.2 §2)
  requires re-solving *every* affected year, not a single one. Both of
  this project's most substantial corrections to date — extending
  Scenario 2 from four sample years to a genuine 20-year solve, and
  correcting how solar output was aged over time — fell into this
  second category, and both required a complete re-solve of every
  affected year (see Appendix C.12 and C.13).

### P.2 General Procedure — Requirements Applying to Every Scenario and Every Solve

#### §1. Time coverage

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

#### §2. Solar output degradation

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

#### §3. Reserve margin

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

#### §4. Gas generating fleet (any scenario using gas capacity, existing or newly built)

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

#### §5. Capacity sizing when a resource faces no cost penalty within the optimizer's own objective

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

#### §6. Terminal value

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

#### §7. Demand and weather-year basis

The same, current demand forecast should be used consistently across
every year-solve — this project's Virginia-only demand total, adjusted for
the flattening effect of data-center load growth described in Appendix
O — rather than an outdated or scenario-specific demand source. The
same, established historical weather year (a full year of actual
recorded solar, wind, and hydroelectric conditions from 2016-2017)
should likewise be used consistently, unless a different weather year is
being deliberately tested as its own, explicitly labeled stress-test
case.

#### §8. Export and curtailment treatment

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

#### §9. Tier 1/2/3 social and environmental cost

Every scenario-solve must calculate Tier 1 and Tier 2 social cost, and
must disclose Tier 3 findings even though Tier 3 is not converted to a
dollar figure. These three tiers are this project's standing framework
for the costs a scenario's gas generation imposes beyond its direct
financial price — costs real to the people and climate affected by that
generation, but not reflected in a fuel bill. Full methodology,
sourcing, and plant-specific detail live in Appendix D; this section
states only the requirement that every scenario-solve must satisfy.

- **Tier 1 (climate cost)**: carbon dioxide, methane, and nitrous oxide
  emissions from each year's actual gas dispatch, calculated using
  standard published emission factors and monetized using the U.S.
  Environmental Protection Agency's own social cost of greenhouse gases
  (SCoC) schedule (a dollar-per-ton figure that rises over time,
  reflecting the growing cost of cumulative climate damage). Tier 1
  must be reported as two separate figures, not one combined total —
  see the dedicated discussion below.
- **Tier 2 (regional health cost)**: fine particulate matter, sulfur
  dioxide, and nitrogen oxide emissions from the same gas dispatch,
  monetized using the EPA's own published benefit-per-ton figures for
  the electric generating sector. Nitrogen oxide emissions specifically
  must use the plant-specific pollution-control classification required
  by §4, not a single fleet-wide assumption.
- **Tier 3 (disclosed, not monetized)**: additional, harder-to-monetize
  effects — for example, elevated cancer risk from air toxics such as
  formaldehyde and benzene, and findings from the current public-health
  and regulatory literature on gas-fired generation sited near
  residential areas — must be identified and cited, even though this
  project does not convert them to a dollar figure. This is a
  disclosed, deliberate choice, not an omission: no sufficiently
  robust, defensible dollar-per-ton figure exists for these effects the
  way one exists for Tier 1 and Tier 2, so including an invented one
  would create false precision rather than genuine insight. Tier 3 is
  excluded from this project's dollar-denominated "total societal cost"
  figures by design, and that exclusion should be stated plainly
  wherever a total societal cost figure is presented, not left implicit.

**Tier 1 must be split into two separately-reported figures, not
combined into one, per Virginia law.** Virginia Code §56-598(2)(d) and
§56-585.1(A)(6) require the State Corporation Commission to separately
consider a Virginia-specific "social cost of carbon" — a distinct,
carbon-dioxide-only concept — when evaluating applications to construct
new generating facilities. This project refers to that specific,
statutory concept as **"Virginia SCC"**, to keep it clearly
disambiguated from **"SCoC"**, the generic economic term for the social
cost of carbon dioxide emissions used throughout this appendix and the
broader literature. Virginia SCC is required by statute to be reported
as its own figure, separate from this project's broader, multi-gas
**"aggregate GHG cost"** (carbon dioxide, methane, and nitrous oxide
combined — what this project has called "Tier 1" throughout its
history). The two are related but genuinely different in scope: Virginia
SCC is carbon-dioxide-only and tied to a specific statutory purpose;
aggregate GHG cost captures the full climate impact of gas generation
across all three greenhouse gases this project tracks.

The statute directs the Commission to determine Virginia SCC using the
best available science, citing the 2016 Interagency Working Group
technical support document as guidance — not this project's usual
2023-updated EPA source for SCoC. **As of this project's most recent
sourcing, the Commission has never actually set a Virginia-specific
rate**, despite the requirement dating to 2020; in practice, Virginia
utilities have used an assumed federal placeholder figure roughly a
quarter the size of the 2023 EPA estimate. Absent an actual Commission
determination, this project uses the EPA's 2023 SCoC schedule's own
carbon-dioxide-only rate as the best available proxy for Virginia SCC —
the same underlying rate used for the CO2 portion of aggregate GHG
cost, simply reported as its own line — with this choice of proxy
stated explicitly wherever Virginia SCC is presented, not left
implicit. Should the Commission ever set an actual Virginia-specific
rate, that rate should replace this proxy.

At the executive-summary and technical-summary level (as opposed to
this appendix's own, full detail), a brief footnote explaining this
proxy choice is sufficient — full statutory citation and reasoning
belong here, not repeated at every level of summary.

Both Tier 1 (in both its Virginia SCC and aggregate GHG forms) and Tier
2 are subject to the same full-window coverage requirement as §1: they
must be calculated across all 20 years of a scenario-solve, not from a
subset of checkpoint years. This project's own history shows why the
distinction matters even here, though the consequence was smaller than
it was for direct financial cost: an earlier version of Scenario 2's
Tier 1/2 figures, built from four checkpoints only, moved only modestly
once corrected to the full 20 years (Tier 1 by about $3.60/MWh, Tier 2
by less than $0.10/MWh) — because, unlike direct financial cost, Tier
1/2 has no terminal-value-style credit mechanism that a partial
calculation could be paired with to produce a large distortion. The
four-checkpoint figure happened to be a reasonable approximation for
Tier 1/2 specifically; it was not a reasonable approximation for direct
financial cost, and that difference should not be assumed to hold for
every future calculation of this kind. Genuine, full 20-year
calculation remains the standing requirement regardless — and this
requirement was found to still be unmet for Scenario 1's own Tier 1/2
figures at the same time the Virginia SCC split was introduced:
Scenario 1's Tier 1/2 had never actually been extended past its
original four checkpoints either, despite Scenario 1's own full
20-year dispatch data having existed the entire time. See P.4 for the
current status of both corrections.

#### §10. Land acreage

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
  degraded/effective capacity (§2), since land is committed based on
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

#### §11. Verification required before any solve is presented as final

- Zero demand goes unserved, unless an unserved-demand shortfall is
  itself the deliberate subject of the analysis.
- Existing plus newly built capacity sums exactly, not approximately, to
  whatever peak or baseload requirement that capacity is meant to cover
  — and once the §3 reserve-margin requirement is properly enforced,
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
  type — see §13.

#### §12. Documentation

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

#### §13. Storage dispatch degeneracy (simultaneous charge and discharge)

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
presented as final, per §11 below. This must be checked directly against
the solved hourly output (`charge[t] > 0 and discharge[t] > 0`
simultaneously, for any hour), not assumed from the presence of a
cycling-cost term alone — the cost term's effectiveness at a new
checkpoint's specific parameterization is an empirical question, not a
mathematical guarantee, per the SLCR trial's own finding (Internal
Debugging Log #20.7) that a mechanism's effectiveness can vary by
checkpoint depending on which constraints are actually binding there.

#### §14. Any alternative solve path must be built from the same code, not reconstructed

A scenario solved through a different route — a multi-period assembly, a sweep harness, a
diagnostic — must obtain its problem from the **same function that ordinarily solves it**, not by
calling the problem builder and reapplying the constraints itself.

**The constraints are not all in the builder.** The capacity cap, the VCEA short- and long-duration
storage floors, the minimum storage duration, the reserve margin and the SLCR row are all applied
*after* the build, by the solve function. A path that calls the builder directly gets a problem
missing every one of them, and the omission does not announce itself: the solve succeeds, and the
result is merely wrong.

**The observable symptom is unserved energy that the ordinary path does not produce.** Without the
minimum-duration floor the optimiser builds storage with power but almost no energy — capacity that
discharges for minutes and cannot cover an evening — and then accepts unserved demand at the
penalty price rather than build usable storage.

**A partial reconstruction is worse than an obvious one**, because the error shrinks rather than
disappears and reads as progress.

**Requirement:** solve functions expose a build-only mode returning the problem exactly as it would
be solved, placed immediately before the solve so it stays complete as constraints are added. A
verification compares the constraint-row count of that mode against a full solve; a single missing
row is a missing constraint.

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

- **Scenario 1 / 1B**: §2 (solar degradation happens automatically via
  vintage tracking); §8 (export-revenue parameter present but disabled
  by default; post-hoc export-revenue calculation included).
- **Scenario 2**: §2 (solar degradation must be separately calculated,
  since capacity follows an externally-set schedule rather than an
  optimizer decision); §8 (no export-revenue mechanism exists in the
  LP at all; no post-hoc export-revenue calculation applied, a
  deliberate decision given the small, single-checkpoint scale of its
  curtailment).
- **Scenario 3**: no bracketed notes yet — scenario not yet built. Once
  built, this index should be updated at the same time any new,
  scenario-specific bracketed notes are added to P.2, consistent with
  §12's requirement that new general requirements be added to this
  appendix as part of documenting the work that discovered them.

### P.4 Disclosed Gaps Against This Procedure, as of This Appendix's Creation

- **Reserve margin (§3) — value settled, mechanism tested, project-wide
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
- **Plant retirement-year cross-reference (§4)**: the retirement years
  used in this project's social-cost NOx classification have not yet
  been checked against the corrected plant roster used for gas capacity
  crediting elsewhere in the project. Believed likely immaterial (the
  classification of which plants have DLN pollution controls is
  unaffected either way), but not yet formally verified.
- **Scenario 1's own reserve-margin status**: covered by the general §3
  gap above. Scenario 1's checkpoint solves were established earlier in
  this project's history and have not yet been individually re-audited
  against this appendix.
- **Virginia SCC / aggregate GHG split, and Scenario 1's Tier 1/2
  20-year extension (§9)**: methodology decided and documented above,
  but the actual figures for Scenario 1, 1B, and 2 are intentionally
  not yet calculated or published anywhere in this project. Both
  corrections depend on each scenario's underlying dispatch, which is
  about to change once the §3 reserve-margin fix is implemented across
  all three scenarios — calculating these figures now would mean
  recalculating them again immediately after. Deliberately deferred
  until after the reserve-margin fix, so both are done once, on final
  dispatch data, rather than twice.
- **RGGI compliance cost is not included anywhere in this project's
  direct financial SLCOE, for any scenario.** Virginia rejoined the
  Regional Greenhouse Gas Initiative (RGGI) on July 1, 2026 — a
  market-priced, cap-and-trade compliance cost gas generators must
  actually pay, genuinely distinct from Virginia SCC and aggregate GHG
  cost (Tier 1), which are externality/social-cost estimates, not real,
  billed expenses. RGGI cost belongs in direct financial cost, not
  Tier 1. Not yet added to any scenario's gas dispatch cost calculation.
  Pricing methodology decided, not yet implemented: RGGI's own published
  Cost Containment Reserve trigger-price schedule is a known, sourced,
  year-by-year figure ($18.22/ton in 2026; a two-tier structure from
  2027, $19.50/$29.25, both rising 7%/year through 2037) — but the
  actual, current market-clearing price (roughly $35-40/ton as of this
  appendix's creation) already runs well above that trigger schedule,
  reflecting real scarcity from Virginia's re-entry and a newly
  tightened regional cap, not a hypothetical or unlikely outcome. A
  single flat price would understate this real volatility. This project
  should use a yearly price profile, not one flat figure, with at least
  two tiers to bound the genuine uncertainty: a low tier following
  RGGI's own published trigger-price schedule, and a high tier following
  the current, elevated market-clearing price — consistent with this
  project's existing practice of using multiple priced tiers for other
  uncertain inputs (the Deloitte/EIA/Hughes gas-price tiers). Like the
  items above, deliberately deferred until after the reserve-margin fix.
- **Land acreage (§10)**: newly added requirement, not yet calculated
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
