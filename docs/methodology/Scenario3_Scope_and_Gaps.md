# Scenario 3 — Full Scope and Reference/Citation Gaps

*Synthesized from: the user's own session-opening definition and subsequent
clarifications; Appendix E (DER Owner Economics); Appendix_Agrivoltaics.md;
Appendix P #10 and #13; Scenario3_Technical_Notes.md (this session's own
flat-panel CF and price-elasticity research); the prior-session notes
document (VPP/DER compensation, DLC-vs-price-signal literature); the white
paper section synthesis; new_peaker_ccgt_costs_by_size.md and
VA_gas_capacity_schedules.md; Virginia_Grid_Analysis_Workplan.docx; and the
newly-checked uploaded LMP files. Organized so each item states what's
already sourced/decided, and what specifically is still open — for the
open items, that means what to fill in, not just that something is
missing.*

## 0. SYNTHESIS — the selected/recommended set of S3 DER-compensation features (this session)

*This section exists because modeling was actually carried out against a specific, final set of
choices — not because every open question in this document has been resolved. It answers "what did
the work that's already been done actually assume," coalescing §§6-8 (this session's own research)
with the parallel session's own executed build, into one place. This addresses Scenario 3's own
part (a)/(b) specifically — how rooftop and parking-lot canopy owners get compensated for FERC
2222-enabled market participation. It does not cover part (c) (agrivoltaics) or part (d) (retail
day-ahead/real-time rate design), which remain separately scoped elsewhere in this document.*

### 0.1 The selected structure

**Option 3 (hybrid)**, resolved in §8.1 and never revisited: the existing base wholesale-equivalent
case stays unchanged; a new, clearly-labeled **"Recommended Program"** tier sits alongside it as one
consolidated, decision-ready combination; the individual sensitivities (LSRV alone, and a separate
revenue-volatility floor mechanism) are retained underneath as reference, not folded in. This is the
structure actual modeling was run against.

### 0.2 The selected component set, with final values — tracing each one to its last, corrected form

Several components were revised mid-stream in the parallel session (documented in §8.2); the table
below is the *final* version of each, not an intermediate one that was later corrected:

| Component | Final selected value | Where it's grounded here |
|---|---|---|
| Energy | Undiscounted wholesale-equivalent rate — $63.00/MWh ($45 EIA average LMP × 1.40 DOM-zone premium, no midday-surplus discount) | §8.2 — a midday-surplus discount describes raw unmanaged export, not a well-timed storage-backed owner's own dispatch; corrected from an earlier, discounted version. **1.40 factor sourced 2026-09-02, from `Notes_from_Previous_session.docx`**: Dominion's real, structural ~40% premium over the RTO average — a year-round relationship, deliberately chosen over a rejected seasonal-spike figure (a winter-only $128.35/MWh IMM number) for exactly that reason. **Not double-counted with the Locational (LSRV) row below** — direct user question, checked against source: the parallel session explicitly confirmed LSRV was built as a separate sensitivity, never merged into this base energy rate ("present only in the sensitivity... not in the base case at all"), and stated directly that the locational adder is "a genuine additional stream on top of wholesale compensation," addressing a different gap (wholesale-vs-retail compensation level) than what the premium itself addresses (Dominion-zone vs. RTO-average pricing) |
| Capacity — storage | PJM-ELCC-derated, same schedule as the base case (not undiminished) | §8.2 — reliability sizing must reflect real, PJM-measured availability regardless of tariff design; corrected from an earlier "undiminished" version that conflated energy value with capacity accreditation |
| Capacity — solar | PJM's declining ELCC schedule, unchanged from the base case | Same principle, solar side — never revised |
| Locational | LSRV-style adder — real NY-sourced rate (§7.4), 90% qualifying urban/suburban share, 10-year term, referenced directly rather than duplicated | §7.4 — NY's own LSRV design maps closely onto this project's own 90%-urban/suburban siting assumption. **Caveat, not a double-counting issue**: this rate is NY's own imported figure, not a Virginia-specific avoided-cost study identifying a real constrained Dominion substation (§7.2, §12 item 9) — defensible in mechanism, not yet proven for Virginia specifically |
| Environmental | Virginia's own real, current D-REC spot price — $22.25/MWh | §7.3 — no Code change needed, real and tradable today; NY's E-Value and the $65-70 upside projection were both considered and set aside in favor of this |
| Event-based | NY DRV-style, converted to a real annual-equivalent rate using actual local hourly load data — $50.59/kW-yr | §7.4 — chosen over MA's ConnectedSolutions ($250/kW-yr, rejected for a twice-replicated 50/50 winter/summer seasonal mismatch) and over Dominion's own PTR (rejected for an automated-battery-vs-manual-program mechanism mismatch, §8.5); DRV and PTR's near-identical computed rates were treated as a cross-validation signal, not a coincidence |
| Transmission-avoidance | A new incentive, 25% of the utility's own avoided transmission-interconnection cost, explicitly built as a transfer (not new value) — 75% retained as ratepayer savings, shown explicitly on the ratepayer-side accounting | §8.4 — justified by an affordability priority; the split itself is a policy choice, not a derived number |

### 0.3 The result actually produced, and what's not yet included in it

Running the base case plus this full component set: **rooftop NPV +$1,053/kW, parking-lot NPV
+$355/kW** — both positive, a real reversal from the base wholesale-equivalent case (which was
negative for both segments). Parking-lot's own result is the more sensitive of the two, given its
higher capex and higher discount rate relative to rooftop.

**Explicitly not included in this figure**: the revenue-volatility floor mechanism (§8.8, Section K
in the parallel session's own model) is a real, tested, structurally-verified addition — but it was
built and left with a **placeholder value factor of 1.0**, meaning it currently contributes nothing
beyond the base case. A real value factor (bounded between 1.0 and roughly 2.0-2.9x per §8.8's own
Loudoun-data analysis, net of forecast-error and cannibalization discounts neither session has yet
applied) was never assigned. If adopted, this would sit as an *additional*, separate layer on top of
the $1,053/$355 figures above, not already folded into them.

### 0.4 Provenance and status — what this is, and isn't, ready for

**This entire selected set was computed using the parallel session's own annual-model capex,
discount-rate, and demand assumptions** — not re-derived against this project's own current hourly-LP
parameters, checkpoint structure, or SLCOE conventions. The mechanism, the reasoning behind each
choice, and the component values themselves (real market rates: DRV, D-REC, LSRV) are directly
reusable. The $1,053/$355 NPV figures specifically are not — they were produced by a structurally
different model (annual, formula-chain-based) than this project's own (hourly LP), and would need to
be recomputed against this project's own methodology before being cited as this project's own result.

**Adopted, direct user instruction, 2026-09-02**: Option 3's structure (§8.1) and the full "Recommended
Program" component list (§8.3, including the 25/75 avoided-transmission-cost transfer split as part of
that adopted set) are now this project's own Scenario 3 DER-compensation design — resolving decision
(1) below. This is a structural/mechanism adoption, not a numerical one: the component list, the rate
sourcing, and the reasoning behind each choice are now settled for this project's own Scenario 3. The
$1,053/$355 NPV figures themselves remain not directly usable, per the paragraph above — decision (4)
below (re-running the adopted structure against this project's own hourly-LP methodology) is the
concrete next step needed before this project has its own real NPV result under this design.

**What still needs to happen**: ~~(1) an explicit decision to adopt Option 3's structure for this
project's own Scenario 3, rather than a different structural choice~~ **(resolved above)**; ~~(2) the
25/75 transmission-avoidance split re-decided (or explicitly re-affirmed) as this project's own policy
choice, not inherited automatically~~ **(resolved above, adopted as part of the §8.3 set)**; (3) a real
value factor decided for the floor mechanism, or the mechanism set aside — **still open**, and
explicitly not part of what was just adopted (§0.3: the floor mechanism sits as an additional,
separate layer on top of the Recommended Program figures, not folded into them); (4) the whole stack
re-run against this project's own capex/discount-rate/demand conventions to get a genuinely
this-project NPV figure, rather than citing the parallel session's own $1,053/$355 — **now the
critical-path item**, unblocked by the structural decision above but not yet done.

## 0a. Software architecture — shared base class hierarchy, 2026-08-26, direct user instruction

Direct user request: common, subclassable base classes for each subject (EE, DLC, WMA, etc.),
proactively eliminating the kind of ambiguity found in entry #109's own review (two independently-
built modules, `large_ci_curtailment_analysis` and `dlc_analysis`, answered the identical avoided-
cost-comparison question with two inconsistent output shapes — a genuine Rule 1 violation that had
gone unnoticed until directly checked).

**Built and tested**: `shared_base_classes/demand_side_feature.py` (+ 15 tests, all passing) — the
first shared package structure anywhere in this project (confirmed directly that none previously
existed: no `__init__.py`, no cross-module imports in `lp_package/`). Hierarchy: an abstract
`DemandSideFeature` root (two required methods: `magnitude_per_unit()`, `current_compensation_usd()`)
with four abstract subject-level subclasses — `EEMeasure`, `DLCProgram`, `WMAPathway`,
`PriceBasedDR`. `DLCProgram` adds one shared, concrete `avoided_cost_comparison()` method, used
identically by every DLC-style program rather than reimplemented per program.

**The core design principle, direct user instruction, proven via a dedicated test class
(`TestNoneVsNotImplementedErrorDistinction`)**: two deliberately different "missing value"
mechanisms, not to be confused —
- `current_compensation_usd()` returns `None` when the concept genuinely applies but the actual
  rate isn't yet publicly known (a real, disclosed sourcing gap — e.g. A.7 data center flexibility's
  own event frequency, Citizen EV V2G's own unpublished BYOD rate).
- `current_compensation_usd()` raises `NotImplementedError` when the concept does not apply to that
  feature at all, structurally, regardless of sourcing (e.g. A.5 CVR — no customer-facing
  compensation mechanism exists to even ask about).

Enforced by Python's own `abc` machinery, not just convention — a subclass missing either required
method cannot be instantiated at all, confirmed directly via test, not assumed.

**Migration completed, 2026-08-26**: all three existing, already-tested modules now have thin
adapter subclasses (`large_ci_curtailment_feature.py` → `LargeCICurtailment`,
`school_bus_v2g_feature.py` → `SchoolBusV2G`, `ev_charger_rewards_feature.py` →
`EVChargerRewards`), each in the same directory as, and reading live from, its own untouched
underlying assumptions module — no existing constant or function was modified or restated as a
duplicate. Every migration verified against the already-established finding it corresponds to, not
just checked for interface compliance:

- **LargeCICurtailment**: the original entry #82 finding (40.7%/70.9% of avoided cost) never
  applied a margin concept — reproduced exactly through the shared method only by passing
  `utility_margin_pct=0` explicitly. A dedicated test also confirms the shared method's own
  *default* (5%) margin produces a genuinely different number — proving the exact-match isn't a
  coincidence.
- **EVChargerRewards**: the opposite case — this module's own existing methodology already matches
  the shared method's own default margin (both built in the same session, entry #109), so no
  override was needed; reproduced exactly with the shared method's plain defaults.
- **SchoolBusV2G**: surfaced a genuine third gap in the base class's original two-case design
  (`None`/`NotImplementedError`) — this program's real compensation is known and applicable, but
  not monetary at all (in-kind battery replenishment). Neither existing case honestly fit. Resolved
  by adding `compensation_is_monetary()` / `compensation_description()` to the root
  `DemandSideFeature` class itself (concrete methods, defaulting to preserve every
  already-built subclass unmodified), rather than forcing a misleading fit — proactively closing
  exactly the kind of ambiguity this whole hierarchy was built to prevent, found by actually doing
  the migration rather than anticipated in the original design.

**205/205 tests pass project-wide** (50 new across the three adapters, the base-class extension,
and their own tests; 155 prior, all unchanged and still passing).

