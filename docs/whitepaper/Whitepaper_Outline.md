# Whitepaper outline — three layers

**Status 2026-09-14.** Structure and placement, with Scenario 2's measured results in place and
every other scenario marked as pending. Written to make the gaps visible, so the compliance sweep
has a target to fill rather than a blank page.

**Three layers, each complete on its own.** The readership runs from state legislators to utility
modelers, and one continuous document serves neither end well. Each layer is readable without the
one below it.

| layer | length | reader | answers |
|---|---|---|---|
| Executive summary | 2 pages | senators, delegates, senior VDOE leadership | what it costs, what it buys, what to decide |
| Technical summary | 12–15 pages | senior engineering staff, a level or two above resource planning | how the answer was reached, and how confident to be |
| Body and appendices | full | resource planners, modelers, stakeholder analysts | everything, checkable |

---

## What the paper is centrally about

**The curve, not the number.** Annualised cost against compliance level, 75–100%, with Scenario 2
plotted as a single point. Every scenario contributes a curve or a point to that chart, and the
chart is the deliverable.

**System levelised cost is informal throughout.** It is reported as a secondary figure in tables
because it compresses a twenty-year stream into one number and readers ask for it — but the
headline is always annualised cost, because that is what a budget and a rate case deal in.

**Two questions carried in parallel, never merged.**

● **Capacity planning** — is enough capacity *built*? Metric: installed reserve margin against
  accredited capacity at peak. What sizes the fleet.
● **Resource adequacy** — does the built system *serve load*? Metrics: loss-of-load hours, unserved
  energy, shortfall event count and duration, per NERC's *Risk Mitigation for Emerging Large Loads*.

They answer different questions and can disagree. Scenario 2 at 2045 satisfies a 17.7% reserve
margin on PJM's own accreditation while leaving 30 TWh unserved when gas is bounded by the real
fleet — which is exactly why both are reported.

---

# LAYER 1 — EXECUTIVE SUMMARY

**Two pages. No methodology. Written so a delegate can act on it without reading further.**

## 1.1 The question

Virginia's clean energy targets were written in 2020 against a demand forecast that has since
doubled. Are they still achievable, and at what cost?

## 1.2 The answer, in one chart

**[CHART: annualised cost against compliance level, 75–100%, with the gas-price band as a shaded
range and Scenario 2 as a single point.]** — *pending the compliance sweep*

## 1.3 What the statutory minimum buys

Building only what the Code names — 16,100 MW of solar and 20,000 MW of storage — and meeting the
rest with gas:

| | 2026 | 2035 | 2045 |
|---|---:|---:|---:|
| clean share of energy | 47.4% | 46.1% | **31.6%** |
| annualised cost | $1.9B | $5.7B | **$10.9B** |

**Compliance falls by a third while cost rises more than fivefold.** Clean share peaks near 2030 as
the statutory solar comes online, then declines as demand overtakes a fixed target.

**Storage moves energy; it does not create it.** A fixed solar target against rising demand can only
lose ground, however much storage is paired with it.

## 1.4 Three findings a decision-maker should know

**The two statutory solar requirements work against each other.** § 56-585.5(D)(2) sets a one-time
16,100 MW capacity target due 2035. § 56-585.5(C)(2), as raised by HB 628 / SB 175, sets an annual
*energy* obligation from resources under 1 MW that grows to about 6,900 MW equivalent by 2045 — 60%
of new build. Because those resources are fixed-tilt rather than tracking, the same nameplate
delivers roughly 4.4 TWh less.

**The mandated storage is insufficient, not idle.** Bounded by the real gas fleet, the statutory
20,000 MW discharges 13 TWh a year and 18 TWh still goes unserved. It is working hard and cannot
close the gap.

**Most of the new gas is a modelling boundary, not a statutory consequence.** New combined-cycle
capacity falls from 6,547 MW with no imports to about 2,000 MW at Virginia's actual 20% import
share. Reported as a range for that reason.

## 1.5 What this does and does not settle

**Does:** which compliance levels are reachable, what each costs, and how sensitive that is to gas
price.

**Does not:** whether any particular plant should be built. This is screening-level analysis. A
procurement decision requires production-cost validation with unit commitment, forced outages and
transmission — a separate tool at a later stage.

---

# LAYER 2 — TECHNICAL SUMMARY

**12–15 pages. For senior engineering staff. How the answer was reached, and how confident to be.**

## 2.1 Scope and method

● The three axes: compliance level (primary), siting overlay, gas price band
● Linear programming, hourly, 8,760 hours per year, twenty years 2026–2045
● Eight weather years on April–March hydro-year boundaries; design year 2016–17
● What is optimised and what is pinned, scenario by scenario

## 2.2 Demand

● Dominion's own hourly projections, 2026–2045, no interpolation
● Virginia-only, North Carolina removed
● **The generation/meter distinction**, and the 1.0925 loss factor — dispatch uses the generation
  basis, statutory obligations the meter basis
● Data-centre growth as the driver; the fourth axis deferred

## 2.3 Capacity planning — is enough built?

● **Metric: installed reserve margin, 17.7%, against accredited capacity at peak net demand**
● PJM effective load carrying capability: 4-hour storage 58%, long-duration 78%, tracking solar 8%,
  offshore wind 67%
● Applied in **every hour**, not only at the peak-net-demand hour
● **What this does not do:** a deterministic margin is a proxy for a loss-of-load study, not a
  substitute. Cole et al. note the margin "receives little attention" as a model input despite being
  a key sensitivity.

