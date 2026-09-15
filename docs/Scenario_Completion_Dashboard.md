# Scenario completion dashboard

**Status as of 2026-09-14.** One row per step per scenario. A step is **done** only when its result
has been produced on the current code and constants — not when the code to produce it exists.

**The gas fleet reference is `docs/methodology/Gas_Consolidated_Reference.md`**, rebuilt against
Dominion's 2024 Annual Report. Any figure from an earlier whitepaper draft, IRP summary or
third-party database is superseded by it and should not be carried forward.

---

## Legend

● **done** — result produced on current code and constants
● **ready** — code complete and audited, not yet run
● **blocked** — cannot proceed until the listed issues are resolved
● **not started**

---

## Scenario 2 — Statutory Minimums

The reference case: build only the 16,100 MW solar and 20,000 MW storage the Code names, meet the
rest with gas. No reserve-margin constraint by design.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired and verified | **done** | — |
| 2 | Four-checkpoint pathway | **done** | — |
| 3 | Twenty-year annual stream | **done** | — |
| 4 | SLCOE, central case | **done** — $32.80/MWh | — |
| 5 | Capex sensitivity band | **done** — $32.30–$33.51 | — |
| 6 | Social + health cost, all 20 years | **done** — $119.48/MWh societal | — |
| 7 | Whitepaper section drafted | **superseded** | see below |
| 8 | Statutory distributed carve-out | **not started** | profile built; not wired |
| 9 | Gas price band (Deloitte MED/HIGH, EIA) | **not started** | — |
| 10 | Unit commitment sensitivity | **blocked** | #17 |

> ### SUPERSEDED 2026-09-14 — the statutory distributed carve-out
>
> Va. Code § 56-585.5(C)(2), as raised by the **Distributed Generation Expansion Act (HB 628 /
> SB 175, 2026)**, requires **4.5% of RPS (2026–2030) and 5% (2031–2045)** from sub-1 MW
> behind-the-meter resources. **No scenario currently builds any.**
>
> | year | share | energy | MW at 15.26% CF |
> |---|---:|---:|---:|
> | 2026 | 4.5% | 4.60 TWh | 3,445 |
> | 2030 | 4.5% | 5.31 TWh | 3,970 |
> | 2045 | **5.0%** | **10.11 TWh** | **7,565** |
>
> **7,565 MW at 2045 is 47% of the entire 16,100 MW statutory solar target**, arriving as
> distributed capacity nothing currently models. It displaces gas, so Scenario 2's clean share
> **rises above 34.7%** and its SLCOE moves.
>
> **Steps 1–7 must be re-run.** The $32.80/MWh figure and the drafted whitepaper section both
> predate this.

### Findings carried forward

● Clean share **47.4% → 34.7%**, peaking near 2030–31. A fixed solar target cannot hold against 72%
  demand growth.
● **The mandated storage never operates** — zero charge, discharge and curtailment in all 8,760
  hours of 2045. Solar delivers 41.3 TWh against 202.2 TWh of demand.