**Utility margin consolidated into a single true global, 2026-08-27, direct user request**: entry
#112's own margin change (5% -> 0%) had required manually updating TWO independently-defined copies
together (this file's own default parameter value, and `dlc_analysis/dlc_assumptions.py`'s own
separate module constant) -- a fragile pattern the user asked to eliminate outright, not just keep
carefully synchronized. `DEFAULT_UTILITY_MARGIN_PCT` now lives in exactly one place
(`shared_base_classes/demand_side_feature.py`); `dlc_assumptions.py` imports it directly rather than
defining its own copy, and `large_ci_curtailment_feature.py`'s own explicit `utility_margin_pct=0`
override (kept in entry #112 "for self-documentation") was removed rather than retained, since
keeping it would itself be exactly one more place the value was hardcoded. A correctness detail
worth noting: the shared method's own default uses a `None`-sentinel pattern rather than embedding
the global directly as the parameter's default value, since Python binds default arguments at
function-definition (import) time -- the sentinel pattern resolves the global fresh on every call,
which is the correct behavior for a genuinely live, single-source value. A real editing mishap
occurred and was caught before finalizing: an initial `str_replace` left a stray, unterminated
docstring fragment mid-method, breaking the file's own syntax -- caught immediately by running
`py_compile` directly (not assumed clean), and fixed with a complete, single-pass rewrite of the
affected method rather than a further incremental patch. **232/232 tests pass project-wide**
(2 new + 230 prior, all unchanged) after the consolidation.

## 1. Core definition (as confirmed across this session)

Scenario 3 = Scenario 1's full build-out and compliance target, modified
per four categories (framework developed and refined this session, full
detail in #5 below):

**Category B — Location Allocation** (confirmed, complete)
• B.1 — 10% of solar sited on urban/suburban rooftops, paired with
  firmed storage
• B.2 — 10% of solar sited on urban/suburban parking-lot canopies, same
  firmed-storage treatment as B.1
• B.3 — the remaining 80%, sited outside urban/suburban areas, split
  across ownership tiers per Dominion's own Rider CE (Company-owned) /
  Rider PPA (third-party physical PPA) / Rider RPS (unbundled RECs)

**Category C — Land Use** (confirmed, complete)
• C.1 — 90% of B.3's non-urban share in agrivoltaic arrangements,
  benefiting Virginia farmers via land lease income

**Category D — Market Participation** (confirmed in principle; D.3 open)
• D.1 — FERC 2222 wholesale-market access, direct at ≥100 kW / indirect
  via DER Aggregator (DERA) below that — applies to B.1/B.2's DER-owned
  tiers only; B.3's Rider CE/PPA tiers have no independent wholesale
  position (#5.2)
• D.2 — Supply-side price response: owners/DERAs dispatching storage or
  generation against wholesale price signals, for the same B.1/B.2 tiers
• D.3 — Compensation structure — **open, "we'll discuss"**

**Category A — Demand-Side Management** (explicitly incomplete)
• A.1 — Price-based DR: retail (residential and C&I) day-ahead/real-time
  rates, ComEd-style, producing genuine price-responsive load shifting —
  confirmed directly, not a peak-proportional DSM allocation
• A.2 — Incentive-based DR — **confirmed in scope, mechanism and
  magnitude not yet specified**, deferred to a later discussion
• A.3 — Energy efficiency: heat pump efficiency and PHIUS building
  standards — confirmed in scope; magnitude not yet quantified (#4)

**Scenario 3B** = Scenario 3 + 5% gas allowance at 2045 and beyond,
structurally parallel to Scenario 1B.

This is **not yet built** — no LP solve exists for Scenario 3 anywhere in
this project's current working environment (confirmed multiple times this
session). Everything below is preparatory scope, not completed work.
Category A is deliberately presented as incomplete here rather than
smoothed over — two of its three elements (A.2, and A.3's own
quantification) remain open, while B and C are complete and D is open
only on its compensation piece (D.3).

## 2. Physical build — solar and storage siting

| Aspect | Status |
|---|---|
| 80% utility-scale share | **Sourced.** Reuses this project's existing solar_cf data (the same Albemarle/Chesapeake/King George blend used throughout Scenario 1/1B/2). |
| 10%/10% rooftop and canopy capacity factor | **Proposed, pending your review.** ~0.81 ratio vs. utility-scale, sourced directly from NREL's 2024 ATB (Commercial PV vs. Utility-Scale PV benchmarks). Full derivation in Scenario3_Technical_Notes.md #1. |
| Rooftop vs. canopy — same CF, or distinct? | **Open, not yet decided.** The 0.81 proposal applies one ratio to both; a canopy structure has more layout freedom than an existing building roof shape, so they may warrant separate treatment. Not yet researched separately. |
| South-facing-shallow-tilt vs. east-west-density-optimized layout | **Open.** Materially changes where in the sourced range (a few percent penalty vs. 10-15%) the true figure sits. Not resolved — 0.81 is a single point estimate spanning both. |
| Agrivoltaic capacity factor | **Sourced, confirmed by you directly**: energy-equivalent to standard ground-mount. No new CF sourcing needed — only land-use and lease-income treatment differ. |
| "Firmed storage" — how distributed storage is sized/dispatched | **Open, structurally unresolved — this is a real gap, not a citation gap.** Scenario 1's own principle is "no standalone storage," and Scenario 3's own definition pairs each distributed segment with its own firmed storage — but *how* that storage is sized and dispatched hasn't been decided: is it part of the same central LP optimization (the solver decides how much Na-power/iron-air to co-locate with the distributed solar), or sized/dispatched independently, given it would actually be owned by DER owners/aggregators rather than centrally dispatched by the utility? This affects the LP formulation directly, not just an input assumption. |
| Distribution-system upgrade cost for hosting high DER penetration (reverse-flow capacity) | **Sourced this session — a real, general benchmark, not Dominion-specific engineering.** See §2.1 (unit cost, $/kW) and §2.2 (how many circuits are actually affected). This project's own hourly LP and Appendix A had zero treatment of this cost anywhere before this session; the existing $200/kW LBNL-sourced figure (§8.4) is transmission-interconnection cost for utility-scale solar specifically, a genuinely different cost from this one. |

### 2.1 Distribution-system upgrade cost for high DER penetration — a real, general benchmark, not yet in this project's own model

**The underlying concern, confirmed as real and directly relevant to Scenario 3**: a conventional
distribution circuit is designed for one-directional power flow sized to its own peak *load*, not
reverse flow from behind-the-meter generation. Once aggregate rooftop/canopy solar output on a given
circuit exceeds that circuit's own "hosting capacity" — the formal industry term (per NREL's own
published methodology, and the analysis software category covered in the uploaded document's own
Appendix E: OpenDSS, EPRI DRIVE, Eaton CYME, ETAP DERMS, DIgSILENT PowerFactory) — physical upgrades
become necessary: transformer replacement (bi-directional-rated units), voltage-regulation equipment
(load tap changers, capacitor banks), and protective relaying capable of detecting reverse power
flow and isolating a fault regardless of which direction it's fed from (the uploaded document's own
Appendix D correctly lists these as the standard mechanisms, though it provides no cost figures for
any of them — checked directly against the source document, not assumed).

**No Dominion-specific circuit-level engineering data exists for this project to draw on** — consistent
with how every other general-industry-benchmark cost in this project (CCGT capex, transmission
interconnection, solar O&M) has been sourced, this uses published, real-feeder-study benchmarks
rather than a specific configuration this project has no basis to assert.

**Sourced benchmarks, real feeder/circuit studies, not vendor estimates**:

| Source | Basis | Implied $/kW of hosted DER (or driving load) |
|---|---|---|
| NREL/E3 (GridLab, 2021), "marginal cost low case" | The report's own stated closest match to standard current utility practice for calculating distribution costs driven by new load/generation | ~$420/kW ($400/kW primary distribution + $20/kW secondary, 2020$) |
| Li & Jenn (PNAS, 2024), real California feeder-level study | 67% of California feeders projected to need capacity upgrades by 2045; 25 GW of upgrades, $6-20B total cost | $240-800/kW |
| GridLab/E3's own cited marginal-cost-of-service (MCOS) utility filings (Otter Tail Power, Eversource, SDG&E, PG&E) | Annualized revenue-requirement figures ($14-175/kW-yr), converted to an implied upfront-capital equivalent using this project's own 4.5% WACC and a 40-year distribution-asset life (a rough proxy CRF, not these utilities' own actual amortization terms) | ~$260-3,220/kW (an intentionally wide range — MCOS studies vary enormously by location-specific growth pressure) |
| GridLab/E3's own direct statement | California utilities specifically run "on the high end, above $1,300/kW" | >$1,300/kW (California-specific, not a national figure) |

**Proposed general-benchmark figure for this project's own use, pending your review**: **$500/kW**
of hosted distributed-solar nameplate capacity — a round figure sitting between the NREL/GridLab
"standard low case" ($420/kW) and the middle of the PNAS California range ($240-800/kW, midpoint
$520/kW), deliberately below the California-specific high-end figures (>$1,300/kW), since Virginia's
own distribution system, while facing real Northern Virginia-specific congestion (already documented
extensively in §7.4/§8.7), is not assumed to face California's specific combination of wildfire-driven
undergrounding costs and mature, already-saturated urban circuits that plausibly drive that state's
own figures higher. **This is a disclosed, reasoned mid-range estimate, not a precise or
Dominion-verified number** — the range above (roughly $240-1,300+/kW depending on source and
location) should be carried forward explicitly as the real uncertainty band, not collapsed into false
precision.

**How this would apply to Scenario 3's own build, mechanically**: unlike the transmission-interconnection
cost (§8.4, applied to the full utility-scale 80% share), this cost applies specifically to the
rooftop+canopy (10%+10%) distributed share, and specifically to the portion Scenario 3 already
assumes is sited in urban/high-demand areas (the same 90% qualifying share already used for the LSRV
locational adder, §7.4) — since that is precisely where distribution circuits are most likely to
already be running close to their own existing hosting capacity, making new DER additions more likely
to trigger upgrades than DER sited on lightly-loaded rural circuits. **Not yet decided**: whether this
should be built as a utility-side cost (added to Scenario 3's own system SLCOE, parallel to how the
transmission-avoidance mechanism already works) or as an interconnection-fee cost potentially borne
in part by individual DER owners (consistent with how the earlier "Grid Interconnection Rules"
finding, a real $2.3M-for-1MW-of-headroom hypothetical illustrating how nonlinear and location-specific
these costs can actually be, described how utilities currently allocate this cost in practice) — a
real, open policy-allocation choice this project hasn't made yet, not a sourcing gap.

**A related, structurally important finding worth flagging directly**: the AAF/EIA-based national
estimate found in this same search ($3.5M/TWh, aggregating to $395B nationally by 2035) uses a
fundamentally different methodology (a flat rate per TWh of distributed generation, not tied to any
actual circuit-level hosting-capacity constraint) and should not be used as a cross-check against the
figures above — it is answering a different, cruder question. The IEEE Spectrum "Full Cost of
Electricity" study cited in this same search reached the opposite qualitative conclusion for a
meaningful share of circuits — that "significant PV generation can be integrated in the grid with
little or no additional cost" up to a real, circuit-specific threshold, before any upgrade is
triggered at all. **Worth stating plainly**: this cost is not owed on every kW of distributed solar
Scenario 3 builds — only on the portion that pushes a given circuit's own DER penetration past its
existing hosting capacity, which this project has no way to determine circuit-by-circuit without
real Dominion hosting-capacity-map data (per the DOE's own "U.S. Atlas of Electric Distribution
System Hosting Capacity Maps" — as of the source checked, Virginia did not appear among the 26
states with at least one utility publishing such a map). **This claim is corrected in §2.2 below**:
a direct follow-up search found Dominion does in fact operate a real, public, interactive hosting-
capacity tool — the DOE Atlas source apparently predates it, or Dominion's own tool wasn't captured
in that particular DOE compilation. Applying the $500/kW figure to Scenario 3's *entire*
distributed-solar build, rather than some estimated penetration-adjusted share of it, remains a
conservative (upper-bound) simplification for now, refined by the circuit-count estimate below.

### 2.2 Estimating how many distribution circuits actually need upgrading — a genuinely separate question from the per-kW cost

**The question this section answers, and why it's distinct from §2.1**: §2.1 established a $/kW cost
for upgrading a circuit that has hit its own hosting-capacity limit — but applying that rate to
Scenario 3's *entire* distributed-solar build assumes every circuit hosting distributed solar needs
an upgrade, which isn't physically true. This section estimates what share of Dominion's own
distribution system that upgrade need actually applies to — narrowing §2.1's own disclosed
upper-bound simplification, not replacing it.

**A correction to §2.1, found directly in this session's own follow-up research**: Dominion does in
fact operate a real, public "Hosting Capacity Tool" — an interactive map covering its full Virginia
and North Carolina service territory, color-coded by available hosting capacity down to individual
line sections and, on a separate residential map, individual transformers. This is a genuine,
existing Dominion resource this project could draw on for far more precise, circuit-specific data
than the general estimate below — but it requires manual, location-by-location lookup, not a bulk,
downloadable dataset this project can process programmatically. The estimate below is offered as a
general, defensible approximation in lieu of that manual survey, not because Dominion's own real
data doesn't exist.

**A real, sourced, Dominion-specific screening threshold, found directly**: Dominion's own hosting-
capacity screening uses a simplified threshold of roughly 15% of a circuit segment's own peak load
— DER additions below that level are fast-tracked; above it, a full impact study (and potential
upgrade) is triggered. This is consistent with standard IEEE 1547-family interconnection screening
practice generally, not unique to Dominion, and the specific 15% figure was sourced from a
third-party solar-industry website rather than an official Dominion or SCC filing — flagged here as
a real but not fully independently verified figure, worth confirming against Dominion's own DER
Interconnection Parameters Manual (a real, official document also found this session, which confirms
Dominion's general interconnection practices but doesn't state this specific percentage in what was
reviewed) before treating it as authoritative.

**Building a general, transparent estimate, step by step**:

1. **Total Dominion distribution circuits**: Dominion's own SEC 10-K filings report approximately
   470 substations (468-473 across 2020-2021 filings — the most recent year this project found a
   direct substation count for; more recent filings describe distribution-line mileage, now ~60,600
   miles as of the 2024 10-K, without restating the substation count) and, separately, "more than
   800 substations" for its transmission system specifically — a different, larger network not to
   be confused with this one. Using a general industry range of 4-8 distribution feeders per
   substation (not Dominion-specific, disclosed as such) yields an estimated **1,880-3,760 total
   Dominion distribution circuits**.
2. **Urban/suburban share**: applying this project's own already-established 90% qualifying-share
   assumption (the same figure used for LSRV siting eligibility, §7.4) as a rough proxy — not a
   precise geographic mapping — yields **~1,690-3,380 urban/suburban circuits**.
3. **Data-center-dedicated exclusion, directly motivated by your own observation**: 371 operating
   Virginia data centers as of August 2026 (a real, current, sourced count), combined with the
   directly-confirmed pattern that Dominion adds "a new substation for every new data center" —
   meaning a substantial share of these are served by dedicated infrastructure structurally separate
   from any circuit that might also host rooftop/canopy solar, exactly the mechanism you identified
   (a data center's own power draw vastly exceeds what its own rooftop/parking footprint could ever
   backfeed, so a data-center-dedicated circuit is never a plausible candidate for a reverse-flow
   hosting-capacity problem). Using a 50-90% dedicated-infrastructure share (a real range, not a
   single sourced figure — smaller/older facilities are more likely to share existing circuits,
   larger/newer ones per the "new substation per data center" pattern are more likely fully
   dedicated) excludes an estimated **190-330 circuits**, leaving **~1,360-3,200 remaining
   urban/suburban, non-data-center circuits**.
4. **Applying the PNAS California feeder study's own real, sourced 67%-of-feeders-need-upgrades
   finding** (§2.1's own source, reused here for its second, genuinely relevant number — not just
   its $/kW figure) as a proxy for what share of these remaining circuits would actually be pushed
   past hosting capacity at Scenario 3's own DER penetration level: **~910-2,140 Dominion circuits**,
   midpoint **~1,530** — roughly **half of Dominion's own total estimated distribution circuits**
   (54% of the 1,880-3,760 total range).

**An illustrative, combined total-cost figure**, purely to show how §2.1 and this section's own
estimate compose (not a recommended final number): assuming each affected circuit hosts roughly
2-5 MW of distributed solar (a disclosed placeholder, not independently sourced to a specific study)
and applying §2.1's own $500/kW figure yields a total distribution-upgrade cost of roughly
**$0.9-5.4 billion** — a genuinely wide range, honestly reflecting that four separate, each
individually-uncertain ranges (feeders-per-substation, data-center-dedicated share, the PNAS
proxy-applicability assumption, and MW-hosted-per-circuit) compound together rather than converging.
**This should be read as establishing the right order of magnitude and the honest width of the
uncertainty band, not as a number to cite as a specific cost figure** — narrowing it meaningfully
would require exactly the kind of real, circuit-by-circuit Dominion hosting-capacity-tool lookup
flagged above as a genuine, existing but manually-intensive resource.

## 3. Ownership and DER economics

| Aspect | Status |
|---|---|
| 80/10/10 ownership split | **Sourced**, Appendix E. |
| ≥100 kW direct FERC 2222 threshold | **Sourced, confirmed by you directly.** |
| FERC 2222 implementation timeline/status in PJM specifically | **Possibly stale — worth a freshness check.** Appendix E's own sourcing may predate this project's "present day" (August 2026); FERC 2222 implementation has been actively evolving. Not re-verified this session. |
| DER compensation structure | **Explicitly deferred by you** ("we'll discuss"). Appendix E has a partially-built "Recommended VA Program" proposal (LSRV-style locational adder + Virginia's real D-REC price + NY DRV-style event compensation) from the prior session, with real, carried-forward reasoning about what's market-defensible vs. subsidy-like — but this predates this session's tightened citation/disclosure standards and hasn't been re-validated against them. |
| Locational value credit grounded in Dominion-specific avoided-transmission data | **Not started.** Currently (per the prior-session material) benchmarked against an out-of-state figure — flagged in Virginia_Grid_Analysis_Workplan.docx as a known gap, not yet addressed. |
| Additional ownership-split scenarios (testing owner economics at a higher distributed-generation share than 80/10/10) | **Not started** — listed as a Phase 3 item in the same workplan document, not yet scoped in this session. |
| Farmland lease income to VA landowners (agrivoltaics) | **Claimed "research complete" in an uploaded prior-session document — NOT independently verified in this session's own environment.** Treat this claim with the same caution this session has applied to other "already done" claims from that document set (see the Appendix N history) — the underlying research, if it exists, hasn't been located or re-confirmed here. **A related but distinct agrivoltaic-economics question was researched and well-sourced in a parallel session, worth noting separately rather than conflating**: real, current, quantified data on solar-grazing as a vegetation-management practice — not farmland lease income itself, but a separate cost-offset mechanism. The American Solar Grazing Association's own 2024 Census counted ~113,050 sheep grazing ~129,000 acres across 500+ US solar sites (an estimated 18-26 GW of capacity) — an established, mainstream practice, not a fringe one. Quantified savings from two independent sources: an OSU Extension worked example (Aug 2025) found grazing cutting mowing passes from 4/year to 2/year, a 50% reduction; Tampa Electric (a named utility) reported 75% cost savings over traditional mowing. Important clarification on the actual mechanism: this offsets the solar owner's vegetation-management fee paid to a grazier (which replaces a mowing contractor), not the underlying land-lease payment itself — the two are separate cost/revenue lines, not the same thing. Given Virginia's humid climate plausibly doubles vegetation-management cost relative to a national average (a separate, disclosed finding from that same parallel session, not independently re-verified here), grazing adoption could plausibly fully offset that climate penalty rather than only partially reduce it — a real, quantified, genuinely useful data point for this project's own agrivoltaic cost modeling, independent of whether the separate farmland-lease-income claim above ever gets verified. |

## 4. Demand side — DSM and price response

| Aspect | Status |
|---|---|
| Genuine price-responsive load shifting mechanism | **Proposed methodology, pending your review** (linearized, ex-ante price-response adjustment — needed to preserve LP linearity, avoiding an endogenous price-demand circularity the solver can't handle directly). Not yet built or tested. |
| **Synchronized-response ("rebound peak") risk in the price-response mechanism** | **New finding, 2026-09-02, direct user research request** — a real, distinct risk from elasticity magnitude, worth tracking separately: if many households' own HEMS all optimize toward the identical published day-ahead price signal, their loads can synchronize and create a *new* peak rather than flattening demand. Directly confirmed as a genuine, named gap in the field by a comprehensive peer-reviewed review (Assolami, *Residential energy management systems: a comprehensive review and case study*, Eng. Sci. Technol. Int. J. 78 (2026) 102355, uploaded to Project KB): "[DR studies]... often neglect rebound peaks, user fatigue, or the impact of communication constraints... there is still limited evidence on how household-level DR strategies interact when deployed at scale on real distribution feeders." Checked the same paper's own "Guidance for Future Research" section directly — it does not propose a specific fix for this, only a general call for real-time control algorithms responsive to "dynamic market signals, load variations, and user behavior" (device-side framing, not the utility/market-side price-setting question this row is about). **Proposed solution (direct user instruction)**: an AI/forecasting layer that continually models aggregate consumer HEMS behavior and adjusts the day-ahead price ex-ante to dampen synchronized over-response — explicitly **not** meant as an in-solve, iterative/endogenous mechanism (direct user instruction, 2026-09-02: "I do not mean to complicate our LP model further with another endogenous factor"). This would run as a separate pre-processing stage producing one, single, already-dampened price signal before the LP runs — preserving the linearized, ex-ante design already adopted for the row above, not a second circularity. **Real-world precedent flagged by direct user, verified 2026-09-02 against the now-uploaded `Virginia_Energy_Plan_Input.docx`**: the "wild swings" premise is confirmed directly from the source — "Because NYISO's energy component is tied to hourly wholesale gas and electricity markets, developer revenues fluctuated wildly during global energy price spikes and dips." **Correction to the user's own recollection, worth being precise about**: the document does not describe NYISO itself implementing a floor-and-cap system. It presents a *Virginia-specific recommendation* inspired by observing NY's problem, not a historical account of NY's own fix: "Offer an optional hybrid tariff or floor price for the energy component during an initial 3-to-5-year transition period, preventing market shock for nascent VPP developers while moving toward full market exposure." Only a floor is proposed (no cap), and it is explicitly scoped to a temporary transition period, not a permanent mechanism. **Independent of the attribution question, this is a genuinely good fit for the user's own ex-ante constraint above**: a floor price is a simple, fixed (or time-varying but still ex-ante) lower bound on the price input, not an iterative feedback loop — a real candidate to pair with or substitute for the AI-dampening idea, worth deciding on directly. **Resolved, direct user instruction, 2026-09-02**: the user is not concerned about this risk, on the basis that the price-setting algorithm eventually deployed would adjust for it, and that this is well covered in the literature — confirmed directly. The specific paper named (Han, Y., ..., Huang, J., *Mitigating synchronous load rebound and demand response uncertainty in community integrated energy systems: A consumer psychology-aware differentiated pricing approach*, Sustainable Energy, Grids and Networks, Vol. 47 (2026), Article 102354) is real and directly on point — its own abstract: "a bi-level differentiated pricing mechanism based on virtual resource pools is constructed. This approach manages user heterogeneity to mitigate synchronized peaks while balancing management costs." ScienceDirect blocked direct access to the full text (abstract only, ScienceDirect's own robots.txt disallows automated fetches); the PII found via title search (`S2352467725004618`) differs slightly from the one the user originally supplied (`S2352467726002365`) — title match is exact, so treated as the same paper, likely a transcription difference. **Net status: this row is no longer an open concern for this project** — the mechanism-design question of *how* to prevent synchronized rebound is delegated to whatever price-setting algorithm is eventually deployed, with real, on-point literature (this paper, plus the broader body found 2026-09-02: Tariff Menus to Avoid Rebound Peaks (Swiss DCE study), the 2015 foundational rebound-peak paper, and the inclined-block-tariff/RTP hybrid approach) confirming viable mechanisms exist. The AI-dampening and floor-price ideas above remain as one project's own possible design options, not as solutions to an unsolved problem. |
| Elasticity value | **Genuinely open, three options presented, not one recommendation** — near-zero (Spain-anchored), modest (EIA/NEMS-anchored, imperfect fit per the intra-day-vs-sustained distinction), or split by customer class. Automation follow-up (this session) gives a real, mechanistic reason to expect the achievable response is higher than the Spain finding alone would suggest, but doesn't pin down a number of the same evidentiary rigor. Full detail in Scenario3_Technical_Notes.md #2. **Cross-utility DA/RT and TOU evidence added 2026-09-02, direct user request — genuinely mixed, not a resolution**: ComEd is rolling out a *new, separate* fixed-four-period Delivery Time-of-Day program in 2026 (distinct from its existing ~1% enrollment Hourly Pricing program already cited above), whose 4-year pilot found 6.5-9.7% peak reduction each summer — real but a different mechanism than continuous hourly pricing. Hawaii's real, recent "Shift and Save" pilot (~16,000 randomly-selected customers, 1:2:3 price ratio, closed to new enrollment Feb. 2025) found **no statistically significant usage change** in its first six months of real data — a genuine, recent disconfirmation of the automation-improves-response premise, not just an old Spain-era finding. PEPCO's older (2008-2010) PowerCentsDC pilot found up to 50% summer peak reduction, strongest specifically when combined with automated smart-thermostat AC control — real empirical support for the automation premise, but 15+ years old and event-based (CPP/CPR), not continuous hourly. A well-established meta-analysis (Faruqui & Sergici) found 3-6% peak reduction for TOU broadly and 13-20% for Critical Peak Pricing across many pilots, with a related finding (Faruqui, Hledik & Palmer 2012) that the on-to-off-peak price *ratio* itself is a key driver of response, independent of automation. No clean WA or MD-specific residential DA/RT finding located; CA's own recent SCE evaluation exists but no clean topline figure found yet. **Net effect: adds real signal on both sides, doesn't resolve which of the three options above to use.** **HEMS market-availability findings, 2026-09-02, direct user research request**: checked seven named consumer HEMS/automation products directly (not taken at face value) — Homey, gridX, Conow, EcoFlow, ABB ReliaHome, Tesla Powerwall/Gateway, plus third-party automation layers (PowerPilot, BatteryProfit). Finding, in the user's own words, confirmed accurate against what was verified: "HEMS that can plan and respond to DA/RT retail pricing are starting to appear, and while more plentiful in the EU/UK, are now also available in the US, and can even now operate on available Dominion TOU rate plans." Detail behind that summary: Homey, gridX, and Conow are genuinely real products but built for and marketed to EU dynamic-contract customers specifically (EPEX Spot, Nord Pool, the EU's own Euphemia day-ahead-coupling algorithm) — even EcoFlow, a company with a real US retail presence, splits this way: its EU site explicitly integrates with 500+ dynamic tariff providers (Tibber, Nord Pool, EPEX SPOT), while its US product page uses only fixed peak/off-peak TOU language, no dynamic-tariff providers named. The clearest US-side confirmation is Tesla Powerwall via third-party automation (PowerPilot, BatteryProfit) — real, working, commercially-available products syncing a Powerwall to ComEd's actual hourly real-time price feed every 5 minutes, confirming the automation layer itself is solved and market-ready today, not theoretical. **Worth preserving precisely for any future reader**: PowerPilot's own coverage table lists ComEd and Ameren (both IL) specifically as "Real-time"; every other utility it supports, including Dominion, is listed as "TOU" only — Dominion itself does not currently offer a true hourly day-ahead/real-time retail rate program, so the automation operates against Dominion's existing fixed-period TOU plan, not a DA/RT one. The prerequisite gap is the retail rate program, not the automation technology. |
| **The actual hourly price shape needed to drive the price-response mechanism** | **This is not a citation gap — real, usable primary data already exists and simply hasn't been processed yet.** Three files of real PJM real-time hourly LMP data for Dominion-territory nodes were uploaded and checked this turn: `tysons-fairfax-rt_hrl_lmps-2025.csv`, `Richmond-rt_hrl_lmps-2025.csv`, `LoudounAggregate-rt_hrl_lmps-2025.csv` (full year 2025), plus a partial 2026 update for Tysons/Fairfax. These are genuine, hourly, node-specific real-time LMPs — exactly the kind of data needed to derive a real hourly price shape rather than continue relying on the confirmed-empty placeholder (`lp_derived_seasonal_shapes_PERMANENT.npz`, Internal Debugging Log #14). Not yet built into a usable shape — a concrete, ready-to-do next step, not something you need to source. |
| Heat pump efficiency / PHIUS building standards' own demand-reduction magnitude | **Not sourced at all this session.** This is part of the DSM suite per the white paper section's combined definition and your own "load shifting, load reduction, lesser peak load" description, but no specific quantification (how much peak/energy reduction these measures produce) has been researched here. Genuine, unaddressed gap. |
| Resulting Scenario 3-specific demand series | **Not built.** Scenario 3's own demand should be lower/reshaped relative to Scenario 1's raw demand once DSM effects are applied — this means Scenario 3 needs its own demand input files, not a reuse of the existing `checkpoint_*_demand_v2.npz` set. Foundational, not yet started. |

## 5. DSM/DER Taxonomy for Scenario 3

*Built from the user's own proposed categorization (the standard
Gellings "load-shape objectives" plus an EE/DR/Strategic-Load-Management
mechanism-level split), refined over four rounds of discussion.
Structured for eventual use as its own appendix, with a condensed
version for the white paper body (5.6) — every tier below is meant to
survive that transition without rework. Full citation list at the end
of this section.*

### Why four parallel categories, not one taxonomy

An earlier draft tried to hold everything inside a single DSM framework,
using a "Tier 0" scope boundary to wall off ownership/siting elements
from the demand-side taxonomy proper. Direct discussion surfaced a
cleaner structure: rather than one taxonomy with an internal boundary,
four parallel categories, each mapped to what it actually changes in
this project's own model — **Category A (DSM)** changes a demand input;
**Category B (location allocation)** changes who owns and where each
share is physically sited, a static question; **Category D (market
participation)** changes how each owner transacts, a dynamic question;
**Category C (land use)** changes land accounting and offsite economics
without touching dispatch at all. B and D were originally one category
("ownership and market participation") — split apart once it became
clear the heading itself was doing two jobs: B.1-B.3 (who owns what,
where it sits) don't change once built, while D.1-D.3 (market access,
dispatch behavior, compensation) are live, ongoing questions about how
that ownership actually behaves. This also resolved a second problem
the single-taxonomy version couldn't cleanly hold: owners and DER
Aggregators (DERAs) responding to wholesale price signals share DR's own
*mechanism* (a price trigger) but produce a *supply-side* effect
(modulating dispatch for arbitrage, not reducing their own consumption)
— genuinely a third thing, not a subtype of either DSM's DR category or
traditional, utility-centered "Strategic Load Management." Category D
gives this behavior an honest home (D.2) instead of forcing a choice
between two categories it only partly resembles.

### 5.1 Category A — Demand-Side Management

**A.1 Load-shape objective** (the Gellings six, unchanged from the
original proposal): Peak Clipping, Valley Filling, Load Shifting,
Strategic Conservation, Strategic Load Growth, Flexible Load Shape.

**A.2 Mechanism**:
• **Energy Efficiency (EE)** — permanent reductions via equipment
  upgrades and behavioral habits.
• **Demand Response (DR)** — price-based (TOU/CPP/RTP/day-ahead) or
  incentive-based (direct load control, curtailable load).
• **Automated EE/DR hybrid** *(not a subcategory of either parent)* —
  smart HVAC/BEMS responding automatically to a price or grid signal
  without requiring the customer's own real-time attention. This
  session's own research found the automation layer itself is the
  likely explanation for why the largest-scale study of *manual* price
  response (Spain, 2015) found near-zero effect while automated-system
  simulation literature reports meaningfully higher figures — DOE's own
  Grid-interactive Efficient Buildings (GEB) framework treats this
  convergence as its own recognized category for the same reason.
• **Passive/automatic** *(new, not a subcategory of any of the above)* —
  utility-side, always-on reduction with no customer enrollment, no
  override behavior, and no event-window assumption at all (e.g.
  Conservation Voltage Reduction). Named as its own mechanism type
  because it structurally lacks the entire class of estimation problem
  (enrollment rate, override rate, event-window timing) that dominated
  this session's own DLC-magnitude work — not because it's a minor
  variant of EE or DR.
• **On-site thermal/physical storage** *(new, not a subcategory of any
  of the above)* — a built asset (ice storage, chilled-water storage)
  that shifts load from peak to off-peak by storing thermal capacity
  rather than cycling equipment (DLC) or responding to a signal (DR).
  Closer in spirit to a battery than to any other item in this list.

**A.3 Scenario 3's own elements, mapped** (updated 2026-08-24 with newly-identified features
alongside the original three — see this session's own `Internal_Debugging_Log.md` #56-63 for the
PHIUS/SEER/HSPF/IEER and DLC-magnitude build work this table's status column now reflects):

| Element | Load-shape objective | Mechanism | LP impact |
|---|---|---|---|
| A.1 — ComEd-style day-ahead/real-time rates | Load Shifting (primary), some Peak Clipping | DR (price-based) → automated EE/DR hybrid in practice | Demand input — magnitude and hourly shape, per #4's elasticity/price-response mechanism. **Real-world enrollment caveat**: ComEd's own actual RTP program has reached only ~1% residential enrollment since 2007 (opt-in) — relevant to a later realistic-adoption discount, not to Scenario 3's own ceiling-scenario framing (see this session's own direct clarification: Scenario 3 is explicitly a "what if all features were adopted" ceiling, not a slow-adoption trajectory). **Equity/sufficiency check: not directly applicable in the same form** — A.1 is a retail *pricing* mechanism (customers pay different prices at different times), not a separate $/kW *incentive payment* the way every other item in this table is; there is no distinct compensation rate to benchmark against avoided cost the same way entry #82 did for A.2 (extended). A related but genuinely different question — whether the underlying rate design itself reflects Dominion's own avoided costs accurately — remains open and unaddressed, deliberately noted here rather than silently skipped |
| A.2 — Incentive-based DR: smart thermostats, EV charger control | Peak Clipping (typically) | DR (incentive-based / DLC) | Demand input — **quantified this session**: EV Charger Rewards ~3.51 kW/participant expected reduction (3-6pm event window, gross figure, override discount not yet applied); smart thermostats modeled as DLC per direct user decision, matching Dominion's own EV Charger Rewards mechanism. **Equity/sufficiency check: now performed, 2026-08-26** — converting the $40/yr flat incentive to a $/kW basis using the already-derived 3.51 kW/participant figure gives an implied rate of **$11.40/kW/yr**, capturing only **~1.0-1.6%** of avoided generation-capacity cost against this project's own established peaker benchmarks (Aeroderivative $1,175/kW-yr, F-Class $713/kW-yr) — a materially wider gap than even the already-flagged-as-low large-C&I rate (A.2 extended, entry #82: $36/kW/yr, 3.1-5.0% capture). **Direct modeling implication, user-confirmed**: given this gap, Citizen EV participation in Dominion's own existing DLC program should NOT be assumed automatic/default — the incentive is genuinely unlikely to drive meaningful voluntary enrollment on its own, consistent with this project's own broader avoided-cost findings across every incentive-based program checked so far. **Territory-wide scale-up ceiling: coded, 2026-08-27** — see the dedicated subsection immediately following this table for the full sourcing and the ceiling-vs-realistic-enrollment distinction |
| A.2 (extended) — **Water Energy Rewards DLC** *(newly identified)* | Peak Clipping | DR (incentive-based / DLC) | Demand input — **quantified this session**: ~0.173 kW/participant expected reduction (flat 24-hour duty-cycle assumption, gross figure, override discount not yet applied). Real Dominion program, confirmed via the PTR mutual-exclusivity list (Section 4) and its own program page. Enrollment status: **closed to new participants** as of 3/31 — doesn't block Scenario 3's own ceiling-scenario inclusion, but a real constraint on this program's actual growth. See `Internal_Debugging_Log.md` #65. **Equity/sufficiency check: not yet performed** — this program's own incentive rate has not yet been benchmarked against avoided-cost. A.2 (extended, Large C&I)'s own cross-check (entry #82) found a meaningful gap; whether a similar gap exists here is an open question, not yet checked — to be addressed when this program is covered directly |
| A.2 (extended) — **Large C&I interruptible/curtailable tariffs** *(built 2026-08-24)* | Peak Clipping | DR (incentive-based) | Demand input — **per-customer/per-MW magnitude quantified this session**: $36/kW/yr, ≥100 kW eligibility threshold, 10-20 events/yr (real Dominion program, "Non-Residential Curtailment Program," genuine operational load reduction — HVAC/lighting/process/refrigeration adjustments, no backup generation required). Correctly distinguished from the separate, previously-conflated "Non-Residential Distributed Generation Program" (A.7 appendix, Section 1.1b — backup-gen switchover, different eligibility/compensation structure entirely). **Aggregate MW scale-up remains an open, disclosed gap**, structurally identical to A.6's and A.7's own already-flagged scale-up gaps: no enrollment or eligible-capacity figure found published anywhere. **Avoided-cost cross-check added (direct user request)**: benchmarked against this project's own established peaker costs (Aeroderivative $1,175/kW, F-Class $713/kW) annualized at this project's own 4.5% real WACC over a 30-year life, the $36/kW/yr incentive captures only ~41% (Aeroderivative) to ~71% (F-Class) of avoided generation-capacity cost alone — before any avoided-transmission-cost adder, which is not yet sourced and would only widen the gap further. **Flagged as a candidate for a higher, avoided-cost-anchored incentive rate** in any future LP formulation, not a recommendation of a specific alternative figure. **Cross-state empirical check added (direct user request, 2026-08-24)**: every commercial curtailment program found across NY, CA, MA, WA, and HI (NJ yielded no clean utility-level figure — a genuine structural difference, not a search gap) pays more per kW than Dominion's $36/kW/yr, ranging 1.37x to 10.42x depending on program and state, corroborating entry #82's own theoretical avoided-cost finding with independent, empirical evidence. **19 additional jurisdictions tracked for future evidence/strategy searches** (sourced from CESA's own 100%-clean-energy-states list, not yet checked) — see the state coverage tracker at the end of `Cross_State_Commercial_Curtailment_Incentive_Comparison.md`. **A third, independent line of evidence added (direct user follow-up, 2026-08-24)**: real-time LMP data at actual Dominion-zone locations (Loudoun, Tysons, Richmond, VA Beach) shows avoided-energy-cost value alone running 259-379% of the $36/kW/yr flat rate (perfect-foresight upper bound, not a realistic capture rate) — plus a genuinely actionable finding that extreme-price event timing splits by sub-location within Dominion's own zone (Northern VA peaks in summer heat; Richmond/VA Beach peak in winter cold), with the existing call-window design capturing this well at Northern VA locations (85% of top hours) but measurably less well elsewhere (70-75%). See `Dominion_Zone_Load_Shape_and_LMP_Analysis.md` for full insights/rationale/tradeoffs. See also `large_ci_curtailment_analysis/` |
| A.3 — Heat pump efficiency, PHIUS standards | Strategic Conservation | EE (equipment upgrades) | Demand input — **quantified this session** (superseding this row's own prior "not yet quantified" status): residential cooling/heating (SEER2 18→22, HSPF2 9→12) and school HVAC (IEER 20.8, DOE Tech Challenge ~50% by 2035), each with PHIUS Core envelope conservation (~51.1% heating+cooling reduction) layered on new construction. Full stock-turnover model, MWh conversion, and Scenario 3 hourly demand set built — see `Appendix_Efficiency_Stock_Turnover_Model.md`. **Equity/sufficiency check: not yet performed** — this program's own rebate/incentive structure has not yet been benchmarked against avoided energy and/or capacity cost. A.2 (extended, Large C&I)'s own cross-check (entry #82) found a meaningful gap for that program specifically; whether a similar gap exists here (a different kind of program — efficiency rebates, not direct curtailment payments) is an open question, not yet checked — to be addressed when this program is covered directly |
| A.4 — **Heat pump water heaters (HPWH)** *(newly identified)* | Strategic Conservation | EE (equipment upgrades) | Demand input — **quantified this session**: ~35.9% savings by 2045 (2,152,273 MWh), triggered by DOE's own May 2029 federal water heater rule rather than a project-chosen policy year. Reuses the same RECS source table as A.3's own space-heating figure; scoped to the ~73% of South Atlantic households using electric water heating (EIA RECS Table HC 8.8), not the full residential customer count. See `Internal_Debugging_Log.md` #67. **Equity/sufficiency check: not yet performed** — this program's own rebate/incentive structure has not yet been benchmarked against avoided energy and/or capacity cost. A.2 (extended, Large C&I)'s own cross-check (entry #82) found a meaningful gap for that program specifically; whether a similar gap exists here is an open question, not yet checked — to be addressed when this program is covered directly |
| A.5 — **Conservation Voltage Reduction (CVR)** *(newly identified)* | Strategic Conservation | Passive/automatic *(new mechanism type, see 5.1's own updated A.2 Mechanism list)* | Demand input — **deprioritized, 2026-08-24, not abandoned**. Scoped in detail (ANSI C84.1 114-126V band, CVR factor = %energy/%voltage, Dominion's own real, published 0.92 pilot CVR factor and 2.8% system-wide projected savings, "up to 4%" demonstrated) -- see `Internal_Debugging_Log.md` #69 for the full scoping record. **Deprioritized specifically because Dominion already has a real, SCC-approved (2022) Voltage Optimization program in active rollout, tied to ongoing smart-meter deployment** -- unlike every other A.x item, which represents genuinely new adoption not yet reflected anywhere, CVR's own effect may already be partially or fully embedded in the demand-checkpoint data this project already uses (which is itself Dominion-sourced), creating a real double-counting risk if added again on top without first checking. Not re-prioritized until that overlap question is resolved. **Equity/sufficiency check: not applicable** — CVR is a passive/automatic grid-side mechanism with no customer-facing incentive payment at all, unlike every other item in this table; the avoided-cost cross-check framework (entry #82) has no direct analog here |
| A.6 — **Thermal energy storage, commercial first, schools deferred** (ice/chilled-water) *(newly identified, rescoped 2026-08-24)* | Load Shifting | On-site thermal/physical storage *(new mechanism type)* | Demand input — **per-building magnitude quantified this session**: ~23,551 kWh/yr office cooling energy (CBECS-sourced), ~33% typically shifted to off-peak (~7,850 kWh/yr shifted), with a documented ~12% net INCREASE in total annual energy alongside a ~36% cost reduction — genuinely different from every EE/DLC stream in this project, which reduce total energy; A.6 shifts it in time while very plausibly using slightly more. **Aggregate MW/MWh scale-up remains an open, disclosed gap**: no clean Dominion-territory commercial-floorspace or building-count figure was found; a multi-step derivation (national floorspace × Virginia population share × Dominion's own share) was considered and explicitly rejected as too compounding-uncertain given Virginia's disproportionately office/data-center-dense economy. See `Internal_Debugging_Log.md` #71 and `thermal_storage_analysis/`. Rescoped from "schools first" to "commercial first," direct user reasoning confirmed against this project's own already-sourced data: Virginia public schools are out for summer roughly mid-June through early August, largely unoccupied exactly when grid stress peaks -- confirmed directly against the real, already-sourced 2026 DLC event-history dates (entries #63/#65): 11 of 18 events (61%) fall within the school-out window, with most of the remaining August events likely preceding full student re-occupation too. Commercial buildings operate at full occupancy and full cooling load continuously through summer, aligning directly with the actual peak-stress window this asset is meant to serve — confirmed quantitatively, not just qualitatively: CBECS's own "open continuously" operating-hours category shows the highest per-square-foot electricity intensity (19.1 kWh/sq ft) of any category. Schools not abandoned, deferred pending commercial scoping. **Refinement preserved for whenever schools are un-deferred**: the "early August" return date is not a single-stage reopening -- teachers return roughly 2 weeks before students, meaning partial building occupancy and correspondingly partial cooling load ramps up before full student re-occupation; any future school-side re-analysis of the DLC-event-overlap percentage should treat this as a two-stage return, not a single date. **Equity/sufficiency check: not yet applicable** — this mechanism does not yet have a determined $ incentive/compensation figure to benchmark (see this row's own "open gap" notes above). When one is established, it should be checked against avoided-cost the same way A.2 (extended, Large C&I) was (entry #82) |
| A.7 — **Data center demand flexibility** *(newly identified, elevated 2026-08-24)* | Peak Clipping / Load Shifting | DR (mechanism TBD — price-based or incentive-based, program-design-dependent) | Demand input — **not yet quantified; status shifted from "Tier 3, not attempted near-term" to actively being scoped**, per a direct, quantified scale comparison (the "blue whale in a bathtub" exchange, see `Internal_Debugging_Log.md` #72): a single typical data center facility (300 MW) is over 1% of Dominion's own all-time system peak (24,678 MW) alone; a single large facility (up to 7,000 MW, per Dominion's own SCC testimony) is roughly 28% of that entire peak, alone; the requested pipeline (70,000 MW) is 2.8x current system peak. One 300 MW facility's own annual energy throughput (~2.6M MWh/yr) roughly matches or exceeds A.4's entire, statewide, multi-million-household 2045 savings. **The sourcing problem that caused the original deferral has not gone away**: no public equivalent of Dominion's STR/EV-Telematics event-history pages exists for data centers -- operators are notably close-lipped about operational flexibility for competitive reasons that don't apply to residential DR programs. Direct user framing: "an extremely sensitive political/tech topic with many billions of dollars riding on it... we can always make a fully transparent assumption and let others argue about which is going to be actually finalized" -- proceeding on that basis rather than waiting for sourcing that may never fully materialize. **Equity/sufficiency check: not yet applicable** — no $ incentive/compensation figure exists publicly yet for this mechanism (GS-5's own per-unit rates and LLDF's own program design are both still undetermined, per this project's own research — see `Appendix_DataCenter_DemandFlexibility_A7.md`). When one is established, it should be checked against avoided-cost the same way A.2 (extended, Large C&I) was (entry #82) |

### A.2 territory-wide scale-up ceiling — coded, 2026-08-27, direct user-provided data verified and extended

Direct user-provided data on Virginia/Dominion EV counts, checked against primary sources rather
than accepted as-is, given one figure traced to a Facebook post and another was labeled only
"historically."

**Confirmed directly**: Virginia's 76% Dominion-territory share is real, but tied to a specific,
dated snapshot -- Dominion's own 2021 Charging Tariff filing (25,500 total VA EVs at the time), not
a current, ongoing measurement. The 220,000-by-2027 Dominion projection is real (confirmed against
a primary-source-adjacent article, not just the original Facebook post), but turned out to be one
of TWO different Dominion-attributed projections found from different sources/vintages --
150,000-500,000 by 2030 (a genuinely wide range, from an earlier source) is the other, preserved
separately rather than collapsed to one.

**Found beyond what was provided**: Dominion's own stated 2038 EV peak-demand figure (1,600 MW) --
a different metric from the DLC-ceiling calculation below (total EV charging load added to the
grid, not the DLC-reducible portion of it), kept as context only, not conflated. Also found: a real,
formal regulatory challenge to Dominion's own forecasts -- Sierra Club's own expert witness testimony
(Erin Camp, PhD, Synapse Energy, in an actual SCC proceeding) argues Dominion's own service-territory
EV registration is likely to run roughly double the utility's own forecast by 2030, a sourced
argument that Dominion's own numbers may be understated, not merely uncertain.

**What this does and does not resolve, stated directly**: this closes the CEILING half of the
A.2 scale-up gap (if every EV in Dominion's territory enrolled, what's the total) -- matching
Scenario 3's own explicit full-adoption framing. It does NOT resolve the REALISTIC
enrollment-rate half, which remains genuinely open; no data source found addresses actual EV
Charger Rewards enrollment as a share of the eligible EV population.

**Coded**: `dlc_analysis/dlc_assumptions.py` Step 8 (`territory_wide_ceiling_estimate_mw()`, +8 new
tests) computes ~102,209 EVs in Dominion's territory (134,486 statewide x 76%) x the already-derived
3.51 kW/participant figure = **~359 MW** ceiling. The output's own `is_realistic_enrollment_
estimate: False` field makes the ceiling-vs-realistic distinction structurally explicit, not just
stated in prose -- a caller cannot silently treat this as a near-term planning figure without seeing
that flag. `EVChargerRewards`'s own adapter exposes this via a direct passthrough, consistent with
this project's own established migration pattern.

**A separate, real bug found and fixed in the same pass**: `avoided_cost_comparison()`'s own
`framing_note` string still said "5% utility margin" -- stale text left over from entry #112's own
margin change to 0%, caught while reviewing this file for the new work, not by a dedicated search.
Fixed directly.

### A.2/D.2 ceiling split 50/50 between EVChargerRewards and CitizenEVV2G, with a real discharge-rate finding — coded, 2026-08-27, direct user instruction

Direct user instruction: split the territory-wide ceiling 50/50 between the two mutually-exclusive
programs (rather than each independently assuming 100% of the same population), and use the Ford
F-150 Lightning's own 9.6 kW bidirectional discharge rate for CitizenEVV2G's own per-vehicle power
figure.

**The 50/50 split, coded on both sides**: `dlc_assumptions.py` gained
`DLC_VS_V2G_POPULATION_SPLIT_PCT` (the single source of truth for the split) and a new
`territory_wide_ceiling_estimate_50_50_split_mw()` -- **~179.5 MW**, exactly half the original 100%
reference ceiling (~359 MW, preserved unchanged as a distinct "if this program alone captured every
eligible vehicle" reference point, not deleted). `citizen_ev_v2g_feature.py` gained its own
equivalent, reusing the same split constant from `dlc_assumptions.py` rather than restating it.

**The F-150 Lightning figure, verified before use, not accepted at face value**: the 9.6 kW rate is
real and directly confirmed (Ford's own official Intelligent Backup Power announcement). But two
real discrepancies surfaced in the same check, disclosed rather than smoothed over: (1) the user's
own "close to 90 kWh" characterization does not hold up -- the Lightning's real battery options are
98 kWh or 131 kWh (the pack specifically associated with the 9.6 kW feature), neither close to the
90 kWh default, which was kept unchanged since it was independently justified as a sales-weighted
market average, not meant to represent this specific vehicle; (2) a second, more recent source
states the Lightning's own V2L rate is 2.4 kW, not 9.6 kW -- likely two different discharge
pathways on the same vehicle (dedicated Home Integration System vs. portable V2L outlets), with 9.6
kW judged the more relevant figure for this project's own grid-directed use case, but a real,
disclosed discrepancy rather than an uncontested single answer.

**A genuinely useful physical check, computed rather than assumed**: does the 9.6 kW hardware rate
or the 79.46 kWh available energy actually bind over the 3-hour return-home window? Verified
directly: sustaining 9.6 kW for 3 hours needs only 28.8 kWh, well under the 79.46 kWh available (a
~51 kWh margin) -- the hardware rate is the binding constraint, with real headroom to spare, not a
near-tie. `per_vehicle_discharge_power_kw()` computes `min(hardware rate, energy/window)` rather
than assuming either side wins, so this holds as a genuine result, not a hardcoded outcome.

**The resulting ceiling, and a real asymmetry worth surfacing directly**: CitizenEVV2G's own 50/50
ceiling comes out to **~490.6 MW** -- using the same 51,105-vehicle population as the DLC side's own
~179.5 MW, but meaningfully higher purely because the per-vehicle rate (9.6 kW hardware) is so much
larger than the DLC side's own expected curtailment (3.51 kW). Not an error -- a real structural
difference between "how much a vehicle can discharge on demand" and "how much load a DLC event
typically clips" -- guarded by a dedicated regression test rather than left to silently drift.

**A real, disclosed gap NOT resolved by any of this**: both ceilings share the same base population
(the average US BEV fleet in Dominion's territory), but CitizenEVV2G specifically requires
bidirectional-capable hardware -- materially rarer than the standard equipment the DLC side's own
population reflects (already flagged in this module's own top-level docstring). CitizenEVV2G's own
490.6 MW ceiling is therefore looser/more optimistic than a true V2G-hardware-eligible-fleet figure
would be -- stated directly in the function's own output (`hardware_eligibility_caveat`), not just
in this document.

**Tests**: 11 new for `citizen_ev_v2g_feature.py` (31 total, all passing) and 9 new for
`dlc_assumptions.py` (33 total, all passing) -- including a dedicated test proving the
binding-constraint logic is genuinely computed (not hardcoded to currently return the hardware
rate), and a regression guard on the ceiling asymmetry itself.

Valley Filling and Strategic Load Growth have no mapped element —
confirmed intentional (nothing in Scenario 3's definition promotes
off-peak load growth or EV adoption), not an oversight.

**Prioritization for future build-out** (direct user request, 2026-08-24, revised same day after a
second review explicitly separating genuine near-term builds from items to flag for later rather
than force): **Build now** — A.4 (HPWH, reuses the existing RECS data and stock-turnover model
pattern directly), A.5 (CVR, simplest possible estimation given no enrollment-behavior modeling
needed), and Water Energy Rewards DLC (same chain as the existing EV charger magnitude work,
different end-use). **Build after those three** — A.6 (thermal storage; needs real performance/cost
data plus its own dispatch-shape decision, now resolved by the same hybrid-exogenous approach used
for WMA/V2G above). **Noted for future modeling incorporation, not attempted near-term** — A.7 (data
centers: no public equivalent of Dominion's DLC event-history pages exists for this at all, the
weakest data foundation of anything on this list despite potentially being the largest-magnitude
item) and the C&I interruptible extension of A.2 (large-C&I-specific program data likely harder to
source than the residential programs already used). School bus/citizen/municipal V2G and CPP/CPR
remain Tier 4 as before (CPP/CPR largely already covered by existing A.1/PTR work, more a taxonomy
note than a new build item).

### 5.2 Category B — Solar/Storage Location Allocation

Not DSM, and not market behavior — purely who owns and where each share
of Scenario 3's build-out physically sits. Static once built. Already
partly scoped elsewhere in this project (Appendix E); this section is
the fuller taxonomy that sits behind it.

**B.1 Ownership.** "80% utility-scale" is not monolithic — it maps
directly to Dominion's own three VCEA-compliance riders:

• **B.1.a — Dominion-owned** (Rider CE): Company-constructed and owned.
  *(Rider CE is a specific cost-recovery tariff, not a synonym for the
  VCEA itself — the VCEA is the enabling statute all three riders below
  operate under.)*
• **B.1.b — Third-party physical PPA** (Rider PPA): third-party-owned,
  under a long-term physical delivery agreement.
• **B.1.c — Unbundled REC purchases** (Rider RPS): a compliance/
  financial instrument, not a physical asset — noted for completeness,
  not part of the physical build.
• **B.1.d — DER-owned rooftop** (10%).
• **B.1.e — DER-owned parking canopy** (10%).

**B.2 Siting percentages**: 10% rooftop (B.1.d), 10% parking canopy
(B.1.e), remaining 80% utility-scale (split across B.1.a/B.1.b/B.1.c).

### 5.2.1 Rooftop and parking-canopy owner classification (direct user decision, 2026-08-23)

High-level modeling rule, not intended to capture every downstream
distribution mechanic — only who is the single participating entity for
FERC 2222/DERA-registration purposes at each property type. **Rule:
whoever legally owns/controls the physical asset is the "owner," for
modeling purposes, regardless of whether that entity is for-profit or a
non-profit/member-owned association** — the model does not track how an
owning entity subsequently distributes proceeds among its own members or
tenants.

| Property type | Rooftop owner | Parking lot owner |
|---|---|---|
| Single-family home | Resident (DERA required — see below) | N/A |
| Townhouse | Resident (DERA required — individually-owned roof) | HOA (C&I-style, direct participation) |
| Condo building | HOA (divvies proceeds per its own rules) | HOA |
| Apartment building | Landlord | Landlord |
| C&I / government (incl. schools) | The entity itself | The entity itself |

**Participation pathway follows directly from B.1.d/B.1.e's own existing
D.1 rule** (Scenario3_Scope_and_Gaps.md §1, D.1): owners under 100 kW go
through a DER Aggregator; owners at or above 100 kW can participate
directly. In practice this means:
- **Residential rooftop (single-family and townhouse)**: near-universally
  under 100 kW individually — assumed to always go through a DERA. This
  is Scenario 3's own largest source of DERA-compensation-structure
  dependency (per this session's own question: "a residential DER will
  invariably go through a DERA to participate, so we have to investigate
  DERA compensation approaches" — **flagged as an open research item**,
  not yet resolved).
- **C&I, government/schools, apartment landlords, and HOAs (condo and
  townhouse)**: assumed to clear 100 kW on size alone (a single
  building's rooftop, or a lot canopy over even a modest number of
  spaces, gets there easily) — direct participation, no DERA needed.

**A genuine, not-yet-resolved distinction this classification surfaces**
(noted directly, not smoothed over): an HOA is typically a non-profit,
member-owned entity, while a landlord is a for-profit one. This does not
change the *participation mechanism* (both are single legal entities that
can sign a direct PJM/DERA agreement), but it is a real, worth-naming
difference in the *economics downstream of that entity* — HOA proceeds
plausibly flow back to unit owners as reduced dues or a direct rebate,
extending solar-canopy economics to multi-family owner-occupants who would
otherwise have no path to rooftop solar ownership at all. Not modeled
separately in the LP (per this rule's own "single participating entity"
scope), but worth naming explicitly in the whitepaper's own equity
narrative, not left implicit.

**Not yet resolved, flagged rather than assumed**: individually-metered,
townhome-style complexes where the roof/unit boundary is more ambiguous
than a clean landlord/tenant or HOA/owner split. Not pursued further this
session — noted as an edge case for later if the residential/C&I
classification needs more granularity.

### 5.2.2 DERA compensation research — Dominion's own, already-filed VPP tariff (direct research, 2026-08-23)

Direct follow-up to §5.2.1's own flagged research item: "a residential DER will invariably go through a DERA to participate, so we have to investigate DERA compensation approaches." This section is the result of that research — and it turned up something more directly useful than any out-of-state comparison: **Dominion has already filed the actual, real, Virginia-specific tariff this project needs**, not a hypothetical.

**Legal framework — Virginia's own Community Energy Act (HB 2346/SB 1100, enacted May 2, 2025, Va. Code §56-585.1:16)**: requires Dominion to petition the SCC for a VPP pilot (up to 450 MW) by December 1, 2025 (done — Docket PUR-2025-00211), and a customer/aggregator participation tariff by November 15, 2026. The statute explicitly contemplates both direct and aggregator-mediated enrollment, and requires the SCC to weigh "lessons learned" against FERC Order 2222 implementation directly — confirming the state and federal frameworks are meant to work together, not as competing pathways. Pilot concludes July 1, 2028; a permanent program follows.

**Dominion's own proposed tariff (filed with PUR-2025-00211, Company Exhibit — Witness CSY, Schedule 1) — concrete, sourced incentive figures**:

| Program | Incentive | Eligibility |
|---|---|---|
| **Residential Battery Storage Pilot** (DR) | $1,000 one-time enrollment + **$294/year** thereafter | Residential, existing qualifying battery |
| Residential IAQ Battery Storage Purchase Pilot | Free 13.5 kWh Tesla Powerwall 3 (~$20,000 value) + $183/year avg. (companion DR pilot) | Income/age-qualifying (≤80% AMI or 60+ with ≤120% state median) |
| Residential Managed EV Charging (non-TOU / TOU) | $40 + $10/mo. / $20 + $5/mo. | EV owners with L1/L2 charger |
| Residential Smart Thermostat | $25 one-time + $25/year | Any residential |
| Non-Residential Curtailment | ~$26,250/year average | C&I, DSM Rider payers |
| **BYOD (Bring Your Own Device) Aggregator Access Pilot** | Pay-for-performance, **"varies across residential, commercial, industrial, and vendor-managed segments"** — exact rate not published in this filing | Res./C&I/industrial via an approved aggregator, or up to 1,000 customers directly with Dominion as pilot aggregator |

**The BYOD program is the one that matters most for this project's own B.1.d/B.1.e (DER-owned rooftop/canopy) modeling** — it's explicitly the third-party-aggregator pathway (Voltus and similar platforms would plug in here), device-agnostic, and is Dominion's own single largest projected contributor to the 450 MW target: **200 MW of the ~466 MW total 2030 pathway**, dwarfing every other program in the portfolio (next largest: Residential Battery Storage Pilot at 88 MW). This confirms Dominion itself expects the aggregator-mediated pathway to carry roughly half of total VPP capacity — directly validating this project's own B.1.d/B.1.e DERA-dependency assumption.

**A real, disclosed gap, not glossed over**: the BYOD program's own actual $/kW or $/MWh pay-for-performance rate is not disclosed in the tariff filing itself — only that it "varies" by customer segment. Whether Dominion has since published a rate schedule (the tariff itself is due November 15, 2026, per the statute — this December 2025 filing pre-dates that final rate-setting step) is not yet checked. **For modeling purposes, the Residential Battery Storage Pilot's own concrete, sourced figure ($1,000 enrollment + $294/year) is the best currently-available Dominion-specific proxy** for what a residential battery-storage DER owner earns through a utility-mediated pathway — though it is a direct-Dominion program, not strictly the third-party-aggregator BYOD rate, so should be labeled as a proxy, not treated as identical.

**Confirms the double-compensation/NEM rule found in §D.1's own research directly, in Dominion's own filing language**: "net metering customers may participate but will not receive duplicate incentives for exported energy" (Residential Battery Storage Pilot eligibility terms) — the FERC-level NEM-vs-wholesale prohibition already researched this session is not just a PJM/FERC abstraction; Dominion's own tariff explicitly enforces it at the program level.

**General third-party aggregator market context (Voltus and peers), for scale/plausibility-checking Dominion's own figures against**: Voltus (the named example) operates as a pure-play DER aggregation platform — owns no generation, pays customers a revenue share from wholesale capacity/energy/ancillary-services payments it earns on their behalf ("Voltus earns money for the capacity or energy provided by the residential aggregation and shares it with you and your customers"). Reported 2025 PJM-wide figures: $240M paid to customers across 8.1 GW of aggregated flexible capacity. Exact revenue-share percentage is not publicly disclosed (varies by OEM/hardware-partner contract, per its own B2B2C model with partners like Resideo/Honeywell). Academic literature on aggregator business models documents two common structures directly: (1) aggregator retains a flat ~20% of the customer's own total value created, or (2) aggregator passes through 100% of value but charges a separate flat platform fee instead — **useful as bounding assumptions if Dominion's own BYOD rate remains unpublished**, not as a substitute for it.

**Not yet resolved / follow-up items**:
1. Check whether Dominion has published a BYOD-specific rate schedule since this December 2025 filing (the November 2026 statutory tariff deadline may resolve this directly).
2. The Residential Battery Storage Pilot's own $294/year figure is a *utility-direct* incentive, not necessarily representative of what a *third-party aggregator* (Voltus-style) would pay for the same asset — these could differ meaningfully once BYOD's own rate is known.
3. Scenario 3's own modeling still needs a decision on which of these figures (or an assumed BYOD rate, bounded by the 20%-aggregator-fee heuristic above) to actually use for the residential rooftop DERA-compensation component.

### 5.3 Category D — Market Participation

Governs how each B.1 ownership tier actually transacts — dynamic,
ongoing behavior, as distinct from B's static ownership/siting question.

**D.1 Market access** — genuinely different between the utility-scale
and DER-owned tiers, sourced directly this session:

• **B.1.a/B.1.b: no independent wholesale arbitrage.** A physical PPA
  "requires the offtaker to purchase the output that the seller
  delivers" (Stoel Rives, *The Law of Solar*) — Dominion, buying to meet
  its own load and its own VCEA compliance, is a physical rather than
  virtual/CFD offtaker. Confirmed by direct example: Arlington County's
  2020 PPA with Dominion left the county unable to claim the associated
  RECs, specifically because "Dominion needs to keep renewable energy
  credits from clean power projects for their own compliance with the
  Virginia Clean Economy Act" (Fairfax County Office of Environmental
  and Energy Coordination). RECs bundle with the energy and transfer to
  Dominion by default (Virginia SCC); the developer retains no separate
  REC or wholesale position.
• **B.1.d/B.1.e: real, confirmed market access.** Direct FERC 2222
  participation at ≥100 kW, indirect via DERA below that. Dominion's own
  net-metering documentation confirms distributed owners can choose
  between selling to Dominion or "selling power into the PJM Market" —
  the mechanism Scenario 3's own definition already invokes.

**D.2 Supply-side price response** *(new node)*. Owners/DERAs dispatching
storage or generation in response to wholesale price signals — DR-like
in trigger, supply-side in effect. Applies only to B.1.d/B.1.e, since
B.1.a/B.1.b have no independent market position to act on (D.1). Cross-
referenced to A.2's DR mechanism for the shared trigger, but lives in
Category D because the effect modulates wholesale supply, not the
owner's own consumption.

**D.2 exogenous-vs-endogenous resolution (direct user decision,
2026-08-24)**: WMA and all three V2G items below get a hybrid, still-
exogenous treatment, not genuine LP dispatch variables — resolving the
question the original camel's-back risk table left explicitly open
("not yet reviewed"). Method: use the existing LMP dataset to derive,
per historical day, the optimal N-hour charge/discharge window for a
stated asset duration and round-trip efficiency, producing a fixed
hourly dispatch shape (extending the prior-session Value Factor work,
which only produced a summary multiplier, into an actual applied
shape) — then feed that shape into the hourly demand array the same
way DLC and efficiency reductions already are. No new SoC-tracking
variables added to the LP. Uses perfect-foresight historical dispatch,
appropriate (not an overstatement to caveat away) given Scenario 3's
own explicit framing as a ceiling scenario, not a forecast.

**D.2 multi-day stress-escalation layer (direct user forethought,
2026-08-24, design confirmed same day)**: the per-day optimal-dispatch
shape above has a real, named gap — a fixed daily shape can discharge
an asset on day 1 of a sustained multi-day low-RE event without
reserving capacity for days 2 onward, since low RE generation persists
throughout such an event, limiting how much the asset can recharge
between discharges. This is a different failure mode than anything the
existing all-hours reserve-margin constraint checks for, since that
constraint assumes the build itself is adequate — it doesn't ask
whether a *fixed, pre-computed* dispatch schedule behaves sensibly
across an atypical multi-day run. Directly grounded in a real,
documented precedent rather than a hypothetical: Winter Storm Fern
(already cited in this project's own DLC research) saw PJM, ISO-NE, and
ERCOT act on multi-day-ahead forecasts, and a major DR provider
sustained an activated portfolio for six consecutive days — confirming
this is a real operational pattern, not a theoretical concern.

**No new pricing algorithm is needed to address this** — real,
historical price data already exists and already reflects multi-day
stress when it occurred. What's missing is a **dispatch-rationing
rule**, not a forecasting/pricing model — and the rationing variable is
physical (recharge capacity), not economic (price). Price already
answers *when within a day* to discharge (the existing per-day shape);
a separate constraint is needed to answer *how much total* to discharge
that day, since price alone doesn't reveal whether using it all today
leaves tomorrow short.

**Concrete mechanism, direct answer to "what's the rationing
mechanism if not price" (2026-08-24)**:
1. Identify multi-day stress windows directly from the historical LMP
   data (consecutive days above a price threshold, as already proposed).
2. For each day within a window, compute recharge capacity directly
   from the solar/wind resource data already extensively used
   throughout this project — a low-RE day during the event still
   generates *something*, just less than normal, and that's the real
   ceiling on how much can be refilled before the next discharge.
3. Each day's discharge budget = starting SoC + that day's recharge
   capacity − a reserve held back for the remaining forecast-days of
   the event (e.g. remaining SoC spread across remaining days, or
   weighted toward whichever remaining day the historical data shows as
   most severe).
4. Within that day's budget, price still picks the hour — same
   mechanism as before, now capped by a daily ceiling instead of
   unlimited.

No new data sourcing required — steps 2-3 run entirely on the
solar/wind resource files and multi-day-window logic already in this
project's own hands. Conceptually similar to how a real storage
operator wouldn't fully discharge on day 1 of a forecast 5-day heat
wave knowing days 2-5 will also need capacity — physical energy-balance
reasoning, not a market-signal decision. This remains fully exogenous
(still no new LP variables) — real modeling effort, not a free
extension of the per-day shape, but bounded, and does not
reopen the endogenous-LP risk the original camel's-back discussion was
built to avoid. **Not yet built** — logged here as a confirmed design
direction, not yet implemented.

**D.2 (extended) — School bus vehicle-to-grid (V2G)** *(newly identified,
2026-08-24, confirmed as next item to pick up 2026-08-24 end-of-session)*. Structurally a D.2 item, not a Category A item — electric
school buses sit idle for large stretches (including the entire summer,
when Dominion's own DLC events cluster most heavily per this project's
own §STR/EV-event-history research), and their batteries could actively
*discharge* back to the grid during events, not merely pause charging
(DLC-style, A.2). That discharge behavior is the same supply-side
mechanism type as B.1.d/B.1.e battery dispatch above, just a different
asset class (school-bus fleets rather than residential/C&I DERs).
**Not yet quantified** — Tier 4 priority (newer, less-established
technology than the residential items above; harder Virginia-specific
fleet data). **Directly connects to a real, already-sourced program**: the
Virginia VPP pilot (HB 2346/SB 1100, Va. Code § 56-585.1:16, filed with
the SCC December 2025) explicitly includes "Dominion Energy Virginia to
propose an Electric School Bus Expansion program" as one of its own named
components — worth checking first for whatever program-design/scale
details are available before building this item from scratch.

**Substantial real-program data found, 2026-08-25 morning session**: Dominion's own existing
electric school bus program (predating and separate from, though feeding into, the December 2027
VPP-pilot expansion deadline) is real, active, and well-documented, not a from-scratch build.

- **Original stated target, cross-validated across two independent sources at the time — but NEVER
  ACTUALLY ACHIEVED, corrected 2026-08-25**: 2019 announcement of "up to 1,050 buses... over the next
  five years"; PJM Inside Lines separately reported 50 buses by end of 2020, growing 200/year through
  2025 — arithmetically totaling exactly 1,050, internally consistent as a *stated plan* at the time.
  Similarly, "up to 105 MWh... enough to power more than 10,000 homes" (implying ~100 kWh/bus,
  itself a derived, not directly-stated, figure) was always explicitly a "when fully implemented"
  projection, not a current-state figure — a distinction this section did not carry forward with
  enough force initially.
- **Actual, verified deployment, substantially and materially lower than the stated target**: Virginia
  Dept. of Education reported 226 buses STATEWIDE (not just Dominion's own) as of October 2022 —
  already far behind the pace needed to reach 1,050 by 2025. An official Dominion/Thomas Built Buses
  press release, the most recent precise figure found, states **135 electric school buses operating
  across 25 districts as of March 2024** — roughly 13% of the original 1,050 target. No more recent
  precise count has been found; the current (Aug. 2026) figure is unverified, plausibly somewhat
  higher given continued but slower-than-planned growth.
- **Root cause, real and documented, not a mystery**: reporting on the shortfall directly explains it
  — "legislation that would've given Dominion the green light to oversee the expansion failed in the
  General Assembly," specifically the bill that would have allowed cost recovery for the expanded
  program through rates. The 1,000-bus Phase 2 target was never actually funded the way the original
  plan assumed — a legislative failure, not merely a slow rollout.
- **Practical implication for this section's own magnitude work**: the 105 MWh aggregate capacity
  figure should not be used as a current-state assumption. A rough, illustrative (not solid)
  rescaling using the same derived ~100 kWh/bus unit figure against the verified 135-bus count gives
  approximately **~13.5 MWh currently** — flagged as illustrative given it chains a derived unit
  figure through a corrected count, compounding rather than resolving uncertainty. Any future
  magnitude-chain build for this item should anchor on the verified ~135-bus figure (or a more
  current count if found) as the actual-deployment case, while still citing the original 1,050/105
  MWh figures as the stated long-term target/upper bound, not the current reality.
- **Real vehicle specs** (Dominion's own page): Thomas Built Saf-T-Liner C2 Jouley, 120-160 mile
  range, ~3hr full charge. **Average daily round-trip route is 80 miles** — meaning a typical bus
  uses only 50-67% of its range on a normal school day, leaving real headroom for V2G discharge
  without compromising the next day's route — directly relevant to whether V2G capacity exists during
  the school year itself, not just summer.
- **Ownership structure, sourced from the actual signed participation agreement** (Dominion Energy
  Virginia / Fairfax County Public Schools, not just a marketing page): equipment is split into
  "Dominion Owned Equipment" and "School Board Owned Equipment," with cost responsibility following
  ownership directly — "Dominion Energy Virginia shall be responsible for paying all costs of the
  Dominion Owned Equipment... and the School Board shall be responsible for paying all costs of the
  School Board Owned Equipment." Combined with Dominion's own stated option to take ownership of the
  battery specifically, this is the governing principle, though the contract excerpt found does not
  explicitly confirm the battery falls under one category or the other in so many words.
- **Battery warranty cost-sharing, a precise, sourced figure** (via a news report of an official
  Dominion communication, not Dominion's own page): "Dominion Energy will also cover the maintenance
  of the charger for 15 years and 50% of the cost of the battery warranty" — not full replacement
  funding. The remaining share presumably falls to the district or other funding sources (the same
  reporting notes EPA Clean School Bus Program grants as a parallel funding stream).
- **A genuinely unusual compensation structure, different from every other program built in this
  project so far**: schools are not paid cash. Instead, "Dominion Energy replenishes battery at no
  charge to customer within three hours" after a V2G call — an in-kind (free replacement energy)
  structure, not a $/kW or $/kWh payment like every other A.2/A.2-extended program. Worth modeling
  as structurally distinct rather than forced into the same $/kW framework used elsewhere.
- **A precise statutory ownership constraint**: "the electric utility shall not own the electric
  school buses as a part of its proposed program, but such electric utility may own the related
  storage batteries" (per the VPP-pilot-era pv-magazine reporting) — Dominion can own the battery,
  not the bus itself.
- **Battery lifecycle context, two figures with different vintages/methods, both preserved rather
  than collapsed into one**: an older industry estimate of 6-10 years battery life (First Student)
  versus a much newer, fleet-data-based figure (BusCMMS, Feb. 2026, based on 847 electric school
  buses across 43 U.S. districts): ~1.5-2%/year degradation, retaining over 80% capacity after 12-15
  years, with most buses retiring for non-battery reasons before replacement is ever needed. The
  newer, real-fleet-data figure is plausibly more reliable than the older generic estimate, though
  both are preserved here rather than silently picking one.
- **Battery cost share of total bus cost**: industry sources put this at 30-50% of the bus's total
  cost — useful context for the scale of the asset involved in any ownership/replacement-funding
  question.

**A second, direct user question answered — local government WMA eligibility, confirmed explicitly
by name**: a World Resources Institute paper specifically on local-government DER aggregation under
FERC Order 2222 states directly: "these DERs may include government owned or contracted solar and
storage resources, **fleets of electric school and transit buses** and municipal vehicles." School
bus fleets are not merely eligible in principle — they are named as a specific example DER type for
local-government aggregation.

- **A real structural nuance — this is very plausibly an either/or choice, not an additive stack**:
  the same WRI source notes a fleet owner "would want to weigh differences, such as compensation and
  risks, between the two options" (Dominion's own in-kind program vs. wholesale participation via
  aggregation) "before choosing." FERC's own official explainer directly confirms the underlying
  reason: "Order No. 2222 permits some restrictions on participation and compensation in the
  wholesale markets if a DER receives compensation in a retail program" — specifically to avoid
  duplicative compensation for the same underlying service. A school district enrolled in Dominion's
  own free-energy-replacement V2G program likely cannot also separately monetize that same battery
  capacity via WMA simultaneously — this should be modeled as a mutually-exclusive choice per fleet/
  battery, not a stackable additional revenue stream, mirroring the same non-duplication logic already
  established for A.2-extended's own mutual-exclusivity constraints (Schedule 10, Distributed
  Generation program, PJM peak-shaving).
- **The 100 kW minimum aggregation threshold, connected directly to the fleet math above**: given a
  single bus's implied battery capacity is ~100 kWh, even a small handful of aggregated buses would
  clear the 100 kW minimum size requirement easily — WMA is a realistic path for a district with any
  meaningful fleet size, not just large ones.
- **Interconnection responsibility stays local even under WMA**: "state and local authorities remain
  responsible for the interconnection of individual DERs for the purpose of participating in
  wholesale markets through a DER aggregation" — a practical implementation detail worth noting, not
  purely a PJM/FERC-administered process end to end.
- **The small-utility exclusion does not apply here**: FERC's rule excludes aggregations of
  customers "of small utilities whose electric output was 4 million megawatt-hours or less," unless
  the relevant retail regulator allows it — Dominion Energy Virginia's own annual sales are far above
  this threshold, so this exclusion is confirmed not applicable to Virginia school districts within
  Dominion's own territory.

**Follow-up research, 2026-08-25 morning, prompted by direct user questions**: source reliability,
legal confirmation of WMA eligibility (federal and Virginia), the V2G-vs-regular-use degradation
distinction, and a cross-state program comparison.

- **WRI source-reliability assessment, requested directly**: World Resources Institute is a large,
  established (founded 1982), mainstream policy research organization, credible in a genuinely
  different tier than lower-quality sources already flagged elsewhere in this project's own climate
  research (e.g. the Watts/Surface Stations material in `Climate_Trends_and_Weather_Station_
  Methodology.md`). One precise caveat: the school-bus-V2G material cited comes specifically from
  WRI's own "Electric School Bus Initiative," an explicitly program-advocacy arm ("aims to build
  unstoppable momentum toward an equitable transition... by 2030"), not WRI's more general neutral
  policy research — worth treating as an informed advocate's account, not a disinterested observer's,
  even where its underlying facts check out (several did, independently cross-confirmed below).
- **WMA legality, confirmed via PJM's own primary tariff text, not just WRI's characterization**:
  PJM's own definition of "DER Capacity Aggregation Resource" is purely technical (100 kW minimum,
  5 MW maximum per aggregation) with no owner-type restriction anywhere — owner-agnostic by design,
  meaning government entities are included by the absence of any exclusion rather than an explicit
  named inclusion. Virginia's own SCC has been actively engaged on DER-interconnection rulemaking
  since May 2022, with a March 2026 tracker report confirming Virginia is currently advancing
  "interconnection reform, VPP pilots, DER aggregation mandates" alongside PA/IL/NJ/MD.
- **A material timeline gap, not previously flagged, found while confirming the above**: the FULL DER
  Aggregation Participation Model (including capacity-market participation specifically) is tied by
  PJM's own tariff text to the 2028/2029 delivery year, and a separate 2024 filing shows PJM
  proposing to push the broader effective date from February 2026 to February 2028, citing delayed
  FERC design clarity. Legal eligibility in principle and near-term operational availability are
  different claims — WMA is very plausibly not a near-term revenue path for a Virginia school bus
  fleet regardless of legal eligibility, given this delay pattern.
- **Battery degradation, corrected**: the BusCMMS source cited previously was checked directly and
  found to never mention V2G or bidirectional discharge anywhere — it is entirely a regular-driving-
  only analysis, so citing it as supportive of the V2G case was an overstatement, now corrected. Real
  V2G-specific findings, genuinely divergent across sources, preserved as a range rather than
  collapsed to one figure: a rigorous, DOE/NREL/Stellantis/LG-Chem accelerated real-world test found
  V2G adds ~1.8%/yr degradation on top of a ~1.5%/yr driving-only baseline (roughly doubling total
  degradation over 10 years: 15% capacity fade EV-only vs. 33% with V2G); a separate 2024/2025 peer-
  reviewed co-simulation study found a much milder +0.31%/yr average; a 2017 University of Hawaii
  study found up to 75% capacity loss in 5 years, but specifically under *unmanaged* V2G cycling, with
  the same source noting smart/managed V2G (plausibly what Dominion's own utility-run program uses)
  should perform meaningfully better.
- **Other U.S. school-bus V2G programs, a real cross-state comparison, not just Dominion in
  isolation**: at least 26 utilities across 19 states have committed to school-bus V2G pilots (WRI,
  May 2025). The most directly comparable, well-documented program — SDG&E / Cajon Valley Union
  School District, CA, via the state's Emergency Load Reduction Program — pays a direct **$2/kWh
  cash** rate (genuinely different from Dominion's in-kind free-replenishment structure), ~10
  events/yr, 1-5hr each, using 60kW bidirectional chargers and ~180kWh battery packs (a useful,
  though higher, cross-check against Dominion's own ~100kWh implied figure). Other real, named
  programs: National Grid delivered 50+ hours of V2G power in Beverly, MA (2021); Con Edison ran a
  5-bus pilot with White Plains, NY schools. A DOE-funded effort (SVIN, ~$11M) is launching 14
  further pilots nationally.
- **A real, unresolved discrepancy in Dominion's own current fleet size, flagged directly rather
  than silently built on**: a January 2026 academic source (MDPI Sustainability) describes Dominion's
  program as having "introduced 50+ ESBs" — not the ~1,050 figure used as this section's own core
  assumption (sourced from a 2019 announcement and a separately-reported 200/yr build-out rate). This
  could reflect the source simply citing the original 2019 first-tranche milestone rather than
  current fleet size, or could indicate the five-year buildout (which should have concluded by
  2024/25) did not reach its stated target. **Not yet resolved** — the 1,050 figure should be treated
  as unconfirmed at current scale, not settled, until Dominion's own actual current deployed fleet
  size is directly verified.

**Modeling-ready module built, 2026-08-25**: `school_bus_v2g_analysis/dominion_school_bus_v2g_
assumptions.py` (+ test suite, 14 tests, all passing) consolidates every Dominion-specific figure
sourced this session into a single, modeling-ready module, following the same pattern as
`large_ci_curtailment_analysis/` for A.2-extended. Every gap is preserved explicitly rather than
filled with a guess — most notably, `EVENT_FREQUENCY_PER_YEAR = None`, since no public indication
of Dominion's own annual dispatch frequency was found despite two targeted search attempts. The
module also documents, rather than silently resolves, two real discrepancies: the battery-capacity
figure (220 kWh directly stated vs. ~100 kWh derived from the now-unreliable 1,050-bus/105 MWh
figures — use 220 kWh going forward) and the ownership wording ("option to take ownership" per
Dominion's own page vs. "will own" per a secondary source).

**Simplified 2030 "turnstile" projection added, 2026-08-25/26, direct user request — TWO scenarios,
after an initial misread corrected directly**: the first attempt (Scenario A below) projected the
fleet forward using the observed historical growth rate — but the user's own original request ("model
the Dominion program at school systems around Virginia by 2030") meant ALL Virginia schools, a full
statewide "bold move" adoption case, not a continuation of the current slow pace. Corrected directly
once flagged, not silently patched — both scenarios are now built and named unmistakably distinctly
(`turnstile_estimate_observed_trend_continuation()` vs. `turnstile_estimate_full_statewide_
adoption()`), since both are legitimate, different what-ifs worth keeping.

**Scenario A — observed-trend continuation** (what was built first, kept as a real status-quo-pace
comparison point, not deleted): fleet size projected forward using the observed historical growth
rate (21.25 buses/yr, derived from the real 50-buses-2020 → 135-buses-2024 data points — NOT the
never-achieved ~200/yr original target rate) to ~262 buses by 2030 → **~433 MWh/yr** potential
discharge.

**Scenario B — full statewide adoption by 2030** (the scenario actually requested): every Virginia
school bus, not just Dominion's own currently-enrolled fleet, electrified and V2G-capable by 2030 —
explicitly framed by the user as deliberately unrealistic ("not entirely realistic, but... trying to
keep it simplistic and give a sense of what a sense of scale could have with these measures... what a
bold move might look like," in contrast to "pilots and slowly increasing implementations"). Uses the
statewide total school-bus count already on record from two independent, genuinely-disagreeing
sources, preserved as a low/high pair rather than collapsed to one number (13,000 per Dominion's own
innovation team via Raconteur; 16,000 per VDOE via WRIC) → **~21,450–26,400 MWh/yr** potential
discharge — roughly 50-60x Scenario A's own figure, illustrating the intended scale contrast between
a status-quo pace and a genuine full-adoption push.

Both scenarios share the same per-bus mechanics (220 kWh stated capacity × 50% route headroom = 110
kWh/bus available for discharge; a clearly-labeled 15/yr event-frequency placeholder — NOT Dominion's
own real, still-unknown figure, and NOT borrowed from any single other program researched this
session), reused rather than reimplemented between the two scenarios. Both explicitly framed as
upper bounds (full discharge assumed at every event, no participation derate, no weather/maintenance
downtime modeled, and for Scenario B specifically, no ramp-up curve within the 2030 date itself — a
simple on/off full-adoption assumption). All parameters are exposed as overridable function
arguments, not hardcoded, so the future, richer, team-reviewed pass can call either function with
different assumptions rather than reimplementing the calculation.

### Cross-program comparison table, 2026-08-25, direct user request

Requested comparison across all school-bus V2G/demand-reduction programs found this session, split
by the user's own two-category framework: (1) reducing charging during high-demand periods
("emergency load reduction") vs. (2) V2G for genuine energy dispatch, with hybrids noted. **An
honest finding stated directly before the table itself**: no well-documented "pure load-reduction-
only" school bus program (charging-pause only, no reverse power flow — analogous to A.2's own DLC
mechanism) was found anywhere in this research. Every real, named program below involves genuine
bidirectional discharge. SDG&E/Cajon Valley is administratively framed under California's emergency
load reduction program but mechanically uses true discharge via bidirectional chargers, so it is
marked a hybrid rather than force-fit into a category it does not actually belong in.

**Category 2: True V2G Energy Dispatch**

| | Dominion (VA) | National Grid (Beverly, MA) | Con Edison (White Plains, NY) | Green Mountain Power (South Burlington, VT) |
|---|---|---|---|---|
| 1. Battery ownership | Utility *may* own battery (option); cannot own bus (statutory) | Not found | Not found | Not found |
| 2. Battery warranty compensation | Utility covers 50% of warranty cost | Not found | Not found | Not found |
| 3. Battery replacement compensation | Not confirmed beyond the warranty share above | Not found | Not found | Not found |
| 4. Mechanism/event basis | True V2G dispatch | True V2G dispatch, summer-only | True V2G dispatch, year-round | True V2G dispatch, year-round |
| 5. Compensation for load reduced | N/A (not a load-reduction program) | N/A | N/A | N/A |
| 6. Compensation for energy dispatched | In-kind: free battery replenishment within 3hrs (no cash rate found) | $200/kW delivered during peak events, avg over summer (one source: $275/kW — genuine discrepancy, both preserved) | VDER Value Stack — day-ahead energy price + capacity value + demand-reduction value (market-linked, not flat); WRI separately describes it as "compensated at reported actual cost to the utility" | Not precisely found; implied via annual figure below |
| 7. WMA allowed | Yes, legally (FERC 2222/PJM tariff, owner-agnostic); likely exclusive of in-kind program; not operational until 2028/2029 delivery year | Not researched | Yes — VDER is itself a market-linked compensation form, administered as a NY state tariff; not confirmed as separate PJM/NYISO WMA specifically | Not researched |
| 8. Event duration | Not found | 2-3 hrs, 3-8pm, Jun-Sep, max 60 events/season (possibly the general residential ConnectedSolutions terms, not confirmed school-bus-specific) | Not found | ~3hr events (per GMP's general BYOD program; not confirmed school-bus-specific) |
| 9. Charger capex/install/O&M | Utility covers charger maintenance for 15 years | MA EV Infrastructure Coordinating Council funded chargers via $50M federal grant (aggregate, not per-bus) | Not found | Not found |
| Annual earnings/bus (reported, not a listed dimension but directly relevant) | Not found | Two conflicting figures: ~$6,000/yr (WRI) vs. up to $12,000/yr (MassCEC via Utility Dive) — both preserved, not resolved | Not found (real-cost-based, no fixed annual figure by design) | Two conflicting figures: ~$9,000/yr (WRI) vs. $12,000/summer (Utility Dive, state VPP program manager) — both preserved |
| Fleet operator | School board (direct utility-district relationship) | Highland Electric Fleets (third-party) | National Express (third-party); tech by Nuvve; buses by Lion Electric | Not found |
| Real-world demonstrated result | Not found | 1 bus discharged 10.78 MWh, earned $23,500 over 2 summers (2021-22) — implies ~$2,180/MWh effective rate | 5-bus pilot since 2018-19 school year; "revenues can exceed charging costs" but don't always cover V2G-specific equipment/degradation costs | GMP reports 50MW total storage access across all sources (buses + home batteries), not bus-specific |

### Gap-fill research, 2026-08-25, direct follow-up

Targeted searches to resolve specific gaps flagged in the table above.

**Dominion (VA) — battery ownership, more definitive; a distinct V2G-specific cost figure; the
program's actual strategic rationale found**:
- **Ownership language, two sources with a real, worth-preserving distinction**: Dominion's own page
  says the utility "will have the **option** to take ownership of the battery." A separate, secondary
  source (Raconteur) states more definitively: "Dominion Energy **will own** and be responsible for
  the upkeep of the batteries and the V2G infrastructure." Both preserved rather than collapsed to
  one — the official page is the more authoritative source but is itself hedged (an option, not a
  commitment), while the secondary source may be simplifying an option into a stated fact.
- **A distinct, separately-reported V2G infrastructure cost**: "a new $16-million V2G project" —
  distinct from the earlier-sourced $13.5M figure, which was specifically the cost of procuring the
  initial 50 buses themselves, not the V2G infrastructure layered on top. Both real, both preserved,
  not conflated.
- **The program's actual strategic rationale, found directly from a named Dominion executive (Dan
  Weekley, VP of Innovation Policy and Development)**: explicitly tied to Dominion's own 2.6 GW
  offshore wind integration needs (CVOW, already extensively documented elsewhere in this project) —
  "offshore wind will produce more electricity to the grid primarily in the evening, afternoon or
  night time; with this programme we can charge the electric vehicle batteries when those renewables
  produce energy and have the flexibility to use it when we need it." The buses are explicitly meant
  to absorb excess overnight/evening wind output and discharge it back during peak need — a real,
  substantive answer to "why this program exists," not previously captured.
- **Event duration/frequency for Dominion specifically: still not found** despite a targeted search —
  remains a genuine, disclosed gap, not filled with a guess.
- **A minor, worth-noting discrepancy on total VA school bus count**: this new search found "13,000"
  (Raconteur, citing Dominion's own innovation team); the previously-cited VDOE figure was "16,000."
  Both preserved — could reflect different count years or different definitions of "school bus."
- **Fairfax County case study detail** (WRI): the charging site itself is school-district-owned, not
  Dominion-owned — a real, useful ownership-structure data point. Also notes Fairfax's own early V2G
  routes were deliberately kept under 70 miles/day (vs. the 80-mile statewide average), plausibly a
  deliberate choice to preserve more battery headroom for V2G specifically on early pilot routes.

**La Plata Electric Association / Durango School District 9-R (CO) — now well-sourced enough to
add as a fifth full table entry**:

| | La Plata Electric Association / Durango SD 9-R (CO) |
|---|---|
| 1. Battery ownership | Not directly stated; grant-funded (see below), not utility-rate-funded |
| 2. Battery warranty compensation | Not found |
| 3. Battery replacement compensation | Not found |
| 4. Mechanism/event basis | True V2G dispatch, single-bus pilot (first in Colorado) |
| 5. Compensation for load reduced | N/A |
| 6. Compensation for energy dispatched | Not found as a $/kWh or $/kW rate — value instead framed as ~$5,000/yr in fuel-cost savings, though this appears to be primarily from running an electric bus at all rather than isolated V2G-discharge value specifically; the two should not be conflated |
| 7. WMA allowed | Not researched |
| 8. Event durations | 5-9pm daily (a direct, precise window — the most precise found for any program in this table) |
| 9. Charger capex/install/O&M | Funded via an Alt Fuels Colorado grant, itself sourced from the $68.7M Volkswagen Diesel Emissions Settlement; LPEA co-wrote the grant and donated additional funds — a genuinely different funding model than Dominion's rate-base approach |
| Hardware | Nuvve V2G DC 60kW charger (same vendor as Con Edison/White Plains — a real cross-program connection, not coincidental branding); Blue Bird bus (a third distinct manufacturer, alongside Dominion's Thomas Built and Con Edison's Lion Electric) |
| Battery size | 155 kWh (direct figure) — a third independent per-bus data point alongside Dominion's ~100kWh (derived) and SDG&E's 180kWh (direct), giving a real ~100-180kWh range across programs rather than one number |
| Scale | Single-bus pilot, not a multi-bus fleet like Dominion/Con Edison/others — a real scale difference worth keeping distinct from the larger programs |

**Cross-program pattern now visible with this addition**: Nuvve (La Plata, Con Edison) and Highland
Electric (National Grid) both appear as third-party technology/fleet vendors across multiple,
otherwise-unrelated utility programs — V2G implementation in this space is not being built
independently by each utility, but substantially through a small number of repeat technology/fleet
providers, itself a relevant structural observation for evaluating how replicable Dominion's own
program is versus dependent on Dominion's own specific vendor relationships (Thomas Built/Proterra).



**Category "Hybrid" (administratively framed as emergency load reduction, mechanically true discharge)**

| | SDG&E / Cajon Valley USD (CA) |
|---|---|
| 1. Battery ownership | Not found |
| 2. Battery warranty compensation | Not found |
| 3. Battery replacement compensation | Not found |
| 4. Mechanism/event basis | California's Emergency Load Reduction Program (ELRP) — demand reduction + energy dispatch, ~10 events/yr |
| 5. Compensation for load reduced | Not separately broken out from #6 |
| 6. Compensation for energy dispatched | $2/kWh cash, direct |
| 7. WMA allowed | Not researched |
| 8. Event durations | 1-5 hrs per event |
| 9. Charger capex/install/O&M | Not found |
| Hardware | 60kW bidirectional chargers; ~180kWh battery packs (a useful cross-check against Dominion's own ~100kWh implied figure) |

**Programs found but too thin to populate reliably, disclosed rather than omitted silently**:
- **La Plata Electric Association / Durango School District 9-R (CO)** — real, named, WRI-documented
  (including a real operational detail: "initial failures with its technology platform"), no
  compensation/ownership terms found.
- **Wells-Ogunquit School District (ME)** — real, but explicitly on hold: WRI reports the pilot
  paused specifically because compensation terms with the utility/regulator were never established
  — itself a relevant, documented failure mode, not just a research gap.
- **Eversource ConnectedSolutions+ (MA)** — a second Massachusetts utility, "in discussions with
  school districts," not yet live.

**Patterns worth naming directly, not just the raw cells**: (1) no program has a clean, sourced
answer on battery ownership or replacement funding except Dominion's — could reflect genuinely less
standardized practice elsewhere, or simply less public reporting; the two cannot be distinguished
from what was found. (2) Compensation philosophies are genuinely different in kind, not just
magnitude, across programs (in-kind vs. flat $/kW seasonal vs. flat $/kWh cash vs. market-linked
value stack) — a direct dollar comparison across programs would be somewhat apples-to-oranges
without normalizing for this first. (3) Every reported annual-earnings figure came with at least one
conflicting source (National Grid, GMP) — preserved as ranges, not resolved, since no basis was
found to adjudicate which is more current/accurate. (4) Independent third-party fleet operators
(Highland Electric, National Express) run several of these programs, not the school district
directly — a real structural variant from Dominion's own direct district-utility model.


**D.2 (extended) — Citizen (private) EV V2G**
*(newly identified, 2026-08-24; scoped and prioritized, 2026-08-26)*. Same supply-side discharge
mechanism as school bus V2G, a further asset class. Requires bidirectional-charging-capable
hardware, materially rarer than the standard one-way Level 2 equipment this project's existing EV
Charger Rewards data is built on (that entire dataset is curtailment-only, unidirectional) —
realistic near-term fleet size is likely much smaller than the curtailment-only EV population
already modeled.

**Direct user decision on WMA pathway, 2026-08-26**: Citizen EV V2G's own wholesale-market access
runs through Dominion's own VPP pilot specifically, not a generic FERC 2222 aggregator path modeled
from scratch. Confirmed against `Dominion_VPP_Pilot_Research.md`'s own already-sourced filing detail
(Company Exhibit, Witness CSY, Schedule 1, Dec. 2025 VPP Pilot petition): the **BYOD (Bring Your Own
Device) Aggregator Access Pilot** (program #5 in that filing's own official Appendix C numbering —
corrected 2026-08-27, see below) is explicitly device-agnostic —
"thermostats, batteries, EVs, behavioral measures" — the correct, real, already-identified pathway
for this item rather than a new one to research separately.

**A real, disclosed complication found while confirming this, not smoothed over — and corrected,
2026-08-27**: the same VPP filing lists a further, distinct EV-specific program beyond the BYOD
path and the already-quantified existing DLC program — "Residential Managed Charging Pilot for TOU
rate and non-TOU rate customers" (**program #9**, new under DSM-XIV, a single entry covering both
rate variants). This means the real landscape has at least three potentially-overlapping EV
participation paths (existing DLC, this new managed-charging program, plus BYOD/V2G), not a clean
two-way split. Per direct user instruction, this build treats it as the two-way exclusivity the
user specified (existing DLC vs. BYOD/V2G) — program #9 is flagged here as a real, unresolved third
wrinkle for future scoping, not silently folded into either side.

**Correction, 2026-08-27, direct user request**: this item and BYOD's own program number were
previously mislabeled ("#8/#9" as two separate entries; BYOD as "#11") — both traced to this
project's own earlier working file (`Dominion_VPP_Pilot_Research.md`) having used the VPP filing's
own informal Table 1 summary ordering (Section 4.3.3) rather than its official, numbered tariff
language (Appendix C, "III. Program Eligibility and Incentives"). Verified directly by fetching the
source PDF (https://cdn-dominionenergy-prd-001.azureedge.net/-/media/content/save-energy/global/
pdfs/virginia/vpp-pilot-young-testimoy-schedule-1.pdf) — Appendix C is authoritative: BYOD is #5;
Residential Managed Charging (both variants combined) is #9; #8 is a different, unrelated program
(Residential IAQ Battery Storage Pilot, Demand Response). `Dominion_VPP_Pilot_Research.md`'s own
table corrected to match.

**Direct answer to a follow-up question, 2026-08-27**: given this project's own focus is citizen EV
owners participating in WMA via a DERA, does program #9 (TOU-based Residential Managed Charging)
have any direct WMA/DERA application? **No.** Checked directly against the filing's own program
description: #9 is structured as a direct-with-Dominion enrollment and incentive program (same DSM
Rider C1A cost recovery as the existing DLC programs, #1-4), with no mention of aggregators or DERA
participation anywhere in its own eligibility or incentive language — structurally identical in
kind to the existing EV Charger Rewards program (#2), just with more sophisticated managed-charging
logic and telematics integration rather than simple pause/resume. The ONLY program in this filing
explicitly structured around aggregator/DERA participation is #5 (BYOD Aggregator Access Pilot) —
exactly the program `CitizenEVV2G` is already built on. This confirms the existing scoping decision
(CitizenEVV2G = BYOD/#5 specifically) was already correct, and #9 remains a genuinely separate,
third pathway — neither the existing DLC (#2) nor the BYOD/V2G path (#5) — consistent with the
"unresolved third wrinkle" framing already established, now with the correct program number.

**Direct user instruction on the resulting hybrid/exclusivity structure**: Citizen EV DLC (the
existing, already-quantified EV Charger Rewards program, #2 in the VPP filing's own table, ~3.51
kW/participant, $40/yr) and Citizen EV V2G (the new BYOD path) are **mutually exclusive** — a given
vehicle's capacity counts toward one program or the other, never both simultaneously. This mirrors
the same non-additive treatment already established for A.2-extended (Schedule 10/Distributed
Generation/PJM peak-shaving) and school-bus V2G's own WMA-vs-in-kind exclusivity finding.

**Real, disclosed gaps carried into the build, not guessed at**: the BYOD path's own compensation
rate is explicitly not published in the VPP filing ("pay-for-performance... exact rate NOT
disclosed") — the statutory tariff deadline is November 15, 2026, after this filing. The filing's
own Figure 7 shows 200 MW of BYOD-pathway capacity by 2030, but this figure spans the ENTIRE
device-agnostic BYOD category (thermostats, batteries, EVs together) — not an EV-specific figure,
and should not be treated as one.

**Coded, 2026-08-26**: `citizen_ev_v2g_analysis/citizen_ev_v2g_feature.py` (+ 16 tests, all passing)
implements `CitizenEVV2G` as a `WMAPathway` subclass — the research above (VPP/BYOD pathway,
mutual exclusivity, unpublished rate) was already complete but had never been built into code,
leaving the migration half-done (only the existing-DLC side, `EVChargerRewards`, had been
migrated). Real per-vehicle magnitude sourced directly rather than left unbuilt: the IEA's own
Global EV Outlook 2026 gives ~90 kWh as the current average US BEV pack capacity, cross-checked
against a second independent source giving the same figure. Available-for-discharge capacity
(~79.46 kWh, an 88.3% headroom) is derived by subtracting this project's own already-sourced daily
charging-energy-need figure (reused directly from `dlc_analysis/dlc_assumptions.py`'s own VMT/
efficiency chain, not re-derived) — with a direct, honest caveat in the code itself: this is an
upper-bound figure, not a conservative one, since it only nets out today's average energy need, not
a real-world safety margin against trip variability the way school bus V2G's own headroom (grounded
in an actual stated range vs. an actual fixed route) was. `current_compensation_usd()` correctly
returns `None`, not raises — this program's compensation is expected to be monetary
(pay-for-performance), just not yet published, the genuinely different case from school bus V2G's
own non-monetary in-kind compensation. Mutual exclusivity with `EVChargerRewards` is declared
explicitly in code (`MUTUALLY_EXCLUSIVE_WITH`), following the same convention already established
in `large_ci_curtailment_assumptions.py`, rather than left as prose alone.

**A real methodology question raised and resolved directly, 2026-08-27**: is the 90 kWh IEA figure
an unweighted average across available catalog models, or a sales-weighted average reflecting what's
actually purchased? Checked directly against the IEA's own stated methodology (Global EV Outlook
2026, Annex C): "battery deployment is calculated as the volume-weighted average battery size
multiplied by vehicle sales by mode and region" — confirmed sales-weighted, not a catalog average
skewed by low-volume luxury models. A further, sharper distinction was then raised: sales-weighted-
of-new-2025-sales is still not the same as an average of the existing on-road fleet, which includes
years of older, smaller-pack vehicles and would pull the true today-fleet average below 90 kWh.
**Resolved directly**: confirmed as the right figure anyway, given this project's own modeling
context — Scenario 3 projects EV sales as a *growing* share of total vehicle sales over time (2030/
2035/2045 checkpoints), not a static snapshot of today's existing fleet. The relevant population for
a forward-looking participant pool is increasingly dominated by newer vehicles as the fleet expands,
making the sales-weighted-of-new-vehicles figure the appropriate proxy for this project's own
growth-modeling frame specifically — a deliberate, reasoned match, not an unexamined default. No
numeric values changed; the module's own comments were updated to state this reasoning directly
(Rule 10) rather than leave the figure's own appropriateness implicit. 222/222 tests still pass,
confirming no regression from the documentation-only update.

### Cross-state residential EV incentive comparison, 2026-08-26, direct user request

NY, CA, MD, WA, and MA checked directly, addressing two genuinely different questions: (1) is
Dominion's own existing DLC rate low relative to peers, and (2) what does a real, live V2G/BYOD rate
look like elsewhere, since Dominion's own is still unpublished.

**Existing DLC-equivalent programs (rate-comparable to Dominion's own $40/yr flat)**:

| State/Utility | Program | Mechanism | Incentive |
|---|---|---|---|
| **Dominion (VA)** | EV Charger Rewards | Direct utility control (DLC) | **$40/yr flat** |
| NYSEG (NY) | OptimizEV | TOU rate-differential | ~$175/yr (directly calculated from a stated formula, not estimated) |
| RG&E (NY) | OptimizEV | TOU rate-differential | ~$142/yr |
| BGE (MD) | Off-peak charging incentive | TOU-conditioned flat annual | ~$50/yr flat — the closest structural match to Dominion's own design |
| CA (ChargePerks/Charge Smart, WeaveGrid-run, multi-utility) | Managed charging | TOU + bill-credit | Up to $600-700/yr (a ceiling, framed as "save up to," not a guaranteed average the way Dominion's flat rebate is) |
| Eversource (MA) | New Managed Charging (2026) | Off-peak charging % + override limit | $50 enrollment + $10/month (~$120/yr ongoing) — closely matches Dominion's own newer, not-yet-built #9 Managed Charging program specifically (corrected 2026-08-27, was "#8/#9"), not the older DLC program |

Every comparable program pays more than Dominion's existing $40/yr — BGE, the closest structural
match, still runs about 25% higher. This independently corroborates, via a second, different
program type, the same directional finding already established for large C&I (entry #82) and now
residential DLC specifically (this session, above): Dominion's existing incentive-based DR programs
consistently price below what comparable states pay.

**Real, live V2G-specific rates — directly useful given Dominion's own BYOD rate isn't published**:

| State/Utility | Program | Rate |
|---|---|---|
| **National Grid / Eversource (MA)** | ConnectedSolutions residential V2G (launched July 2026) | **$275/kW**, average performance over the summer season |

This is the single most directly useful benchmark found for the BYOD path specifically, since it's
a real, currently-live rate rather than a rebate ceiling or a differently-structured TOU discount.
For context (not as a substitute for Dominion's own eventual rate): $275/kW is roughly 24x
Dominion's own implied existing-DLC rate ($11.40/kW/yr, derived above) — though the two are not a
clean apples-to-apples comparison, since one is a live V2G discharge rate and the other is a
DLC-pause rate for a structurally different, less demanding form of participation.

**A real, cross-state pattern worth stating directly, not just a Virginia-specific gap**: residential
V2G specifically (as opposed to simple managed charging) is early-stage everywhere checked, not only
in Virginia. Maryland's own DRIVE Act V2G pilots (BGE/Pepco/Potomac Edison, 185.7 MW target) aren't
anticipated live until summer 2027. Massachusetts's own program launched only days before this
research (per the source's own July 23, 2026 date). Dominion's own BYOD rate remains unpublished.
This is useful context for how this module's own gaps should be read — not evidence Dominion is
unusually behind, but confirmation the entire residential-V2G market is genuinely nascent right now.

**A real, disclosed gap, not forced into a false comparison**: Washington does not appear to have an
ongoing managed-charging or V2G participation incentive comparable to the others checked — its own
programs are predominantly one-time charger-installation rebates ($300-$600) plus off-peak rate
design (Seattle City Light), not a direct payment for allowing utility control or discharge. Noted
as a real difference in program design across states, not a research gap.

### A real correction, EV-specific override research, and closing the T&D gap, 2026-08-26

**A direct user correction, confirmed and accepted, not defended**: the Wildstein/Craig/Vaishnav
override-discount citation used earlier this session (in the "properly-priced DLC incentive"
discussion above) was about **403 Ecobee smart thermostats** in SCE's 2019 program -- not EV
chargers at all. Citing it, even qualitatively, as support for an EV-charger capacity-value
discount was imprecise and should not have gone unflagged -- thermostat overrides (driven by
immediate comfort) and EV charger overrides (driven by range anxiety/trip-planning) are genuinely
different mechanisms, and the user's own hypothesis -- that longer EV ranges since 2023 should
plausibly reduce override behavior -- is a real, distinct question the thermostat study cannot
answer.

**Real, EV-specific override/participation research found, replacing the thermostat citation**:
- **Burlig, Bushnell, Rapson (working paper, April 2026, studying an actual current California
  utility's EV managed-charging program)** -- meets the user's own 2023+ window cleanly: "20 percent
  of households who opted into the program never granted access." A real, recent,
  chronic-non-participation figure specific to EV managed charging -- distinct from a per-event
  override rate, but a genuine, directly-relevant data point on how much of nominal enrollment
  translates to actual usable capacity.
- **A second study (residential PEV charging coordination pilot) is directly on-point
  mechanistically but predates the requested window** -- its arXiv submission date (Dec. 2021) is
  flagged directly rather than silently included as if it met the 2023+ criterion. Kept for its
  substantive value only: opt-in rate rises from ~10% (under 1hr of charging "slack" time) to ~80%
  (7-18hrs of slack) -- the clearest available mechanistic evidence for the user's own hypothesis
  (more buffer/flexibility, which longer range directly provides, sharply reduces override
  behavior) -- just not from the requested period.
- Separately, a Calgary/Alberta/Stanford field experiment (Bailey, Brown, Myers, Shaffer, Wolak,
  presented 2024) found qualitatively that "few EV owners subject to managed charging override the
  automation" -- directionally opposite the thermostat study's own 48% finding, though without a
  precise percentage located.

**The avoided-T&D gap, searched and found -- with a real, honest twist**: Dominion's own SCC-approved
standby charge (Case PUE-2011-00088) gives $2.79/kW distribution + $1.40/kW transmission = **$4.19/
kW total** -- genuinely Dominion-specific and SCC-vetted, though from 2011 (pre-dating essentially
everything else sourced this session) and framed as a standby charge, not a derived avoided-cost
incentive. **More importantly**: the SCC's own order in that same case states directly that "any
avoided cost benefits provided by customer-generators, at least in terms of the transmission and
distribution grid, are insufficient to pay for their proportionate share of the grid" -- the
regulator itself finding avoided T&D value from DG/DR is small, not large. Recomputing the full
three-component figure (capacity + energy/WMA + T&D) with this figure included showed T&D adding
only ~0.3-0.5% to the total. A newer (2026), potentially more relevant mechanism was also found --
Dominion's current 12CP transmission-cost-allocation methodology and an active $1.5B transmission-
cost case -- but this is specifically tied to large-load/data-center "direct-connect" infrastructure,
not something a residential DLC program meaningfully avoids; forcing it into a clean $/kW figure for
this purpose would be a real stretch, not attempted.

**T&D removed from the calculation entirely, direct user decision, 2026-08-26**: given how small
its own contribution turned out to be (~0.3-0.5% of the total) and the SCC's own direct finding that
avoided T&D value from DG/DR is not a meaningful value source, T&D is dropped from the "properly-
priced DLC incentive" calculation rather than carried forward for negligible precision gain. The
governing figure is now **capacity + energy/WMA only**:

**Utility margin changed from 5% to 0%, direct user decision, 2026-08-26**: the 5% figure was never
a sourced Dominion or SCC number — it was the user's own illustrative assumption for an earlier
hypothetical question ("if Dominion were to incentivize based on avoided capacity, avoided WMA, and
avoided T&D — a modest 5% utility margin..."). Once that assumption became the *default* behavior of
a shared, reusable code method (`shared_base_classes/demand_side_feature.py`), it risked being
quietly treated as an established methodological standard simply by virtue of being the code's own
default. Changed to 0% — not an assertion that the correct margin is zero, but that no margin figure
has actually been sourced, and an unverified default should not silently apply itself in real
comparisons. Every already-computed figure below is updated to reflect this directly, not left
stale:

| | Avoided cost (0% margin, unchanged from avoided cost itself) |
|---|---|
| Low (F-Class + Southill LMP) | **$803.98/kW-yr** |
| High (Aeroderivative + Tysons LMP) | **$1,311.29/kW-yr** |

Still ~71-115x Dominion's actual current rate ($11.40/kW-yr) — the direction and scale of the
finding is unchanged (removing an already-small, unsourced margin moved the range up modestly, from
$764-1,246 to $804-1,311, since 0% margin means no discount is applied at all), but the figure now
reflects only genuinely sourced inputs, not an illustrative assumption presented with more
confidence than it had earned. The $4.19/kW T&D figure and the SCC's own "insufficient to pay for
their proportionate share" finding remain on record above as real, sourced context, unaffected by
this change.

**Coded, 2026-08-26**: `dlc_analysis/dlc_assumptions.py` Step 7 (+ 12 new tests, 21 total in this
module, all passing) implements this calculation directly, following the same
avoided-cost-cross-check pattern already established in `large_ci_curtailment_analysis/`. Every
component is exposed as an overridable function parameter (Rule 8), T&D's exclusion is a named,
tested boolean in the output (`td_included: False`) rather than an undocumented omission, and the
energy component's own upper-bound status is similarly flagged in the output itself
(`energy_component_is_upper_bound: True`) so no downstream consumer of this function can miss it.
The existing Wildstein/thermostat citation error in this same module's own "Known Limitations" note
(Step 6) was also corrected in the same pass, for consistency with the working-notes correction
above.

**D.2 (extended) — Municipal transit bus V2G**
*(newly identified, 2026-08-24)*. **Held, 2026-08-26, direct user decision** — left as a note for
separate future investigation, not built this pass. Municipal transit buses have a genuinely
different duty cycle than school buses — continuous operation through the day rather than large idle
blocks, with the least idle time often falling during the same peak transit hours that overlap
grid-peak windows. A real, structural reason transit-bus V2G may have meaningfully less usable
capacity than school-bus V2G, not just a smaller fleet of the same opportunity — worth a dedicated
look when picked back up, not a quick extension of the school-bus module.

**D.3 Compensation structure** — **still open, explicitly deferred**
("we'll discuss"). Appendix E's "Recommended VA Program" proposal
(LSRV-style locational adder + Virginia's real D-REC price + NY
DRV-style event compensation) is the starting point, not yet
re-validated against this session's own tightened citation standards.
Related to A.2 (both involve ownership/compensation questions) but
confirmed as a genuinely separate discussion — consumption response
(A.2) and supply response (D.3) are mechanistically distinct even where
the same enrolled customers or DERA might eventually participate in both.

### 5.4 Category C — Land Use and Siting

Also not DSM — governs land accounting and offsite economics, not
dispatch.

**C.1 Siting types**: non-urban standard (8% of total) / non-urban
agrivoltaic (72% of total, i.e. 90% of the 80% non-urban share) /
rooftop (10%) / canopy (10%).

**C.2 Consequences**: agrivoltaic dual-use land accounting (open,
Appendix P #10) and farmer lease income (claimed complete in an
unverified source — see #3 above) / rooftop-canopy's zero-incremental-
land treatment (open, no decision yet).

### 5.5 Items still open within this taxonomy, not yet resolved

• **D.3 compensation structure** — ~~genuinely deferred by direct
  instruction, not an oversight~~ **resolved, 2026-09-02: adopted as
  this project's own design (see §0.4); the remaining open piece is
  re-running the adopted structure against this project's own
  hourly-LP methodology, not the structural choice itself**.
• **A.2 incentive-based DR** — confirmed in scope, mechanism and
  magnitude not yet specified.
• **Rooftop vs. canopy treatment within B.1.d/B.1.e** — this taxonomy
  currently treats both identically for market-access purposes (D.1);
  whether they warrant separate treatment for compensation (D.3) or
  capacity-factor purposes (#2) remains open.

### 5.6 White paper summary format

Four tables only, no sub-taxonomy discussion: A.3 (DSM elements), B.1/
B.2 (ownership and siting), D.1/D.2 (market access and response), C.1
(siting types) — full reasoning and sourcing stays in the appendix
(this section), cited from the white paper body rather than repeated
in it.

### 5.7 Second view of the same items — by customer-facing mechanism (EE / DLC / Price-Responsive / Other)

*Direct user request, 2026-08-24: "let's have both of the views in that
document." This is NOT a replacement for the A/B/C/D structure above —
the two are orthogonal lenses answering different questions. A/B/C/D
organizes by what changes in the model (demand input, static ownership,
dispatch behavior, land accounting). This view organizes by what the
customer or device actually experiences — useful for enrollment/
behavioral reasoning and, specifically, for judging how much estimation
risk (override rates, elasticity, event-window assumptions) an item
carries, the same lens used throughout this session's own "camel's
back" LP-complexity discussion.*

**Price-Responsive** splits into two subcategories rather than one,
because they produce measurably different real-world results, not just
different implementation styles — this project's own already-cited
research shows manual price response (Spain, 2015) achieved near-zero
effect while automated-system response achieves meaningfully more,
which DOE's own Grid-interactive Efficient Buildings (GEB) framework
treats as its own recognized distinction for the same reason.

**Price-Responsive → Automated** (algorithmic response to a price
signal, no real-time human in the loop):

| Item | Formal category |
|---|---|
| A.1 Day-ahead/RTP pricing (automated implementation) | A (price-based DR → automated in practice) |
| D.2 WMA / storage arbitrage | D (supply-side price response) |
| D.2 School bus V2G *(if price-triggered)* | D (supply-side, extended) |
| D.2 Citizen (private) EV V2G *(if price-triggered)* | D (supply-side, extended) |
| D.2 Municipal transit bus V2G *(if price-triggered)* | D (supply-side, extended) |
| A.7 Data center flexibility *(if price-based)* | A (mechanism TBD) |

**Price-Responsive → Manual** (customer directly watches and reacts to
a price signal):

| Item | Formal category |
|---|---|
| A.1 Day-ahead/RTP pricing (manual/unautomated implementation) | A (price-based DR) |

*A.1 appears in both Automated and Manual deliberately — the same
underlying program, two different implementation modes, with
materially different real-world effectiveness per the research cited
above.*

**EE** (permanent, equipment-based reduction):

| Item | Formal category |
|---|---|
| A.3 Heat pump efficiency / PHIUS | A (EE) |
| A.4 Heat pump water heaters | A (EE) |

**DLC** (utility/aggregator remotely cycles or curtails equipment):

| Item | Formal category |
|---|---|
| A.2 Smart thermostats | A (DLC) |
| A.2 EV charger control *(curtailment only, not V2G — see D.2 above)* | A (DLC) |
| A.2 Water Energy Rewards | A (DLC) |
| A.2 Large C&I interruptible | A (DLC) |
| A.7 Data center flexibility *(if incentive-based instead)* | A (mechanism TBD) |

**Other** (no price signal, no customer mechanism, or purely
structural):

| Item | Formal category |
|---|---|
| A.5 CVR | A (passive/automatic) |
| A.6 School thermal storage | A (on-site storage) |
| B Solar location allocation | B (static ownership) |
| C Land use/siting | C (land accounting) |

**Two items genuinely ambiguous across both tables above, not an
oversight**: A.7 (data center flexibility) and the three D.2 V2G items
appear under Automated with an "if price-triggered" qualifier because
their actual mechanism depends on a program-design decision this
project hasn't made yet — DLC-style direct curtailment/discharge is
equally plausible for all four. **C&I BEMS still has no clean single
row in either table** — it straddles DLC and Automated depending on
configuration (pre-cooling is Automated/price-responsive; hard
equipment cycling during a declared event is DLC-style) — treated as
its own explicitly hybrid case rather than forced into one bucket.

### Citations for this section

• Gellings, C.W. (1985), "The concept of demand-side management for
  electric utilities," *Proceedings of the IEEE* 73(10), 1468-1470 — the
  original source of the six load-shape objectives; the primary source
  the secondary discussions below ultimately trace back to.
• The five sources provided for the load-shape-objective tier
  (fsrglobal.org; *ScienceDirect* S2352484722005479; MDPI *Energies*
  15(8):2863; AEEE; *Clean Energy* 8(1):36) and the source for the
  original EE/DR/SLM split (IET *Generation, Transmission &
  Distribution*, gtd2.13204) — carried forward as provided, not
  independently re-verified this session.
• The three sources provided under Energy Efficiency, and the five
  under Demand Response — same status, carried forward as provided.
• DOE, "A National Roadmap for Grid-interactive Efficient Buildings"
  (2021) — source for the automated EE/DR hybrid category's framing.
• Fabra, N. et al., "The Real-Time Price Elasticity of Electricity"
  (Spain RTP study) — already cited in Scenario3_Technical_Notes.md #2;
  cross-referenced as the basis for the hybrid category's reasoning.
• Dominion Energy, "RPS | Virginia" (Rider RPS/CE/PPA structure) —
  http://www.dominionenergy.com/en/Virginia/Rates-and-Tariffs/RPS
• Virginia SCC, "RECs" (bundled-vs-unbundled REC treatment) —
  https://www.scc.virginia.gov/regulated-industries/utility-regulation/energy-regulation/renewable-resources/recs/
• Fairfax County Office of Environmental and Energy Coordination,
  "Fairfax County's Plan to Go Green: How Virtual Power Purchase
  Agreements Could Help" (Arlington/Dominion REC example) —
  https://www.fairfaxcounty.gov/environment-energy-coordination/climate-matters/virtual-power-purchase-agreements
• Stoel Rives LLP, "Utility-Scale Solar Power Purchase Agreements," *The
  Law of Solar Guide* (physical vs. virtual/CFD PPA distinction) —
  https://www.stoel.com/insights/reports/the-law-of-solar/power-purchase-agreements-utility-scale-projects
• Dominion Energy, "Net Metering | Virginia" (distributed-owner PJM
  market-sale option) —
  https://www.dominionenergy.com/virginia/renewable-energy-programs/net-metering
• WattBuild, "How does an SREC save me money in Virginia?" (residential
  PPA/SREC ownership) — https://www.wattbuild.com/learn/about/14/srec-virginia

## 6. Multi-state literature search — locational DER rates and DSM/DER program breadth (this session)

*(Direct follow-up to the #5/#6 discussion below — commissioned specifically to inform how
distributed storage dispatch and DER-owner arbitrage should be structured, given several states
have already built and tested real compensation mechanisms for exactly this question. Checked the
project's own knowledge base first — it holds the NSPM's own generic BCA framework and citations to
these states' own source documents, but not their actual content — so this section is built from
direct web research, not the knowledge base.)*

### 6.1 New York — the most directly relevant precedent, already named/scoped

**VDER "Value Stack"**, five components: Energy Value (zonal, hourly day-ahead LBMP), Capacity
Value (ICAP, tied to NYISO's own capacity auction, three payout alternatives), Environmental Value
(fixed REC-style payment, 25-year lock), **Demand Reduction Value (DRV)** — based on utility-specific
Marginal Cost of Service studies, paid for performance during a pre-set peaking window (~300 hours
of summer evenings, 2-7pm) — and **Locational System Relief Value (LSRV)** — a locational adder
available only at utility-designated, congested substations, both DRV and LSRV locking in for 10
years once a project qualifies. This is the direct origin of the LSRV/DRV terms raised earlier this
session.

**Quantified rate, and a direct match to this project's own siting assumption** (from a parallel
session's own follow-up research, not independently re-verified here): LSRV currently runs
$2.56-3.07/kW-month (~$31-37/kW-year) on top of energy and capacity value. This maps closely onto
Scenario 3's own, already-established assumption (§2) that 90% of rooftop/parking-lot DG sits "in
or near urban or suburban high-demand areas" — precisely the siting profile NY's own LSRV zones are
built around. A usable, directly-sourced quantitative benchmark for this project's own locational-
payment layer, not just a structural analogy.

**Also flagged (parallel-session finding)**: under VDER, storage capacity value is not ELCC-derated
at all. Noted here as external context from a different conversation, not reconciled against this
project's own capacity treatment — this project's own model doesn't have a directly comparable ELCC-
style derating mechanism on record to compare it against, so the NY comparison point doesn't carry
forward into this project's own methodology.

**Directly relevant, current finding**: as of April 2026, both DRV and LSRV are under active PSC
review (Case 15-E-0751) because the rates are "nearly a decade out of date" — a live illustration of
the general risk any locked-in, long-duration locational rate carries as system conditions evolve.

### 6.2 California — the broadest, most mature framework; conceptually similar to NY but less generous to individual owners in practice

**Avoided Cost Calculator (ACC)**, E3's own methodology, adopted 2005, updated biennially (2026
update cycle already underway) — generation energy, generation capacity, ancillary services, T&D
capacity, decarbonization compliance. **Locational Net Benefits Analysis (LNBA)**, developed since
2015 by the state's three IOUs with CPUC oversight, a more granular, feeder-level companion to the
ACC. **Distribution Investment Deferral Framework (DIDF)**: PG&E/SCE/SDG&E competitively procure
DER specifically to defer identified capital projects — the same underlying locational-deferral
concept as NY's own LSRV, structurally different in how it reaches individual owners (see below).
**Distribution Resources Planning (DRP)**, required under CA Public Utilities Code §769 — utilities
must identify optimal DER siting locations.

**An important distinction, not fully captured in this document's own first pass**: California has
the same conceptual machinery as New York, but that locational/deferral value mostly flows through
utility-side competitive procurement (DIDF), not automatic per-project payment the way NY's own
LSRV does. For an individual rooftop or small C&I owner specifically, the actual compensation
mechanism is NEM 3.0's own avoided-cost export rate (~$0.05-0.08/kWh) — *lower* than the prior,
retail-rate-based NEM 2.0, not higher. California prices this value conceptually and uses it at the
utility-procurement level, but does not hand it directly to small owners the way New York's own
Value Stack does. Worth keeping this distinction explicit if Scenario 3 draws on California as a
model — the mechanism exists, but the individual-owner payment pathway it implies is genuinely
different from New York's.

**Directly relevant, very recent development**: E3's own July 2026 "LVDER" (Local Value of DER)
whitepaper proposes a two-tier compensation structure — "a modest system-wide credit to every DER
for broad load reduction and a targeted locational payment only where a resource can demonstrably
defer an identified investment" — explicitly the same broad-vs-targeted-locational shape as NY's
own DRV/LSRV split, and directly analogous to the two-stage structure already sketched for this
project's own Scenario 3 (system-wide credit / arbitrage layer, plus a targeted locational layer
where a resource demonstrably relieves a specific constraint).

### 6.3 Massachusetts — the simplest mechanism, and the most directly translatable into this project's own model

**SMART (Solar Massachusetts Renewable Target)**, a feed-in-tariff-style program since 2018, now on
"SMART 3.0" (2026 revision): fixed per-kWh incentive (Base Compensation Rate minus Value of Energy),
10 years (residential) / 20 years (commercial). **Location-based adders**: projects sited on a
building, brownfield, landfill, canopy, or active agricultural operation receive additional,
explicitly differentiated compensation — direct precedent for treating rooftop and canopy solar
differently by siting type (open item #3 on this document's own list), including a
canopy/parking-lot-specific adder and a storage adder (+$0.04/kWh) that map one-for-one onto this
project's own segments. **Greenfield subtractor**: ground-mounted projects on undeveloped land
without a locational adder receive a compensation *penalty* ($0.06/kWh flat plus $0.04/acre) — a
genuinely different design choice (discouraging greenfield development directly, rather than only
rewarding preferred siting) worth weighing against this project's own agrivoltaic-acreage question
(item #8).

**Of the three most-developed frameworks (NY/CA/MA), this is the most directly translatable into
this project's own model as-is** — SMART's own adders are sized per technology/siting-type
(building, canopy, storage) rather than requiring a locational-deferral study or a utility
procurement process to determine the payment, matching this project's own segment structure
(rooftop, canopy, storage-paired) without needing an intermediate translation step the way NY's
substation-specific LSRV or CA's DIDF procurement value would.

**Directly relevant, active 2026 development**: the Massachusetts Senate is considering a DER peak-
reduction mandate that would move compensation "away from subsidized equipment and toward a
market-based model where DERs are compensated for the specific locational and temporal value they
provide to the grid" — the same directional shift NY and CA have already made.

### 6.4 Maryland — a formally codified locational-value planning requirement

**COMAR 20.50.15** (Electric System Planning) formally defines "locational value assessment" in
regulation — "a process that provides price signals based on the benefits and costs of deploying
distributed energy resources in a specific location and over time" — and requires each electric
company's own annual Electric System Plan to "provide locational value for each identified electric
system constraint." Structured as a planning-disclosure requirement rather than a direct
compensation tariff (unlike NY's VDER), but the same underlying concept, codified.

**DRIVE Act (2024)**: EV/storage/VPP integration, time-of-use pricing, vehicle-to-grid — directly
relevant to Scenario 3's own DER-orchestration question. **2025 legislative package**: a "robust
program for the procurement of energy storage devices for front-of-the-meter transmission energy
storage and distribution-connected front-of-the-meter energy storage" — directly on-point for the
distributed-storage sizing/ownership question (item #5). **Resilient Maryland Program (FY26)**: $13M
specifically for solar-canopy-plus-battery-storage systems at critical infrastructure — a direct,
funded precedent for the canopy-plus-storage pairing this project's own Scenario 3(b) already scopes.

### 6.5 Washington — a genuinely simpler, less granular counter-example, worth noting as a contrast

**RCW 19.280.100**: requires utilities to identify data gaps and propose "cost-effective... tariffs
to fairly compensate customers for the actual monetizable value of their distributed energy
resources" — a broad planning mandate, not yet a built tariff. **Value of Solar and Storage (VOSS)
study**, led by the Washington State Academy of Sciences, due 2026, meant to inform a successor to
the state's existing net-metering tariff. **CETA** (Clean Energy Transformation Act) — carbon-free
electricity by 2030/carbon-neutral by (structurally the closest parallel among these five states to
Virginia's own VCEA), requiring utilities to file Clean Energy Implementation Plans (CEIPs) every
four years with specific EE/DR/renewables targets. **Distributed Energy Storage & Resiliency Act**
(SB 5727/SB 6008, pending as of this research, not yet enacted): would create a residential battery
incentive program and require large utilities to implement VPP/flexible-demand programs by January
2027.

**A genuinely useful counter-example, not just another precedent**: Washington's own existing
Societal Cost Test "only includes greenhouse gases (methane and carbon) and a flat value for air
quality benefits from displacing gas generation (with no locational nor temporal component)" — the
simplest of the five frameworks reviewed, worth keeping as a lower bound on complexity when deciding
how granular Scenario 3's own locational treatment needs to be. Not every jurisdiction has concluded
that NY/CA-style locational granularity is worth the added complexity.

### 6.6 Synthesis, directly bearing on the #5/#6 structural question

All five states that have moved past a purely planning-level mandate (NY, CA, and — via the pending
2026 legislation — MA and WA) converge on the same basic shape: a **broad, system-wide/energy-value
layer** (arbitrage against a real price signal, available everywhere) **plus a separate, targeted
locational layer** (available only where a resource demonstrably relieves an identified constraint,
priced and administered separately from the broad layer). None of the five states fold locational
value into the base energy-arbitrage price itself — it is consistently a distinct, additive
component. This directly supports the two-stage structure already proposed for this project's own
Scenario 3 (independent, price-taking DER-owner arbitrage dispatch first, then a separate,
centrally-administered locational-relief layer) rather than trying to build one, unified price
signal that captures both — no reviewed state does that, and the consistency across five
independently-developed frameworks is itself evidence this split reflects something structurally
necessary, not just administrative convenience.

Two design choices worth deciding explicitly, now that real precedent exists for each side:
**MA's location-based adders (rewarding preferred siting) vs. its own greenfield subtractor
(penalizing non-preferred siting)** are two different mechanisms for the same underlying goal, not
redundant — this project's own agrivoltaic/rooftop/canopy siting question (items #3, #8) could
reasonably adopt either, or both. **WA's own, deliberately simpler Societal Cost Test** is a genuine
reminder that full locational/temporal granularity is a choice, not a requirement — worth stating
explicitly if Scenario 3 ultimately adopts a simpler treatment than NY/CA's own, most granular
examples, rather than defending it as a limitation.

**A practical recommendation, given how the three most-developed frameworks now compare directly**:
New York and Massachusetts each give this project something the other doesn't. NY's LSRV supplies a
quantified, directly-sourced *rate* ($31-37/kW-year) for the targeted locational layer, and its
underlying siting logic (congested urban/suburban substations) matches Scenario 3's own 90%-
urban/suburban assumption closely enough to use as a starting benchmark rather than build from
scratch. Massachusetts supplies the more directly translatable *mechanism* — adders sized per
siting-type/technology, matching this project's own rooftop/canopy/storage segments one-for-one,
without needing an intermediate substation- or feeder-level study the way NY's LSRV or CA's DIDF
would require. California's own experience is the clearest cautionary note: the conceptual machinery
existing does not guarantee individual owners are actually paid more for it — worth keeping in mind
if Scenario 3's own compensation design ends up more DIDF-like (utility-procured) than VDER-like
(automatic per-project payment).

## 7. Dominion-specific programs, market-defensibility framework, and DLC/reliability literature (from a parallel session)

*(Preserved here for its conceptual/methodological content, not its dollar figures — that prior
session's specific SLCOE/Tier 1/2/3 numbers predate this session's extensive corrections and should
not be treated as current. The DER mechanisms, market-defensibility reasoning, and DLC-vs-price-
signal research below are independent of those figures and remain directly usable.)*

### 7.1 Dominion's own, real, in-territory programs — two anchors more conservative than any out-of-state benchmark

**Peak Time Rebate**: $1.25/kWh saved during peak demand events, real and current today — directly
the load-reduction mechanism (smart thermostats, C&I BEMS) this project's own Scenario 3 discussion
has been describing. One real gap: it's a flat rate regardless of event severity — Dominion doesn't
currently pay more during a Winter Storm Fern-level event than an ordinary summer peak afternoon,
unlike the "prices compound during coincident stress" dynamic the hourly coincidence work below
establishes empirically.

**EV charger managed-charging program**: $40/year flat incentive (plus signup bonus) for allowing
Dominion to cycle a customer's EV charger during peak periods — literally Direct Load Control by
FERC's own definition (§7.5 below), not a price signal. For a typical 7-11kW charger, this works out
to roughly $3.60-5.70/kW-yr — 40-70x smaller than the $250/kW-yr ConnectedSolutions-style ceiling
used as an aggressive upper bound elsewhere in this research. A second real Dominion anchor
(alongside PTR) suggesting the utility's own current practice sits far below out-of-state maximum
benchmarks, for reasons not yet distinguishable from the rate alone (genuinely lower avoided cost,
conservative program design, or under-investment).

**VPP battery pilot**: confirmed moving through the regulatory pipeline (Community Energy Act
mandate, filed with the SCC December 2025) — actual dollar rate not yet public, due in a separate
tariff filing November 2026. No current Dominion-specific storage rate exists yet; any storage-side
benchmark currently requires an out-of-state proxy.

### 7.2 Cross-state maximum composite and the market-defensibility framework

A five-category cross-state comparison (NY/CA/MA/MD, maximum value in each) was built as a
deliberate ceiling case — "start from the maximum, then moderate down" — surfacing several real
decision points before that composite means anything: **the energy-value line dominates every other
adder combined** and isn't really comparable to the rest (importing MD's full-retail net-metering
rate would mean adopting NEM 2.0-style retail crediting in Virginia, a much larger policy choice than
any single adder — flagged for later consideration, not adopted); **DRV, ConnectedSolutions, and
Dominion's PTR all measure the same underlying thing** (compensation for delivering/reducing load
during system stress) and stacking their maximums together would double- or triple-count; **units
don't match across programs** ($/kWh-in-a-window vs. $/kW-year flat vs. $/kW-summer-average-
performance) and converting between them requires an actual load/timing profile, not just picking
the biggest number.

**Market-defensibility tiering** (a genuinely rigorous pass at "which of these would a free-market
critique actually survive," built specifically to anticipate the fair critique that some DER
compensation designs subsidize owners rather than reflect market-responsive signals):

| Component | Market-defensible? | Reasoning |
|---|---|---|
| Energy value | Yes, cleanly | Approximates real wholesale price for energy delivered — the free-market critique would target precision (flat average vs. real zonal LMP), not the underlying principle |
| Capacity value, at actual PJM ELCC (not undiminished) | Yes | Paying more than a resource's PJM-measured ELCC means paying for reliability capacity that, by the market's own accreditation process, doesn't exist — the textbook shape of a subsidy |
| Locational/distribution-deferral value (LSRV-style) | Conditionally | Sound logic in principle — pay X to defer a $Y utility investment where X<Y is the same cost-effectiveness test justifying any demand-side alternative to a supply-side investment — but an imported out-of-state rate hasn't proven X<Y for a specific Dominion constraint; the fix is a real Virginia-specific avoided-cost study, not a conceptual objection |
| Environmental/REC value | Genuinely contested | A real, competitively-traded market price (not set by fiat) — but the demand side only exists because of a legislative RPS mandate; "market-driven" in the narrow price-discovery sense, not in the deeper sense of reflecting voluntary economic demand |
| Event-based value (ConnectedSolutions-style flat rate) | Least defensible | An administratively-set rate calibrated to drive adoption, not benchmarked against a demonstrated avoided cost (e.g., peaker-capacity cost) — funded across the full ratepayer base regardless of participation, the structural shape of a subsidy |

**Directly useful for this project's own item #9 (locational value credit)**: this tiering gives a
ready-made framework for defending — or explicitly flagging as a subsidy — whatever compensation
design Scenario 3 ultimately adopts, rather than presenting a single blended number without that
distinction.

### 7.3 Virginia's own, real Distributed REC (D-REC) market — no Code change needed for basic eligibility

Virginia already operates a real, live, tradable REC market under the VCEA's own RPS statute (Va.
Code §56-585.5), tracked through PJM-EIS GATS (the same system NY/NJ/PA/MD/DE use), with a specific
carve-out for exactly this project's own rooftop/parking-lot segment: **Distributed REC (D-REC)** —
behind-the-meter solar under 1 MW. **Just substantially expanded in the 2026 legislative session**
(HB628): the mandatory BTM D-REC carve-out rose from 1% to 4.5% of total retail electric sales for
2026-2030, stepping to 5% for 2031 onward — a 4.5x expansion of Dominion's own annual D-REC demand
(roughly 740,000 to 3.4 million SRECs/year).

Current SACP (price ceiling): $57.13 (2026). **Actual traded price** (Flett Exchange, live 2026
spot): $22.25/REC — the defensible current-law figure, not the ceiling. Market analysis projects a
rise toward $65-70/REC before the end of the 2026 compliance period as HB628's demand expansion
works fully through the market (a forward-looking estimate, not a locked-in number). A 75%
Virginia-siting requirement (as of 2025) on Dominion's general RPS RECs creates a real premium for
in-state-generated RECs specifically, directly benefiting a Virginia-sited rooftop/parking-lot
fleet. REC lifetime is 5 years (a certificate-validity window, not a cap on ongoing annual
generation/registration).

**No Virginia Code update is needed to make an SREC-equivalent instrument available** — it already
exists, is already tradable today via existing platforms, and was just strengthened by the General
Assembly itself. A live open question (not yet decided) is whether this project wants to go further
and propose Virginia adopt something closer to New York's fixed, 25-year-guaranteed E-Value
tariff — that would be a genuine, substantive Code-change proposal, not a modeling assumption, and
is a decision still on the table rather than made.

### 7.4 DRV / ConnectedSolutions / Dominion PTR — quantified on a common basis using real DOM-zone data

Resolving which of the three "same underlying thing" programs (§7.2) actually returns the most
revenue required converting all three onto a common $/kW-year basis using real Dominion-zone hourly
load data, not qualitative comparison. The key structural finding, more important than which number
is biggest: **ConnectedSolutions-style compensation pays a flat rate on average kW performance
across events, completely independent of energy actually delivered or discharge duration**; DRV and
PTR pay per kWh delivered within a window, so they scale with battery duration. Since this project's
own storage mix is long-duration (sodium-ion, iron-air), not a simple 4-hour reference battery, the
"winner" depends materially on duration assumptions, not a fixed ranking.

**A data-completeness correction worth carrying forward as a general caution**: an initial DRV
estimate, built from a data window that turned out to be missing roughly half of the June24-
September15 qualifying period, was roughly half the corrected figure once a fuller year of data
closed the gap — a reminder to check window completeness against the program's own stated eligibility
period before trusting a derived rate, not just whether the underlying data source loaded
successfully.

**A genuinely strong, independently-replicated finding**: Dominion's own real top-20 peak-demand
days, checked across two separate years of actual DOM-zone data, split exactly 10 winter / 10 summer
both times — not a marginal winter contribution, a real 50/50 split, with the actual dates
interleaving directly (summer 2026 heat-wave days alongside January 2025's own annual peak and the
Winter Storm Fern period). A concrete, twice-replicated, data-grounded reason not to import
Massachusetts's summer-only (June-September) ConnectedSolutions design into a Virginia-specific
program uncritically — a directly-relevant caution for Scenario 3's own market-participation design
(item #6).

### 7.5 Direct Load Control vs. price-based signals — a formally established distinction, not this project's own framing

FERC's own official demand-response taxonomy splits this exactly: **Direct Load Control (DLC)** —
"the program sponsor remotely shuts down or cycles a customer's electrical equipment... on short
notice" (Dominion's EV charger program, §7.1, is DLC by this definition) — versus **price-based
rate/tariff** — "terms and conditions under which customers can choose their energy consumption
pattern based on price." This directly bears on Scenario 3's own retail day-ahead/real-time rate
design (part d of the scenario's own definition) — that design is squarely a price-signal mechanism,
and the literature below is directly relevant to its expected reliability performance relative to a
DLC alternative.

**Why price signals can underperform, not just "be weaker" — a documented failure mode, not just
theoretical risk**: a 2026 paper on stochastic price-response modeling found that "inadequately
designed price signals can inadvertently cause adverse effects, such as load synchronization or
system instability" — if many customers respond to the same signal the same way, ending an event can
create a new demand spike immediately afterward (e.g., every smart thermostat or EV charger resuming
the instant an event ends), a failure mode DLC avoids by staggering resumption centrally.

**Even DLC isn't fully guaranteed**: Wildstein, Craig & Vaishnav (cited within Miri & McPherson,
below) found participant overrides can halve the reliability value of DLC programs.

**Miri & McPherson** (Alberta power system, SSRN abstract-level access only — full text paywalled):
both price-signal and DLC programs deliver real, comparable flexibility value (up to 580 MWh/year
improved wind integration, ~1.4% operational cost reduction, 7.7% avoided wind curtailment) — but
"these improvements are only achieved fully when sufficient flexible load is provided."

**A concrete, real-world illustration, not a hypothetical**: the July 2-3, 2026 PJM all-time peak
(168,158 MW) came within, in Dominion's own words, "minutes" of forcing every Ashburn-corridor data
center onto backup diesel generation — avoided via PJM's emergency demand-response program (a DLC
mechanism, not a price signal) pulling 6,000+ MW off-grid, not through voluntary price response.
Making that "guaranteed" curtailment work required suspending EPA air-quality permit limits so
backup diesel generators could run beyond normal legal limits (~3.25 GW from units operating outside
permits) — the real cost structure of DLC-based reliability isn't zero, it substitutes a visible
market payment for an externalized, uncompensated local health cost (quantified in §7.6).

### 7.6 A three-category grid-stress risk taxonomy, and the quantified externality cost of DLC-with-backup-generation

Hourly (not daily) coincidence analysis of real DOM-zone load against solar/wind capacity factors
found day-level aggregation hides a genuine artifact — a "max daily stress" metric ends up dominated
by ordinary nighttime physics (solar always zero after dark) rather than capturing genuine anomalous
scarcity. At hourly, season-split resolution: winter's average peak hour (7am) shows high average
wind (0.696 CF) but 12.2% of hours still show near-zero wind; summer's peak hour (5-7pm) shows
moderate average wind (0.39 CF) but 37.7% of hours show near-zero wind — three times more often than
winter on raw frequency. But the severe, coincident events (top-20%-load AND wind<0.20 simultaneously)
still cluster in winter and independently re-derive the same Winter Storm Fern period from a
completely different analytical angle (load-wind coincidence, not load alone) — a genuinely strong
validation.

**Combined solar+wind drought analysis surfaced a counter-intuitive finding**: winter has the
*lowest* combined-drought frequency (11.6%) of any season in the two-year record, not the highest —
fall has the highest (15.7%), with 7 of the top 10 longest drought streaks landing in late October/
November ("November doldrums," a recognized meteorological pattern of stagnant high-pressure
transitional-season weather suppressing both wind and solar simultaneously), running 14-16 hours
straight and recurring on nearly the same calendar window across both years of data (a real
recurring pattern, not noise). But these fall droughts coincide with only moderate load — well below
winter's demand extremes. **Duration-of-drought and magnitude-of-coincident-load are two separate
risk dimensions that peak in different seasons** — worth treating as two distinct stress tests, not
one "worst season."

**Winter Storm Elliott (December 2022)**, researched as a comparison case to the 2016-17 hourly LP's
own reference weather years: PJM-wide peak ~135,000 MW; generator outages reached ~46,000 MW (~25%
of installed capacity), 70% of which were natural gas units failing from extreme cold and gas-supply
constraints — genuinely different from a renewable-output drought, since extreme cold fronts are
often accompanied by strong wind, not calm conditions. PJM avoided firm-load shedding (unlike TVA
and Duke Energy Carolinas, which had actual rolling blackouts) via emergency tools, again including
a DOE order authorizing generators to exceed environmental permit limits — the same mechanism as
Ashburn, applied at grid-scale. ~$1.8B in Non-Performance Charges resulted under PJM's post-2014
Capacity Performance rules.

**A three-category risk taxonomy, worth carrying into Scenario 3's own reliability framing**: (1)
renewable-output drought (2016-17-style, the hourly LP's own existing stress test), (2) demand-spike-
plus-thermal-failure (Elliott-style, cold weather knocking out gas plants regardless of wind/solar
availability), (3) transmission/local congestion under extreme demand (Fern-style, the Ashburn near-
miss). A resource-adequacy approach that only guards against category (1) — which is what this
project's own hourly LP currently does — would offer limited protection against an Elliott-style
event, since more solar+storage doesn't fix gas plants freezing.

**Quantified externality cost of DLC-with-backup-generation** (Ashburn-style diesel gensets
specifically, not this project's own CCGT gas fleet — a distinct technology requiring its own,
separately-sourced emission factors, not a reuse of the diesel figures): approximately $213-253/MWh
all-in (CO2 ~$99/MWh at $190/ton; NOx $41-79/MWh; PM2.5 ~$70/MWh at $350,000/ton; SO2 ~$3-5/MWh) —
roughly 5x this project's typical energy-price assumption, comparable to Winter Storm Fern's own
peak wholesale price spike. The core point: "guaranteed" DLC-plus-backup-generator reliability isn't
actually cheaper than a market-price alternative once its full cost is counted — it moves cost from
a visible wholesale bill to an invisible, uncompensated local health and climate externality. A
California grid-disruption health-cost study specifically warns that episodic/single-event modeling
(a few hours during one event) understates health impacts by roughly an order of magnitude relative
to sustained, recurring exposure — relevant given Virginia's own data-center-driven load trajectory
suggests these events are more likely to recur than remain one-off.

Both the SC-GHG figure ($190/ton, EPA Dec 2023, peer-reviewed) and the criteria-pollutant Benefit-
per-Ton figures used here are, as of this research, politically contested at the federal level (EO
14154 withdrew the IWG's SC-GHG estimates from official policy status in 2025; a 2026 EPA economic
analysis challenged the co-benefits methodology behind the PM2.5/ozone figures, with direct pushback
from RFF) — worth flagging as the most rigorous available numbers, not as settled, uncontested
federal policy.

### 7.7 PJM's own pricing mechanism, and validation of this project's existing DOM-zone choice

PJM's real Operating Reserve Demand Curve (ORDC) — which sets scarcity/shortage pricing, penalty
factors reaching $850/MWh on the first step, LMPs able to reach the $2,000/MWh offer cap plus
penalties during genuine shortage — is explicitly built using "24 fixed ORDCs for six daily time
blocks across four seasons based on empirical distributions of historical uncertainties in load,
wind, solar, forced outages, and net interchange." **This project's own load÷clean-generation-
availability stress-signal work is not a novel construct being brought to PJM's market — PJM's own
price-formation methodology already embeds materially the same logic**, calibrated on the joint
distribution of load and clean-generation availability by season and time-of-day. A genuinely
validating finding for the overall analytical approach, not just a side note. (A more granular
academic proposal — a "dynamic ORDC" conditioning generator forced-outage probability on ambient
temperature rather than static seasonal blocks — found that added precision sharpens prices during
genuine scarcity but has minimal effect on total market payments in aggregate; better precision
changes *when* money flows, not *how much* flows overall.)

**DOM zone validated as the right pricing signal, not a placeholder needing replacement**: DOM has
priced above the PJM-RTO average every year 2021-2025, with the gap structurally widening (driven by
the same data-center load growth this project's own demand work is built around) — running ~40%
above the RTO-wide average as of the most recent data, and, notably, DOM's premium over the RTO
average did not close when PJM-wide prices corrected after the 2022 Ukraine/LNG shock elsewhere — it
kept widening. A more granular option exists if ever needed (PJM prices over 10,000 individual
nodes; "data center alley" specifically is a persistent, well-understood congestion hotspot distinct
from the DOM zonal average, with basis differences described as "tens of dollars per MWh routinely,
hundreds during constraint events") — but DOM-zone remains the right zonal-level choice for this
project's own purposes, not a simplification to correct.

### 7.8 Levelised Cost of Demand Response (LCODR) — citation and methodological limitations

**Citation**: Thrän, J., Green, T.C., & Shorten, R. (2025). "Levelised Cost of Demand Response:
Estimating the Cost-Competitiveness of Flexible Demand." *Energy Conversion and Management*
(Elsevier). https://www.sciencedirect.com/science/article/pii/S0196890425013354. Preprint: arXiv:
2502.03124 (submitted Feb 5, 2025; revised Dec 5, 2025). Authors affiliated with Imperial College
London (Dept. of Electrical and Electronic Engineering; Dyson School of Design Engineering). Journal
identity confirmed via PII prefix matching Energy Conversion and Management's ISSN (0196-8904) and
the journal's own Elsevier attribution in the arXiv HTML metadata — volume/issue/page/DOI not
confirmed via search, would need direct verification for a formal citation.

**Four methodological limitations worth weighing before drawing on this framework**:

1. Consumer compensation is modeled from stated-choice survey literature (what respondents *say*
   they'd need to be paid), not observed/revealed program payout data — a well-known source of
   systematic bias in behavioral economics, meaning LCODR figures could diverge meaningfully from
   what real programs like ConnectedSolutions or Dominion's PTR actually pay.
2. A static, single-year (2025) snapshot; the paper's own authors note storage technology costs are
   expected to keep declining as deployment scales, while DR's main cost driver (consumer
   remuneration) has no comparable, predictable decline path — any DR-vs-storage competitiveness
   conclusion from this paper has a limited shelf life, already probably somewhat stale.
3. Narrow scheme coverage — only four DLC schemes (V2G, smart charging, smart heat pumps, heat pumps
   with thermal storage) — none of which map onto LSRV, DRV, ConnectedSolutions, or Dominion's PTR,
   the actual programs this project's own research has focused on; the paper's own findings answer a
   related but different question.
4. A conceptual limitation of any "levelized cost" treatment of demand response generally, not
   specific to this paper's execution: LCOE/LCOS-style metrics work well for supply resources because
   a MWh of generation is roughly fungible across hours; DR's value proposition is the opposite — it
   is specifically valuable *because of* when and where it's available relative to system stress,
   exactly the point of the hourly coincidence and risk-taxonomy work in §7.6. The paper adapts a
   "value factor" (borrowed from variable-renewable-energy cost literature) as a partial mitigation,
   but collapsing DR into a single scalar $/MWh-equivalent number still risks losing the temporal/
   locational richness this project's own analysis has been building toward. If LCODR is ever pulled
   into this project's own model, treat it as one data point in a stack, not a replacement for the
   density/frequency/seasonal distinctions already established.

## 8. Scenario 3 compensation structure — a resolved design, and the reasoning behind it (from the same parallel session)

**Adopted as this project's own Scenario 3 DER-compensation design, direct user instruction,
2026-09-02** (see §0.4 for the full adoption status): the structure (§8.1) and the "Recommended
Program" component list (§8.3), including the 25/75 avoided-transmission-cost split, are settled.
Not yet resolved by this adoption: the floor mechanism's own value factor (§8.8), and re-running the
adopted structure against this project's own hourly-LP methodology to produce a this-project NPV
figure — the $1,053/$355 figures below remain the parallel session's own annual-model result, not
this project's.

*(This section documents a genuinely resolved set of decisions, not just research — the parallel
session worked through the structural question, built and corrected the resulting compensation
tiers, and arrived at a specific, defensible design. Preserved here for the reasoning and mechanism,
not the specific dollar figures, which used that session's own capex/discount-rate assumptions and
should be re-derived against this project's own current parameters before being treated as final.)*

### 8.1 The structural question, resolved

Three options were weighed for how Scenario 3's own DER compensation should be organized: (1) keep
every value stream (LSRV, DRV, REC, event-based, undiminished-storage) as independent, stackable
sensitivities — maximum transparency, but no single decision-ready number; (2) consolidate
everything into one new base case — decision-ready, but silently overrides everything already
established and forces several judgment calls at once; (3) a hybrid — keep the existing base case
unchanged, add a clearly-labeled "Recommended Program" tier as one consolidated combination, and
retain the individual sensitivities underneath as reference. **Option 3 was chosen** — it's the only
option that doesn't force a choice between decision-readiness and preserving what's already been
established, at the cost of more to build and maintain.

### 8.2 Two mechanism corrections worth carrying forward as general principles, not just as fixes

Both were caught mid-build in the parallel session, and both generalize beyond that session's own
model — worth stating as principles for this project's own future DER-economics work:

**Capacity de-rating and energy value are different questions; don't let one "undiminished" decision
answer both.** Reliability sizing (how much storage the *system* needs to physically build, and how
much of it can be counted on during real stress) is a different question from an owner's own energy
revenue for what a battery actually *delivers*. A storage-friendly retail tariff (VDER-style) can
legitimately not derate the second — a state retail incentive program has no obligation to mirror
PJM's wholesale reliability accreditation math, since a well-established regulatory-purpose
distinction. But the first must still respect PJM's real ELCC schedule regardless of what compensation
structure sits on top of it: a battery that's only reliably available 20-50% of the time during
genuine stress hours can't be treated as 100%-available for the purpose of what actually needs to
get built. Conflating these two led to an initial, incorrect design; separating them cleanly is the
right general principle for this project's own future work, including its own Scenario 3.

**A flat, unmanaged-export discount doesn't apply to a well-timed, storage-backed owner's own
discharge.** A "midday discount" on export price is a legitimate discount for raw, unmanaged surplus
solar (which genuinely clusters at midday, when prices are structurally lower) — but a 100+kW owner
or VPP aggregator with real dispatch control is charging cheap midday and discharging into
evening/morning peaks, the opposite behavior the discount was built to describe. Applying a
midday-surplus discount to a deliberately-timed storage discharge understates that owner's real
revenue. General principle: any energy-price discount factor needs to be checked against *whose*
behavior it's actually describing before being applied to a new revenue line.

### 8.3 The final "Recommended Program" component list, and why each choice was made

| Component | Choice made | Reasoning |
|---|---|---|
| Energy | Undiscounted wholesale-equivalent base rate (no midday-surplus discount — see §8.2) | Reflects a well-timed, storage-backed owner's real dispatch behavior, not raw unmanaged export |
| Capacity — storage | PJM-ELCC-derated, same as the base case (not undiminished — see §8.2) | Reliability sizing must reflect real, PJM-measured availability regardless of tariff design |
| Capacity — solar | PJM's declining ELCC schedule, unchanged | Same principle, solar side |
| Locational | LSRV-style adder (already built as its own sensitivity; referenced directly, not duplicated) | Real NY precedent, quantified rate (§7.4) |
| Environmental | Virginia's own real, current D-REC spot price (§7.3) | No import needed — real, current Virginia law |
| Event-based | NY DRV-style, converted to an annual-equivalent rate using real local hourly load data (§7.4) — not MA's ConnectedSolutions | DRV and Dominion's own real PTR rate independently converged on a similar figure, a genuine cross-validation signal; ConnectedSolutions was structurally mismatched to a real, twice-replicated 50/50 winter/summer peak split (§7.4) that a summer-only program would be blind to |
| Transmission-avoidance | A new, explicitly-designed transfer mechanism (§8.4) | Real, additive mechanism found while reasoning about Scenario 3's own structure — see below |

### 8.4 Avoided-transmission-cost as a DER-owner benefit — a real mechanism, built as an explicit transfer

**The underlying logic**: in a design where a meaningful share of total capacity is DER-owned rather
than utility-scale, every kW that's rooftop/canopy instead of utility-scale directly reduces the
utility's own transmission-interconnection need (the same $/kW transmission cost this project's own
Appendix A.16-adjacent capex work already applies to utility-scale solar). That's a real, mechanistically
sound, quantifiable avoided cost — conceptually the direct transmission-level sibling of the
distribution-level LSRV mechanism already built.

**The double-counting risk, and why this must be built as an explicit transfer, not free new value**:
a system-wide cost figure that already reflects a smaller DER-ownership-driven utility transmission
build has already handed that avoided cost to ratepayers generally, as a lower system-wide cost. Credit
that same dollar amount to DER owners as new revenue on top, and the same avoided cost gets counted
twice — once as "ratepayers pay less," again as "owners get paid extra," without the second dollar
coming from anywhere real. **The correct framing: this is a transfer, not new value created from
nothing** — exactly the same principle LSRV already embodies. If DER owners receive it, ratepayer-side
savings must shrink by the same amount, and that reduction should be shown explicitly on the
ratepayer/utility side of the accounting, not silently absorbed.

**A specific split, worth noting as a policy lever with a documented rationale**: the parallel session
split this transfer 25% to DER owners (as a real incentive payment) / 75% retained as ratepayer
savings, explicitly justified by an affordability priority (making the ratepayer-side benefit visible
and dominant, while still creating a real incentive), with the ratepayer-side cost of running the
incentive shown as its own explicit, small SLCOE line — not buried inside the primary figure. This
25/75 split is a policy choice, not a derived number — worth deciding fresh for this project's own
Scenario 3 rather than assumed, but the *mechanism* (transfer, not new value; explicit ratepayer-side
disclosure; a stated policy rationale for the split) is a sound, reusable design regardless of what
split this project's own Scenario 3 ultimately adopts.

### 8.5 Dominion's own current DER-adjacent programs — a real, current finding that no in-territory mechanism cleanly fits automated battery dispatch

Beyond the Peak Time Rebate and EV charger program already documented (§7.1), the parallel session
checked Dominion's Smart Thermostat Rewards program specifically to test whether it — being genuinely
automated Direct Load Control, unlike PTR's manual/behavioral design — might be a better mechanism
match for a battery's automated dispatch. It isn't usable for this purpose either: compensation is a
flat $25 signup + $25/year, completely decoupled from event count, hours, or capacity — there's no
sensible way to convert a flat annual participation fee into a $/kW-year rate. **The honest conclusion
worth carrying forward: Virginia currently has no real, in-territory program that is both automated
(matching a battery's actual dispatch mechanism) and capacity-scaled (economically meaningful for a
real asset)** — PTR is automatable-in-principle but structurally a manual/behavioral program; Smart
Thermostat Rewards is genuinely automated DLC but not capacity-scaled. This is the same underlying
gap already noted (§7.1) — Dominion's own VPP battery pilot rate isn't public yet — observed
independently from a different angle.

### 8.6 Three distinct commercial pathways for DER wholesale/quasi-wholesale participation, and Virginia's own PJM DER-aggregation size thresholds

Directly bearing on Scenario 3's own FERC 2222 market-participation language (part a/b of the
scenario's own definition): **an individual DER has no minimum size to participate in an aggregation,
but a combined DER Aggregation Resource (DERA) must total at least 100 kW to register and bid into
PJM's energy, capacity, or ancillary-services markets via an aggregator; individual component DERs
within an aggregation cannot exceed 5 MW.** This is a hard regulatory floor, not a business-model
choice — for the great majority of Scenario 3's own individual rooftop systems (5-15 kW) or even a
mid-sized canopy, direct wholesale participation is structurally inaccessible without bundling
through an aggregator. **PJM's own FERC Order 2222 framework doesn't open this pathway until February
1, 2028 for energy/ancillary services, and the 2028/2029 Base Residual Auction for capacity** — a
concrete, citable date this project's own Scenario 3 timeline should account for.

This resolves what would otherwise look like a contradiction: a large (16.8 GW nationally, 300 MW
already live in Northern Virginia specifically) VPP program was found operating today, years before
Order 2222 opens. The resolution is that **there are three structurally distinct commercial pathways,
not one**, with different availability timing:

| Pathway | Mechanism | Available |
|---|---|---|
| Utility-administered tariff | A regulated rate (PTR, thermostat rewards, a future Dominion VPP tariff, any state-adopted LSRV/DRV-style program) paid directly by the utility | Now — doesn't touch Order 2222 at all |
| Private bilateral contract | An aggregator sells DER capacity directly to a private commercial buyer (e.g., a hyperscale data center operator) under a private contract, bypassing utility ratemaking entirely | Now — also doesn't touch Order 2222 |
| True PJM wholesale market (DERA) | Direct energy/capacity/ancillary-services bidding via an aggregated 100kW+ resource, under FERC Order 2222 | Not until Feb 2028 (energy/ancillary) / 2028-29 BRA (capacity) |

The already-operating VPP program is using the private-bilateral pathway specifically — a hyperscaler
with its own acute outage-cost exposure (directly evidenced by the Ashburn near-miss, §7.6) may
plausibly pay more for firm local capacity than any regulated tariff, since its willingness-to-pay
reflects its own outage cost, not a public-interest rate-setting process. **Worth an explicit decision
for this project's own Scenario 3**: whether the FERC 2222 market-participation language in the
scenario's own definition should be scoped to the true wholesale DERA pathway specifically (2028+,
matching Order 2222's real timeline) or broadened to include the private-bilateral pathway that's
demonstrably already active in exactly this project's own geography today.

### 8.7 Real PJM nodal LMP data — Loudoun, Tysons, and Richmond compared, and a genuine correction to an earlier locational claim

Real hourly LMP data (energy/congestion/loss decomposed) was obtained for three Dominion-zone nodes:
Loudoun (500kV EHV, the bulk-transmission node type), and Tysons and Richmond (both 35kV distribution-
level "LOAD" nodes — a real difference in node type, not a perfect apples-to-apples comparison).
Overall means: Loudoun $71.42/MWh, Tysons $83.10/MWh, Richmond $62.93/MWh — Tysons running *higher*
than Loudoun, a genuinely counter-intuitive finding worth being explicit about.

**A real, worth-preserving correction to an earlier "Loudoun is the most congested node" framing**:
checking specific stress events revealed the congestion pattern splits by event type, not by node
identity alone. **Winter extreme events (Winter Storm Fern, the February peak window) tracked closely
across all three locations** (Fern: Loudoun $409.12, Tysons $410.83, Richmond $371.67) — winter stress
is largely system-wide, not a Loudoun-specific transmission bottleneck, consistent with what's already
known mechanistically (Fern was substantially a cold-driven, system-wide generator-failure event, not
a localized congestion event). **Summer events showed genuine locational divergence, with Tysons — not
Loudoun — the more stressed node** (June 2025 heat wave: Loudoun $177.73 with *negative* mean
congestion, Tysons $247.06 with +$43.87 congestion) — summer stress is locationally variable within
Northern Virginia, shifting with whatever specific circuit binds that day, not reliably concentrated
at any one "worst" node. **Worth correcting in this project's own materials if a similar single-node
congestion claim has been made anywhere**: the right framing is "Northern Virginia broadly, with
winter system-wide and summer locationally variable" — not "Loudoun is the most congested location."

One dataset checked and explicitly ruled out as unhelpful for this purpose: PJM's "Nodal Reference
Prices for Export Credit Screening" is a bi-monthly credit-risk-management tool for external
interface points (where power crosses into neighboring grids), not a real-time/day-ahead market price
signal — not Virginia-specific, not hourly, structurally the wrong tool regardless of its
superficially-relevant name.

### 8.8 Value Factor, quantified with real data — real upside, three genuine caveats, and a documented revenue-volatility risk with a proposed mitigation

Using real Loudoun LMP data, a battery discharging into its own top 2/4/6 hours per day (rather than
being credited a flat 24-hour average) captured 2.89x/2.34x/2.00x the flat average price respectively
— a substantial, real, data-grounded case that a flat-average energy-value assumption meaningfully
understates a well-dispatched battery's real value. **Three genuine caveats, all worth carrying into
any use of this finding**: (1) this used perfect hindsight (each day's actual top-N hours, selected
after the fact) — a real operator dispatches on forecasts, and forecast error would reduce the real
captured premium below this ceiling; (2) no state-of-charge constraint was modeled — the calculation
assumes the battery is always full entering the peak window regardless of that day's actual solar
generation or charging opportunity; (3) **cannibalization at scale** — if every DG owner dispatches
into the same daily peak window, that additional supply itself compresses the peak price (the same
"price cannibalism" risk the LCODR paper, §7.8, flags directly) — realized value factor at Scenario
3's own eventual DG penetration is very likely lower than what today's much-lower-penetration data
shows. Honest read: the true, realistic value factor sits somewhere between 1.0 (flat-average, the
current assumption) and the ~2.0-2.9x idealized ceiling — probably meaningfully above 1.0, but not
close to the full ceiling without further work to discount for forecast error and cannibalization.

**A documented, real revenue-volatility risk, with New York's own experience as direct precedent**:
NY's capacity-price component swung roughly 400% within a single year in NYC specifically, and
NYSERDA's own materials confirm the Energy Value component — not DRV or LSRV, both of which are
already locked in as fixed 10-year rates — is the one piece of NY's own VDER design left fully exposed
to real-time market swings. **Virginia's own real Loudoun data shows comparable volatility**: monthly
captured value (4-hour discharge) ranged from $64.60/MWh (August 2025) to $403.82/MWh (July 2026) — a
6.25x max/min ratio, coefficient of variation 0.56. A developer financing against one year's pattern
could be blindsided by the next.

**Proposed mitigation, worth adopting as a design pattern for this project's own Scenario 3 if a
similar energy-value-timing mechanism is built**: a floor-price transition structure — during an
initial multi-year period (5 years was used), a participant receives max(floor, market), with the
floor set to the existing base linked price; after the transition, full market exposure applies. This
protects early participants against downside shock during the period when program uptake is most
fragile, while preserving genuine long-term market-price exposure (and the upside that comes with
it) once the market has matured. Explicitly verified as correctly implemented by a clean structural
test: with the post-transition price set equal to the floor (a placeholder value factor of 1.0), the
mechanism reduces to exactly the base case, confirming the transition logic itself is sound
independent of whatever real premium eventually gets assigned to it.

## 9. Virginia Energy Plan Input.docx, Appendices B/C — NoVA price-spread mechanics, NY VDER Capacity Alternatives, and physical DER siting potential

*(A separately-uploaded document, not part of the parallel-session transcripts documented in §§6-8.
Appendix A ("Direct Transfer Trip (DTT) Considerations") and Appendix D ("Approaches by other
utilities") both exist in the same document and were not read as part of this pass — Appendix D in
particular, given its title, may be directly relevant to a similar "lessons learned" question and is
worth checking in a follow-up if useful.)*

### 9.1 Why wholesale prices vary within Dominion's own network — a clear mechanical explanation, largely confirmatory

The standard LMP decomposition (Nodal LMP = Marginal Energy + Marginal Congestion + Marginal Loss)
is stated plainly, with the NoVA-specific driver named directly: Northern Virginia's own Marginal
Congestion Component turns positive during high-demand hours (transmission from western generation
hubs becomes constrained), while its Marginal Loss Component is also elevated, since NoVA imports
power over long distances rather than generating locally. This mechanism-level explanation is
consistent with, and gives cleaner language for, the same effect already found and quantified in
this project's own real Loudoun/Tysons/Richmond node data (§8.7).

**A quantified benchmark worth noting as a contrast, not a contradiction**: this document gives a
*typical* on-peak NoVA-vs-rest-of-state spread of $10-30+/MWh, versus near-zero (<$1-2/MWh) off-peak
— substantially smaller than this project's own real-data finding for Winter Storm Fern specifically
($172.78/MWh congestion component at Loudoun). The two aren't in tension: this document is describing
ordinary/typical peak conditions, while this project's own figure is a genuine, documented extreme
event — worth keeping both in view as different points on the same distribution, not conflating a
typical-day spread with a stress-event one.

**A data source not yet explored**: alongside PJM Data Miner 2 and GridStatus (both already used this
session, with GridStatus's own web app confirmed inaccessible via fetch), this document names
**PowerDev** as a third option offering PJM real-time/day-ahead node-level price-map tooling —
untested here, a genuine candidate if GridStatus's own access limitation is ever revisited.

**Two additional named PJM pnodes** worth having on record if further locational work is ever done:
"Dominion Louisa" (central/southern benchmark) and "Dominion Clifton" (northern benchmark), alongside
this project's own already-used Loudoun/Tysons/Richmond nodes.

### 9.2 Value Stacking DER Compensation — mostly confirmatory of this project's own §7-8 findings, with two genuinely new, concrete policy mechanisms

Much of this section restates ground already covered in detail elsewhere in this document — NY's own
DRV (10-year lock) and Environmental Value (25-year lock), the double-counting-avoidance logic behind
stacking distribution-level and wholesale-level value (§7.2's own market-defensibility tiering covers
the same ground with more rigor), and the "avoid revenue shock" lesson this project's own §8.8 floor
mechanism was built specifically to address — confirmatory, not new, though useful as independent
corroboration that these are the right lessons to be drawing from NY's experience.

**A genuinely new, useful detail: NY's own VDER capacity value has three distinct, separately-named
"Capacity Alternatives," not one flat rate.** This document names "Capacity Alternative 2" as NY's
own fixed peak-window compensation design, and "Capacity Alternative 3" as NY's own performance-based,
single-hour/critical-event tier — this project's own existing $86/kW-yr ICAP figure (§7.4/original
research) is specifically Alternative 3, not a generic "NY capacity rate." Worth being precise about
this distinction if this project's own Scenario 3 work ever cites NY's capacity value again — there
are at least two other named alternatives with different designs, not variations on the same number.

**Two genuinely new, concrete policy mechanisms, not previously documented anywhere in this file**:

1. **A standardized "Value Stack Calculator" tool**, modeled directly on NYSERDA's own Excel/web
   tool — the specific, named NY lesson behind this recommendation is that early VDER tariffs were
   complex enough that mid-sized commercial customers and regional banks struggled to underwrite
   projects against them. A concrete, buildable policy recommendation worth carrying into this
   project's own policy-relevant observations (§8's own existing list, or the executive/technical
   summaries) if a similar tool is ever proposed for Virginia.
2. **"Wholesale-bypass" riders**: allowing C&I customers already enrolled in a utility's own
   interruptible-load program to opt into a rider that strips out the wholesale-capacity component of
   their existing retail credit specifically, so they can sell that capacity directly into PJM via a
   third-party VPP while retaining their retail credit for local distribution relief. A specific,
   named mechanism for exactly the kind of multi-use stacking this project's own market-defensibility
   work has been reasoning about in the abstract — worth considering as a concrete implementation path.

**A related lesson worth flagging even though it falls outside DER compensation design specifically**:
"high stack compensation is meaningless if projects spend years stalled in utility interconnection
queues or face arbitrary upgrade fees" — this document ties that risk directly to Virginia's own
Direct Transfer Trip (DTT) telecommunication costs as a named, existing bottleneck (covered in this
same document's own Appendix A, not read as part of this pass). Worth keeping in view as a real risk
to whatever compensation design Scenario 3 ultimately adopts — a well-designed rate is not sufficient
on its own if the underlying interconnection process remains a separate, unaddressed barrier.

### 9.3 DER Energy Calculations and Assumptions — a real, independent physical-siting cross-check for Scenario 3's own rooftop/canopy allocation

**Parking-lot canopy potential, built bottom-up from a national proxy**: ~800 million US parking
spaces (3,000-5,500 sq mi total) scaled to Virginia's own ~2.6% population/vehicle-registry share
yields an estimated 78-120 sq mi (50,000-76,800 acres) of Virginia parking pavement, of which roughly
80% is assumed toppable with canopy solar. Applying Virginia's own solar irradiance (4.3-4.7
kWh/m²/day) and standard ~20% panel efficiency (≈160 kWh/m²/yr AC after system losses) yields a total
estimated Virginia parking-lot solar potential of **16.6-49.7 TWh/year** — a real, independently
sourced ceiling worth checking Scenario 3's own parking-lot-canopy build-out against for physical
plausibility, not just cost/compensation reasonableness.

**A cost-ratio figure worth a direct cross-check against this project's own existing parking-lot
capex assumption**: this document states canopy installations run "roughly two times more expensive"
than standard ground-mounted systems. This project's own already-established figures (parking-lot
$3.80/W vs. rooftop $2.20/W) imply a ratio closer to 1.73x — directionally consistent, not an exact
match; worth noting as a minor, disclosed discrepancy rather than either treating them as identical
or flagging it as a contradiction.

**Rooftop solar potential, with a real, named, independent source and a direct tie to this project's
own existing Scenario 3 assumption**: Google's Project Sunroof estimates Virginia's total viable
rooftop solar potential at approximately **68,400 MW DC (68.4 GW)** statewide. This document states
Scenario 3 assumes roughly 1/12th of that figure (one solar array per 12 buildings) as its own
rooftop allocation — **worth a direct physical-feasibility check against this project's own current
Scenario 3 rooftop build-out trajectory**: does this project's own 10%-of-total-solar rooftop share,
at whatever absolute MW level Scenario 3 reaches by 2045, sit comfortably under this 68.4 GW ceiling,
or does it approach or exceed it? Not yet checked as part of this pass — a concrete, bounded follow-up
task if useful, using a real, sourced denominator rather than an assumed one.

## 10. Independent literature search — NY/CA/MA/MD/WA/HI/Germany/IL "lessons learned" (this session)

*Commissioned specifically because Appendices B/C of Virginia_Energy_Plan_Input.docx were AI-generated
(by a different model, later abandoned) and the user wanted independently-sourced verification and
expansion rather than continued reliance on that material. Organized by the cross-cutting themes that
emerged, since the most valuable findings recur across jurisdictions rather than sitting neatly under
one state.*

### 10.1 The single most important cross-cutting finding: transitioning away from a generous scheme is far more dangerous than never offering one

**Hawaii's own experience is the starkest, most directly quotable version of this.** Ending net
metering in 2015 caused an 80% decline in new solar installations in parts of the state; the number
of active solar companies on Oahu fell from 300 (2015) to 98. A sitting Hawaii state senator later
published a piece explicitly using this experience to warn California directly against a proposed
monthly "solar tax," writing "ending NEM nearly killed solar for us." **Massachusetts's own SMART
program shows the same pattern from a different angle, and very recently**: its solar-only incentive
(no storage) has actually collapsed to literal $0/kWh in every MA utility territory, because the
program's own formula (Base Rate + Adders − Value of Energy) let a rising "Value of Energy" term
erode the net incentive to nothing as retail rates climbed — a structural failure mode worth
naming explicitly: **a compensation design defined as a delta against a floating baseline can
collapse to zero even without anyone deciding to cut it.** Massachusetts's own broader market
consequence was severe and quantified: the state fell from a top-five solar market to 26th in new
installations, a decline explicitly attributed to a combination of interconnection delays and low
compensation rates together, not either alone.

**Direct implication for this project's own Scenario 3 design**: whatever compensation structure is
adopted, (1) avoid defining any component as an undefined delta against a market baseline without a
floor, and (2) treat any future reduction to an already-adopted rate as a high-risk action requiring
its own careful transition design — not because the rate itself was too generous, but because
*changing* it is where the demonstrated damage occurs.

### 10.2 A genuine, real-world precedent for this project's own Section K floor mechanism — Germany's Marktprämie, tested at national scale for over a decade

Germany's own "sliding market premium" (Marktprämie), introduced 2012 and made the primary RES
support instrument by a 2014 reform, is structurally the same mechanism as this project's own
Section K: the operator receives the market price plus a premium that tops the total up to a
guaranteed reference level — functionally the same as this project's own "max(floor, market)"
design, just described from the premium side rather than the floor side. **This is a real,
independently-studied success on its own stated terms**: a peer-reviewed counterfactual analysis
found the scheme's introduction reduced the number of negative-price hours by roughly 70%, since
operators are incentivized to curtail once a negative price fully offsets the premium — the opposite
of a flat feed-in tariff's "produce and forget" behavior, where a generator has no incentive to ever
reduce output regardless of price, a named term worth adopting directly. **A very recent (Feb 2025)
evolution is worth flagging as the field's own current direction**: Germany's new "Solarspitzengesetz"
(solar peak law) suspends subsidy payments for new PV systems during any 15-minute interval when
the day-ahead price turns negative — tightened from an earlier "six-hour rule" — while offering a
genuinely clever make-whole mechanism: rather than simply denying that revenue, the operator's own
~20-year compensation period is extended to reflect the number of suspended hours, balancing market-
signal fidelity against long-term revenue certainty rather than trading one for the other outright.

**A real, quantified confirmation of the cannibalization risk already flagged in §8.8**: over 90% of
German solar capacity remains under legacy fixed-price protection, and as captured market value falls
for the unprotected share (the "solar cannibalization" effect, driven by high solar penetration
compressing midday prices precisely when solar itself produces most), the support gap for that share
widens — a real, large-scale, currently-unfolding version of the same forecast-error/cannibalization
discount this project's own §8.8 flagged as needed but not yet applied to its own 2.0-2.9x idealized
ceiling.

### 10.3 California's own, formally-published "six key lessons" and a specific, named technical barrier

A 2018 Energy Bar Association law-review article, "DER in Wholesale Markets" (Gundlach & Webb),
interviewed CAISO stakeholders directly and distilled six formal lessons for other ISO/RTOs. **The
single most concrete, actionable finding**: CAISO's own requirement of 24/7 settlement for DER
aggregations (to hold them to the same reliability/transparency standard as conventional generators)
was named by every interviewee as a real barrier, with some calling it possibly insurmountable —
worth flagging directly to Virginia/PJM stakeholders as a specific, technical design choice to watch
for, not just a generic "administrative complexity" concern.

**A formal, Order-2222-level confirmation of the double-counting risk already discussed in §8.2/§8.4**:
an LBNL report states plainly that "Order 2222 allows RTO/ISOs to limit the participation of resources
in wholesale markets if a DER aggregation is receiving compensation for the same services as part of
another program" — this is not just a theoretical modeling concern this project has been reasoning
through; it is an explicit provision PJM itself could invoke. ComEd's own real, filed VPP tariff
(§10.8) independently builds in exactly this exclusion, confirming it is standard, expected practice.

**A sobering, multi-decade timeline lesson**: California's own demand-side DER integration effort has
been underway "with limited success" since 2007 — nearly two decades — and was explicitly insufficient
to prevent real 2020 rolling blackouts. Maryland's own PSC chair struck the same honest note in a 2026
order, stating plainly that VPP implementation "may not result in immediate relief." **Worth setting
this expectation explicitly for Virginia's own policymaker audience**: this is realistically a
multi-year, not multi-month, undertaking, even when every individual design choice is sound.

### 10.4 Massachusetts's own siting-type-specific evidence, directly on point for Scenario 3's rooftop/canopy segments

A real, current (April 2025) Massachusetts DOER-convened "Solar Canopy Working Group" — with DOER,
Eversource, and a real canopy developer (Solect, 33 completed MA canopy projects) as members — found
canopy-specific barriers genuinely distinct from generic solar barriers: real estate access, utility
easement complexity, and permitting/interconnection timeline mismatches specific to canopy structures.
Solect's own proposed solutions (standardized utility reviews, template easements, dedicated
technical-assistance funding, timeline flexibility aligned to project schedules) are concrete,
adoptable precedents. **A direct structural precedent for treating canopy differently, with two
distinct mechanisms**: SMART's own adders reward preferred siting (rooftop, canopy, brownfield)
while a separate "greenfield subtractor" actively penalizes ground-mounted development on undeveloped
land — two different levers for the same underlying goal, not redundant (already noted in §7.2, now
with the working-group-level implementation detail behind it).

### 10.5 Maryland's own, very current (May 2026) comprehensive VPP order — a concrete regulatory-process template

Beyond what was already documented in §7 from the parallel session, this session's own search
surfaced a real, six-provision PSC order (May 2026) worth citing as a template for Virginia's own
Order 2222 implementation process: (1) a Data Exchange Work Group for third-party data access, (2) a
DER registry accessible to aggregators, (3) required interconnection-tool alignment across BGE/
Delmarva/Pepco, (4) periodic utility registration-status reporting, (5) an explicit decision *not* to
accelerate DERMS deployment timelines despite pressure to do so, and (6) aggregator cybersecurity
non-compliance reporting. **Worth flagging specifically**: item (5) is a real, disclosed example of a
regulator deliberately choosing a slower, more deliberate pace over a faster one under real pressure —
directly consistent with the multi-year-timeline lesson in §10.3.

**A separately useful, quantified Maryland finding**: a state-commissioned study (CEIR-20) valued the
distribution-level line-loss-reduction benefit of aggregate distributed solar at up to $6/MWh — a
real, sourced, small additional value-stream component not currently part of this project's own
Recommended Program component list (§0.2), worth considering as an addition.

### 10.6 Washington's own useful framing concept and a real-world scale benchmark

Puget Sound Energy's own public framing of its VPP strategy as "energy orchestration" — coordinating
efficiency, demand response, distributed generation, storage, and EVs as a single resource — is a
genuinely useful conceptual term worth adopting in this project's own materials, distinct from the
narrower "VPP" label. **A real, directly comparable scale benchmark**: PSE's own 2045 plan targets
roughly 15,000 MW of clean energy resources, of which ~3,660 MW (about 24%) is planned to come from
demand-side/distributed resources — a real utility's own long-range distributed-share target, useful
context alongside this project's own 20% (10%+10%) Scenario 3 assumption.

### 10.7 New York's own additional detail beyond what §6-8 already cover

**A real, dated inflection point worth citing directly**: New York's own PSC 2019 adjustments to
VDER, which stabilized values that had been allowed to fluctuate in the program's earlier years, are
directly credited (by SEIA's own state policy director) with enabling the state's solar market to
"explode" afterward — the positive-case mirror of the Hawaii/Massachusetts cautionary examples above,
confirming stability itself (not just the compensation level) is a real, separate value driver.

**A genuinely useful, disclosed limitation in NYSERDA's own official VDER calculator tool**: even
this widely-cited, government-published tool has real, acknowledged shortcomings — a linear-only
degradation model (real degradation follows a curve), a fixed RTE assumption held constant for the
project's full life (real RTE also degrades), and reliance on historical LSRV call-period data rather
than the forward-looking optimization a real operator would use to maximize LSRV-DRV coincidence.
Worth citing directly if Virginia ever builds an analogous calculator tool (§8.5's own recommendation)
— learn from NY's disclosed gaps rather than reproducing them.

**A useful refinement to the "Capacity Alternative" structure already noted in §9.2**: ICAP Alt 2
(a fixed peak-window design) yields higher revenue than Alt 1 across all NYISO zones; Alt 3
(performance-based, single-hour/critical-event) is specifically limited to standalone BESS projects,
not available to solar or hybrid systems — a real eligibility distinction worth knowing if any of
these alternatives are ever cited as a specific benchmark rather than referenced generically.

### 10.8 Illinois/ComEd — the most directly relevant of all nine jurisdictions, given it is this project's own named retail-rate model

**A real, quantified validation of the underlying retail-rate-design concept Scenario 3's own part
(d) is built on**: ComEd's own four-year time-of-use pilot (concluded 2024) found genuine, measured
behavior change — both EV-owning and non-EV-owning participants meaningfully reduced "super peak"
summer usage, with EV owners saving $10-70/month and peak demand reduced 6.5-9.7% each summer across
the pilot. This is real, not modeled, evidence that the core Scenario 3 mechanism (retail day-ahead/
real-time pricing driving genuine load-shifting) works in practice, in exactly the utility this
project's own scope document already names as the model.

**A genuinely important, very recent (Nov 2025) cautionary process lesson**: ComEd withdrew its own
already-filed VPP tariff proposal (Rider VPP, plus companion Rider CSS and Rider BYODLR) specifically
because new state legislation (the Clean and Reliable Grid Affordability Act, signed Jan 2026) was
about to supersede it — a real illustration that even a well-designed, already-filed program can be
overtaken by superseding legislation mid-process, a process risk worth naming for Virginia's own
timeline expectations if the General Assembly and SCC pursue parallel tracks.

**A real, directly comparable, and notably low statutory floor rate**: CRGA sets ComEd's own VPP
compensation at a $10/kW-year statutory minimum (average dispatch power basis) — substantially below
every other rate documented across NY ($50.59/kW-yr DRV-equivalent), MA ($250/kW-yr ConnectedSolutions),
and this project's own already-adopted event-based component. Worth flagging as the low end of the
real-world range, not a rate to adopt, but useful for bounding how wide the genuinely-observed
spectrum is.

**The same double-counting exclusion already discussed in §10.3, independently confirmed in a real,
filed tariff**: ComEd's own proposed VPP explicitly excludes customers already enrolled in an
"incompatible" program rewarding similar behavior (e.g., a peak-time rebate or A/C-cycling program) —
direct, filed-tariff-level confirmation this is standard practice, not a theoretical concern.

**A directly parallel load-growth/capacity-price context, worth citing since ComEd sits in the same
PJM footprint as Dominion**: ComEd reported 28 GW of new large-load interconnection applications
between January-August 2025 alone (more than 4 GW above its own prior record peak), and PJM's own
capacity price for ComEd's zone rose from $68.96/MW-day (2022-23) to $333.44/MW-day (2027-28) — the
same underlying PJM-wide capacity-price pressure this project's own analysis has documented for
Dominion, now confirmed as a shared, PJM-wide phenomenon rather than something specific to Northern
Virginia's own data-center concentration.

## 11. Structural/methodological questions (not citation gaps — real design decisions)

| Aspect | Status |
|---|---|
| How DER-owner wholesale arbitrage interacts with this project's standing export rule (Appendix P #8: export never inside the LP objective) | **Not yet addressed, and this is a real structural question, not a detail.** #8's existing rule governs a centrally-dispatched utility LP's own optimization. Scenario 3's DER owners dispatching their own storage for individual arbitrage profit is a conceptually different actor with a different objective — whether this is modeled as a post-hoc calculation analogous to #8's existing treatment, or requires a genuinely different mechanism (since individual owners might dispatch differently than a cost-minimizing central utility would), hasn't been decided. |
| Land acreage accounting for agrivoltaic dual-use land | **Open — already flagged in Appendix P #10**, restated here for completeness: whether agrivoltaic acreage counts as equivalent to standard exclusive-use solar acreage or as a distinct dual-use category is an explicit, undecided methodology choice. |
| Land acreage accounting for rooftop/canopy solar | **Not yet addressed anywhere.** Unlike utility-scale or agrivoltaic siting, rooftop and parking-canopy solar doesn't consume new land — it uses existing structures/paved area. Whether this project excludes this 20% from the land-acreage total entirely, or tracks it separately as a distinct "zero-incremental-land" category, hasn't been decided. |
| Reserve margin (17.7% IRM) | **Value settled, mechanism built and tested — but only against Scenario 1 so far.** Will need to be applied once Scenario 3's own LP exists; no reason to expect the outcome (binding or not) to match Scenario 1's own checkpoint-by-checkpoint pattern, given Scenario 3's materially different resource mix. |
| Storage dispatch degeneracy (simultaneous charge/discharge) | **Standing requirement now exists (Appendix P #13, this session)** — must be directly verified against Scenario 3's own solved output once built, not assumed clean by analogy to Scenario 1's own clean results, especially given Scenario 3 introduces a new storage-dispatch context (DER-owner-operated distributed storage) the existing verification has never been tested against. |
| Gas fleet / new-build methodology | **Already sourced, no gap.** Scenario 3/3B falls under the same standing rule as Scenario 1/1B (`new_peaker_ccgt_costs_by_size.md`'s own explicit scope: "Scenario 1, 1B, 3, 3B, and 3C specifically") — overhaul/retain near-EOL plants first, simple-cycle new-build (Aeroderivative/F-Class/H-Class) for any remaining shortfall. |
| Tier 1/2/3 social cost | **No new gap** — same methodology as Scenario 1, just needs computing once Scenario 3's own gas dispatch (if any, under whatever gas-allowance target Scenario 3/3B ultimately uses) is solved. |
| **A second, lower demand-projection model set across all scenarios** *(raised 2026-08-24, held for future discussion, not yet scoped)* | **Open, explicitly deferred by direct user decision — a real, project-wide methodological question, not an A.7-specific one.** Motivating evidence, all independently sourced this session in the A.7 research (`Appendix_DataCenter_DemandFlexibility_A7.md`, Sections 8-10): (1) phantom/speculative interconnection-queue inflation (one estimate of 5-10x actual data centers vs. speculative requests; AEP Ohio's own measured ~57% queue reduction after a firm-commitment tariff; Dominion's own testimony splitting its pipeline into 25,000 MW with a confirmed energization date vs. 75,000 MW without one); (2) a physical constraint independent of financial filtering (chip-availability limits on how much proposed capacity can actually be built, per the October 2025 hyperscaler counter-proposal to PJM); (3) financial filtering mechanisms explicitly designed to "shake out" speculative load (GS-5's own collateral/minimum-take terms, confirmed directly by a named SCC-case attorney; the new $0.011/kWh consumption tax); (4) public/political opposition capable of halting projects outright, not just raising their cost (a real, quantified $156B in projects delayed or canceled nationally in 2025 per Data Center Watch; Texas's own governor imposing what functions as a de facto statewide pause). Four independent mechanisms, all pointing the same direction — the announced/requested demand pipeline this project's current scenarios are built against very plausibly overstates what actually gets built by 2045. **Real open questions, explicitly not yet resolved and not to be answered without a dedicated methodology discussion**: where a defensible lower-demand figure would actually come from (the AEP Ohio and Dominion 25/75 GW figures are real anchors but weren't built as 2045 demand curves and aren't directly transferable); whether this requires a full parallel second model set across all scenarios (S1/S1B/S2/S3 and sub-variants) or a lighter sensitivity band applied to existing results (full re-optimization matters most where the LP's optimal resource mix could shift non-linearly at lower demand — e.g., fixed transmission/interconnection costs not scaling down proportionally with load — so this isn't purely a scope-convenience question); and how to frame this for the whitepaper's own reader list (which includes sitting legislators) as a symmetric high/low sensitivity band bounding genuine uncertainty, not as an implicit policy argument for "build less." **Structural resolution, direct user decision, 2026-08-26**: this — and the parallel climate-adjusted-demand question (`Climate_Trends_and_Weather_Station_Methodology.md`) — are **not a prerequisite blocking other features**, despite both being "upstream" in the broadest sense (each would affect every feature's own sizing). Both are run as **separate, independent scenario variants** alongside the base case (the same pattern Scenario 3B already uses relative to Scenario 3), not resolved first and then built into every other feature's own baseline. This directly unblocks proceeding through the rest of the feature list without waiting on either. |
| **Climate change's effect on demand profiles through 2045** *(raised 2026-08-24, groundwork in progress, not yet resolved)* | **Open — real groundwork established, guiding question not yet answered.** Motivating concern, direct from the user: all historical load/price/weather data this project uses is necessarily backward-looking, while climate change may alter future summer-heat and winter-cold extremes in ways the historical record doesn't capture. Virginia's own first statewide climate assessment (VCA, GMU Virginia Climate Center, Nov. 2025) found and quantified directly: summer heat evidence is real, quantified, and one-directional (WBGT +0.29°F/decade since 1950; projected days above 95°F dry-bulb ranging ~10 to >50 by end-of-century depending on emissions pathway; cooling degree-days rising fastest specifically in the Tidewater and Northern divisions, with an explicit VCA-drawn connection to data-center-driven grid heat-sensitivity in the Northern division) — supports treating historical extreme-heat-hour frequency as a floor, not a ceiling, for future checkpoints. Winter cold evidence is genuinely mixed, not one-directional: the VCA's own data shows the coldest days warming faster than the warmest (i.e., average winter cold moderating), but whether discrete polar-vortex-disruption *events* are becoming more frequent within a warmer winter is an active, unresolved scientific debate with real evidence on both sides — does not support a symmetric "more severe" winter adjustment the way summer heat does. A three-category weather-station framework was developed (stayed-rural baseline; already-populated-stayed-populated established-UHI reference; rural-to-urban-transition, most demand-relevant) with one category (Sterling, VA, GHCND:USC00448084, 1977-present) fully station-confirmed, one (Pennington Gap, VA) strongly evidenced demographically but not yet station-verified, and one (urban reference — Arlington/Richmond/Norfolk candidates) not yet individually verified. **A real, disclosed tooling constraint**: this project cannot pull raw NOAA daily station data directly (web_fetch can't construct parameterized API URLs; bash's network allowlist excludes NOAA) — the concrete next step is user-uploaded raw station data, mirroring the LMP/load CSV upload pattern already used successfully this session. See `Climate_Trends_and_Weather_Station_Methodology.md` for full detail. |

## 12. Summary — what you'd actually need to fill in

Narrowing all of the above to genuine open decisions or sourcing gaps
(excluding items already sourced, and excluding the LMP-data item, which
is a processing task rather than something to fill in):

1. ~~**DER compensation structure** — no longer fully open. §8.1-8.3 document a resolved structural approach (hybrid: base case + a "Recommended Program" tier + retained individual sensitivities) and a specific, reasoned component list, from the parallel session. Adopting this design (or deliberately choosing differently) for this project's own Scenario 3 is now a concrete yes/no/adjust decision, not a blank-slate one.~~ **Resolved, direct user instruction, 2026-09-02: adopted as this project's own Scenario 3 design (see §0.4).** The floor mechanism's own value factor (§8.8/§0.3) remains a separate, still-open decision — not resolved by this adoption. The concrete remaining step is re-running the adopted structure against this project's own hourly-LP methodology to get a real, this-project NPV figure (§0.4, item 4).
2. **Elasticity value for price-responsive demand** — three options presented, none chosen.
3. **Rooftop-vs-canopy CF treatment** — same ratio or distinct? §6.3/§7 give real precedent for treating them differently (MA's own distinct canopy vs. building-mount adders), if that's the direction chosen.
4. **Layout assumption** (shallow-tilt vs. east-west) underlying the 0.81 CF ratio.
5. **Distributed storage sizing/dispatch mechanism** — central LP decision or independent DER-owner decision? §6.6's cross-state convergence (broad arbitrage layer + separate targeted-locational layer) plus §8.1-8.3's fully-worked-out example structure give this project's own Scenario 3 a concrete template to adopt or adapt, not just a direction.
6. **DER-owner arbitrage vs. the export-rule structure** — how Scenario 3's individual-owner dispatch relates to #8's existing centralized-LP treatment. Same status as #5 — a concrete worked example now exists, not yet adopted/built here.
7. **Heat pump/PHIUS efficiency measures' own quantified impact** — not researched at all yet.
8. **Land acreage treatment**: agrivoltaic dual-use accounting, and rooftop/canopy's zero-incremental-land treatment.
9. **Locational value credit** — §7.4's NY LSRV rate ($31-37/kW-year) gives a real starting benchmark, but §7.2's own market-defensibility tiering is explicit that this only becomes fully defensible with an actual Virginia-specific avoided-cost study identifying a real constrained Dominion location and its real avoided capital cost — the benchmark exists now; the underlying Virginia-specific study still doesn't.
10. **Farmland lease income figures** — claimed complete in an unverified source; needs an actual check for whether this research exists anywhere, or needs redoing.
11. **DLC vs. price-signal design for Scenario 3's own retail rate component (part d)** — new, surfaced by §7.5's own literature: price-based signals carry documented failure modes (load synchronization, inadequate response speed under genuine emergency conditions like the Ashburn near-miss) that a DLC-style mechanism avoids, at the cost of DLC's own limitation (participant overrides can halve its reliability value). Not yet decided whether Scenario 3's own market-participation design should be price-signal-only, DLC-only, or a hybrid.
12. **Whether to formally cost the DLC-with-backup-generation externality** (~$213-253/MWh, Ashburn-style, §7.6) anywhere in this project's own Tier 1/2/3 framework, or hold it as disclosed context only — an explicit open question from the parallel session, not yet answered either way.
13. **Whether Scenario 3's own FERC 2222 market-participation language should scope to the true wholesale DERA pathway specifically** (not available until Feb 2028 per §8.6) **or explicitly include the private-bilateral pathway** already active in this project's own geography today (§8.6) — a new, concrete open question, not yet decided.
14. **Avoided-transmission-cost transfer split for this project's own Scenario 3** — §8.4 documents a sound mechanism (transfer, not new value; explicit ratepayer-side disclosure) with a worked 25/75 example from the parallel session, justified there by an affordability priority — the mechanism is ready to adopt; the actual split percentage for this project's own Scenario 3 is a fresh policy decision, not inherited automatically.
15. **Revenue-volatility floor mechanism for any energy-value-timing component this project's own Scenario 3 eventually builds** — §8.8 documents a tested, working design pattern (a multi-year floor-then-market-exposure transition) with real Virginia data (6.25x monthly max/min ratio) motivating why it matters — not yet decided whether to adopt for this project.
16. **Physical-feasibility check: does this project's own current Scenario 3 rooftop build-out sit under Virginia's real ~68.4 GW total viable-rooftop ceiling** (Google Project Sunroof, §9.3)? A concrete, bounded, not-yet-performed check against a real sourced denominator, not a sourcing gap.
17. ~~A related, not-yet-read section of the same uploaded document — Appendix D~~ — **resolved**: read directly and confirmed it lists the technical mechanisms utilities use (bi-directional transformers, voltage regulation, protective relaying) plus an Order 2222 RTO-implementation-status comparison table — no cost figures. Superseded by items #21 below.
18. **A negative-price/oversupply safeguard for whatever energy-value component Scenario 3 ultimately adopts** — §10.2's own Germany precedent (a 15-minute-granularity subsidy-suspension rule, paired with a compensation-period-extension make-whole mechanism) is a real, tested design this project's own Section J/K currently lacks entirely; worth an explicit decision on whether to adopt a similar safeguard or deliberately not.
19. **Whether to add a distribution-line-loss-reduction value stream to the Recommended Program component list** — §10.5's own Maryland CEIR-20 figure (up to $6/MWh) is a real, sourced, currently-unused addition candidate.
20. **A structural risk not yet accounted for in this project's own timeline assumptions**: §10.8's own ComEd example (a filed VPP tariff withdrawn mid-process due to superseding state legislation) and §10.3's own multi-year CA/MD timeline lessons both suggest Virginia's own Order 2222/VPP implementation should be planned around realistic multi-year regulatory-process risk, not a single clean filing-to-approval path — worth reflecting explicitly wherever this project's own materials describe an implementation timeline.
21. **Distribution-upgrade cost for high-DER-penetration hosting capacity** — §2.1 proposes a general-benchmark $500/kW figure (real, sourced, but not Dominion-verified); §2.2 refines the "apply to 100% of the build" simplification with a transparent circuit-count estimate (~910-2,140 of Dominion's own circuits, roughly half its total), yielding an illustrative $0.9-5.4B combined range. Three real, unresolved decisions remain: (a) whether to adopt the $500/kW figure and the circuit-count refinement as-is, adjust either, or pursue real Dominion hosting-capacity-tool data (confirmed to exist, §2.2) circuit-by-circuit instead; (b) whether this cost should be borne on the utility side (parallel to the transmission-avoidance mechanism) or allocated in part to individual DER-owner interconnection fees; (c) whether to independently verify Dominion's own 15%-of-peak-load screening threshold (§2.2, currently sourced from a third-party site) against an official Dominion or SCC document.
