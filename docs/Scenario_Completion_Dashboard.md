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
| 7 | Whitepaper section drafted | **done** | — |
| 8 | Gas price band (Deloitte MED/HIGH, EIA) | **not started** | — |
| 9 | Unit commitment sensitivity | **blocked** | #17 |

**Complete for its primary purpose.** Steps 8 and 9 are sensitivities, not prerequisites.

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
| 7 | Whitepaper section | **not started** | depends on step 4 |

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
| 7 | Whitepaper section | **not started** | depends on step 5 |

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

## Cross-scenario

| # | step | status | blockers |
|---|---|---|---|
| 1 | Compliance sweep, 75–100% | **not started** | S1 step 2 |
| 2 | Gas price band across the sweep | **not started** | sweep |
| 3 | Siting overlay (utility / 20% distributed / 85% agrivoltaic) | **not started** | #14, S3 |
| 4 | Data-centre demand axis | **not started** | deferred by decision |
| 5 | Final chart: annualised cost vs compliance level | **not started** | all of the above |

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