● The **$3.4B/yr of idle storage capital** carries a caveat: the model offers storage nothing to
  arbitrage (#3, and flat annual gas pricing), so mandate mismatch and modelling boundary cannot be
  separated.

---

## Scenario 1 — 100% Clean by 2045

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired, all-hours reserve applied | **done** | — |
| 2 | Four-checkpoint pathway | **superseded** — needs re-run | #24 |
| 3 | Twenty-year annual stream | **ready** | depends on step 2 |
| 4 | SLCOE | **not started** | depends on step 3 |
| 5 | Social + health cost, all 20 years | **not started** | depends on step 3 |
| 6 | Myopic vs perfect-foresight comparison | **blocked** | #22 |
| 7 | Statutory distributed carve-out | **not started** | profile built; not wired |
| 8 | Whitepaper section | **not started** | depends on step 4 |

**Step 2 is the gate.** The prior run predates Bath County's correction to Dominion's 1,808 MW
share, which moves every dispatch result. #24 asks whether `checkpoint_solver`'s remaining parallel
constructions are still justified — worth settling in the same pass, since both touch the solver.

### Findings from the superseded run, to re-confirm

● **59.1% of the solar fleet arrives in the final checkpoint** — 92,622 MW at 2045 against 64,114 MW
  cumulative through 2040. The delay-then-overbuild pattern.
● **142.1 TWh curtailed against 202.2 TWh served** — the system generates ~344 TWh to deliver 202.

---

## Scenario 1B — 95% Clean, 5% Gas from 2045

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver and reserve variant | **done** | — |
| 2 | Capacity sweep result implemented (6,000 MW) | **done** | — |
| 3 | Five-checkpoint pathway incl. 2044 | **superseded** — needs re-run | #24 |
| 4 | Twenty-year annual stream | **not started** | no runner yet |
| 5 | SLCOE | **not started** | depends on step 4 |
| 6 | Social + health cost | **partial** — per checkpoint only | depends on step 4 |
| 7 | Statutory distributed carve-out | **not started** | profile built; not wired |
| 8 | Whitepaper section | **not started** | depends on step 5 |

**Same gate as Scenario 1.** Step 4 has no runner: `run_scenario1_annual.py` is Scenario 1 specific
and would need the five-checkpoint set and 1B's 2045 capacity.

### Findings from the superseded run, to re-confirm

● **Gas reaches 4.27% of the statutory base and cannot reach 5%** — the search saturates across a
  tripling of the allowance. The binding constraint is fleet capacity, not the RPS percentage.
● **2045 builds nothing.** 2044's own RPS target is already 5% gas, so its build covers 2045.

---

## Scenario 3 — Distributed 80/10/10

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver, reserve variant, distributed bounds | **done** | — |
| 2 | Four-checkpoint pathway | **not started** | #14, #24 |
| 3 | Twenty-year annual stream | **not started** | depends on step 2 |
| 4 | SLCOE | **not started** | depends on step 3 |
| 5 | DER owner economics | **blocked** | #5, #15 |
| 6 | Transmission-deferral assessment | **not started** | #4 |
| 7 | Social + health cost | **not started** | depends on step 3 |
| 8 | Whitepaper section | **not started** | depends on step 4 |

**Least advanced, and #14 is the substantive blocker**: the distributed siting cap rests on a
per-capita basis that has been discredited and needs re-deriving on commercial and industrial floor
area. Every Scenario 3 capacity figure depends on it.

**Also the most expensive to run** — the distributed segment costs roughly 9× the solve time.

---

## The distributed profile — built, not yet wired

`lp_package/distributed_solar_profile.py`, 2026-09-14. Five sites averaged — Sterling, Arlington,
King George, Richmond, Chesapeake — at **45° due south, fixed**, on the same April–March hydro-year
boundaries as every other weather input.

| hydro year | CF | | hydro year | CF |
|---|---:|---|---|---:|
| 2012-13 | 0.1499 | | 2016-17 *(design)* | **0.1526** |
| 2013-14 | 0.1524 | | 2017-18 | 0.1521 |
| 2014-15 | 0.1497 | | 2018-19 | **0.1420** |
| 2015-16 | 0.1501 | | 2019-20 | 0.1465 |

**The design year is the best of the eight.** The robustness run will see less distributed output
than the design-year solve assumes — 0.1420 against 0.1526.

**45° is not a yield sacrifice.** Against 15°, measured at Sterling 2016: December **+31.5%**,
January **+29.9%**, June −17.5%, and the **year +1.3%**. The December-to-June ratio moves from 0.45
to 0.71 — a far more even year, with the gain landing where peaks, outages and price spreads are.

**No paired storage.** The DER expansion text sets none for distributed resources; the obligation
rests with the utility under § 56-585.5(E).

---

## Cross-scenario

| # | step | status | blockers |
|---|---|---|---|
| 1 | Compliance sweep, 30–100% | **not started** | S1 step 2 |
| 2 | Gas price band across the sweep | **not started** | sweep |
| 3 | Siting overlay (utility / 20% distributed / 85% agrivoltaic) | **not started** | #14, S3 |
| 4 | Data-centre demand axis | **not started** | deferred by decision |
| 5 | Final chart: annualised cost vs compliance level | **not started** | all of the above |

**The sweep runs to 30%, not 75%.** Scenario 2 achieves **34.7%** clean at 2045, so a sweep stopping
at 75% would leave the reference case off its own axis — plotted as a detached point with nothing
to read it against. Extending the lower bound puts Scenario 2 **on** the curve, which is what makes
"what does the statutory minimum buy, and what would more buy" a single readable comparison rather
than two separate claims.

**The floor is 30%, not 35%, so the reference case sits inside the range rather than at its edge.**
A point at the very end of an axis reads as a boundary rather than a result, and leaves no room to
show that compliance below the statutory minimum costs more than it saves.

Density still concentrates at the top: 100, 95, 90, 85, 80, 75, then coarser steps down to 30.

---

## Blocking issues, by weight

| # | title | blocks |
|---|---|---|
| **#24** | `checkpoint_solver` parallel constructions | S1 step 2, S1B step 3, S3 step 2 |
| **#14** | Distributed siting cap on a discredited basis | all of S3, overlay |
| **#22** | Perfect-foresight salvage and unserved energy | S1 step 6 |
| #17 | Merit order solve time | S2 step 9 |
| #5, #15 | DER foresight and revenue stack | S3 step 5 |
| #4 | Nodal prices | S3 step 6 |
| #3 | No import capability | caveats every result; blocks none |

**#24 is on the critical path** — it gates the re-run that three scenarios depend on, and the sweep
depends on Scenario 1.

---

## Known limitations that caveat every scenario

These block nothing and will not be resolved before publication. Each is recorded in Appendix P.2.

● **No imports** (#3). Virginia imports roughly 20% of its energy. Excluding it makes every scenario
  build more in-state capacity than needed, so **every cost is overstated** — conservative, but not
  neutral.
● **Flat gas price within each year.** Real PJM Mid-Atlantic prices show a $45.92 overnight-to-peak
  spread. Storage can absorb surplus but never arbitrage, so idle storage may be a modelling
  artifact rather than an economic result.
● **No unit commitment** (#17). Minimum run times and start costs are what create the intra-day
  spread, and they are absent.
● **Decommissioning and scrap both omitted.** Schedule B retires 7,502 MW of gas at 2045. The scrap
  value and the demolition liability partly offset; neither is costed for want of sourced figures.