## 2.4 Resource adequacy — does it serve load?

● **Metrics: loss-of-load hours, unserved energy, event count, longest event** — per NERC (2026),
  which asks for "duration, magnitude, and severity" and warns that "aggregate metrics like loss of
  load expectation cannot detect" rare severe events
● **What is reported and what is not.** These are realisations under one weather year with no
  forced-outage draws, so they are named `loss_of_load_hours` and `unserved_energy`, not LOLE or
  EUE. Conditional value at risk is not offered: it needs ~375 draws per weather year for a stable
  tail, and eight years give 0.4 observations above the 95th percentile.
● **What would close it:** forced-outage draws on the eight weather years already held — 8 × 375 =
  3,000 scenarios, about 2.5 hours per scenario on commodity hardware. Scoped, not run.

## 2.5 The gas fleet

● Merit-order stack: five rungs, heat rates 6.40 to 11.00, 92% availability derate
● **Two retirement schedules** — physical (A) and VCEA-driven (B) — and why each scenario declares
  its own
● New capacity sized by **brownfield screening curve** (Appendix Q): run-length against minimum
  uptime, costed on capital, fuel, start fuel and maintenance interval
● **Thermal cycling priced, not forbidden**: $645M/yr at 2045, 6% of total
● **Validated against observed behaviour.** Dominion's own 2022–24 capacity factors by rung — 66.8%,
  47.8%, 7.0% — track the modelled heat rates 6.40, 7.55, 11.00 exactly.

## 2.6 The scenarios

● **Scenario 1** — 100% clean by 2045, firmed solar co-located with storage *(pending re-run)*
● **Scenario 1B** — 95% clean, 5% gas from 2045 *(pending)*
● **Scenario 2** — statutory minimums only **(complete)**
● **Scenario 3** — distributed 80/10/10 with FERC 2222 participation *(blocked on siting cap)*

## 2.7 Results

**[CHART: the compliance curve with its gas-price band]** — *pending the sweep*

**Scenario 2, measured:**

| | EIA (low) | Deloitte (medium) | Hughes (high) |
|---|---:|---:|---:|
| 2045 annualised cost | $8.59B | $10.86B | $12.84B |
| clean share at 2045 | 31.6% | 31.6% | 31.6% |
| *system levelised cost* | *$29.59* | *$36.35* | *$37.02* |
| societal cost | $115.96 | $122.33 | $123.12 |

**Gas price changes what the scenario costs, not what it achieves** — the build is statutory, so the
dispatch mix is fixed by what was built.

## 2.8 Limitations that bound every number

● **Imports excluded**, and it accounts for roughly 70% of Scenario 2's new gas
● **No unit commitment** — start costs and minimum run times are priced after the fact, not
  optimised against
● **Deterministic reserve margin**, not loss-of-load expectation
● **Continuous capacity in the LP**, discretised to real units afterwards
● **Part-load heat rates unrepresented**, so the modelled price spread is an upper bound
● **Screening-level throughout.** Güner: the method suits "preliminary investigation... to narrow
  down the technology alternatives for detailed analysis."

---

# LAYER 3 — BODY AND APPENDICES

**For resource planners and modelers. Everything, checkable.**

## 3.1 Body sections

| # | section | state |
|---|---|---|
| 1 | Statutory framework — VCEA, RPS, the 2026 amendments | drafted in parts |
| 2 | Demand basis and its sourcing | working notes exist |
| 3 | Resource modelling — solar, wind, storage, nuclear, gas | partial |
| 4 | Capacity planning method | `Reserves_Approach.md` |
| 5 | Resource adequacy method | `Common_Reference.md` sections 2-3 |
| 6 | Scenario 1 | pending |
| 7 | Scenario 1B | Appendix N |
| 8 | **Scenario 2** | **complete — `scenarios/Scenario2_Working_Document.md`** |
| 9 | Scenario 3 | blocked |
| 10 | Compliance sweep and the headline curve | pending |
| 11 | Siting overlays | pending |
| 12 | Transmission deferral — the secondary objective | pending |

## 3.2 Appendices in place

● **Q** — gas capacity method: brownfield screening curve, formulas, limits, presentation
● **Agrivoltaics** — land use, grazing evidence, cost by configuration
● **N** — Scenario 1B
● **P** — solve procedure and the 17 standing requirements
● **D** — tiered social cost
● **O** — intermediate-year demand shape
● **A7** — data-centre demand flexibility

## 3.3 Registers

● `Master_Citations.xlsx` — 120 citations with topics, evidence type, verification status
● `Virginia_Grid_Analysis_Tracker_updated.xlsx` — 85 activities

---

## What blocks the whitepaper

**The compliance sweep has not run**, and it is the primary axis. It needs Scenario 1 re-run, which
needs the carve-out and siting overlay wired into Scenarios 1, 1B and 3.

**Scenario 2 is the only complete scenario.** Everything in the outline above marked *pending* is
waiting on that chain, not on writing.

**Prior drafts to reconcile.** `docs/whitepaper/Scenario2_Section_Draft.md` holds the current
Scenario 2 text and is the only whitepaper file in the repository. Older drafts of the executive
summary, technical summary and whitepaper body exist outside it and should be brought in or
explicitly superseded before drafting resumes — writing a fourth version alongside three
unreconciled ones would repeat the fragmentation the gas-document merge was undertaken to fix.
