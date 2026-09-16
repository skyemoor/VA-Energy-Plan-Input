# Scenario completion dashboard

**Updated whenever a step's status changes on any scenario.** Status as of 2026-09-14. One row per step per scenario. A step is **done** only when its result
has been produced on the current code and constants — not when the code to produce it exists.

**The gas fleet reference is `docs/methodology/Gas_Consolidated_Reference.md`**, rebuilt against
Dominion's 2024 Annual Report. Any figure from an earlier whitepaper draft, IRP summary or
third-party database is superseded by it and should not be carried forward.

---

## Legend

● **done** — result produced on current code, constants and scenario definition
● **re-check** — result may still hold, but an input to it has changed
● **ready** — code complete and audited, not yet run
● **blocked** — cannot proceed until the listed issues are resolved
● **not started**

---

## Scenario 2 — Statutory Minimums

The reference case: build only the 16,100 MW solar and 20,000 MW storage the Code names, meet the
rest with gas. No reserve-margin constraint — adequacy is bounded by the merit-order stack instead,
which caps gas at the real fleet and surfaces any shortfall as unserved energy.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired and verified | **superseded** | steps 2, 3 |
| 2 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 3 | Agrivoltaic siting, applied evenly | **not started** | — |
| 3a | Merit-order stack in the solver | **done** | — |
| 3b | Gas capacity fit on the measured gap | **done** | — |
| 4 | Four-checkpoint pathway | **superseded** | steps 2, 3 |
| 5 | Twenty-year annual stream | **superseded** | steps 2, 3 |
| 6 | SLCOE + capex band | **superseded** | steps 2, 3 |
| 7 | Social + health cost | **superseded** | steps 2, 3 |
| 8 | Whitepaper section | **superseded** | steps 2, 3 |
| 9 | New gas capacity costed into the SLCOE | **not started** | steps 2, 3 |
| 10 | Gas price band (Deloitte MED/HIGH, EIA) | **not started** | — |
| 11 | Unit commitment sensitivity | **blocked** | #17 |

**Two changes to the scenario definition supersede the completed run.** The
$32.80/MWh SLCOE is a clean result on a specification we have since revised, not a wrong
result — see build log 140.

● **The distributed carve-out is statutory and unbuilt.** 4.5% of RPS (2026–2030) and 5%
  (2031–2045) from resources ≤1 MW, per § 56-585.5(C)(2) as raised by HB 628 / SB 175.
  **7,565 MW by 2045**, which is 47% of the 16,100 MW solar target. It displaces gas, so
  clean share rises above 34.7% and cost moves.
● **Agrivoltaic siting should apply to every scenario, not Scenario 3 alone.** It changes
  cost and land, not compliance.

**Order matters:** carve-out first, since it changes the build; agrivoltaics second, as an
overlay on whatever build results.

### Findings carried forward

● Clean share **47.4% → 34.7%**, peaking near 2030–31. A fixed solar target cannot hold against 72%
  demand growth.
● **The mandated storage never operates** — zero charge, discharge and curtailment in all 8,760
  hours of 2045. Solar delivers 41.3 TWh against 202.2 TWh of demand.
● **The storage is not idle — it is insufficient.** With the merit order bounding gas at the real
  fleet, sodium-ion discharges **13.04 TWh over 2,666 hours** and **17.96 TWh still goes unserved**.
  The earlier idle-storage finding was an artifact of unbounded gas. Not arbitrage but scarcity: the
  alternative to discharging is unserved energy at the penalty price.
● **The 2045 capacity gap is 10,263 MW of peaking duty** — 1,233 blocks, median 2 hours, clearing no
  combined-cycle minimum uptime at any level. Combustion turbine beats combined cycle by
  **$1,365M/yr**, on capital, maintenance, capacity factor and duty shape alike. Appendix Q.3a.
● **Fuel was understated by $11.90/MWh** at a flat 6.40 heat rate; the stack gives 8.12.

---

## Scenario 1 — 100% Clean by 2045

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired, all-hours reserve applied | **superseded** | steps 7, 8 |
| 2 | Four-checkpoint pathway | **superseded** | #24, steps 7, 8 |
| 3 | Twenty-year annual stream | **ready** | depends on step 2 |
| 4 | SLCOE | **not started** | depends on step 3 |
| 5 | Social + health cost, all 20 years | **not started** | depends on step 3 |
| 6 | Myopic vs perfect-foresight comparison | **blocked** | #22 |
| 7 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 8 | Agrivoltaic siting, applied evenly | **not started** | — |
| 9 | Whitepaper section | **not started** | step 4 |

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
| 1 | Solver and reserve variant | **superseded** | steps 7, 8 |
| 2 | Capacity sweep result implemented (6,000 MW) | **re-check** | steps 7, 8 |
| 3 | Five-checkpoint pathway incl. 2044 | **superseded** | #24, steps 7, 8 |
| 4 | Twenty-year annual stream | **not started** | no runner yet |
| 5 | SLCOE | **not started** | depends on step 4 |
| 6 | Social + health cost | **partial** — per checkpoint only | depends on step 4 |
| 7 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 8 | Agrivoltaic siting, applied evenly | **not started** | — |
| 9 | Whitepaper section | **not started** | step 5 |

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
| 1 | Solver, reserve variant, distributed bounds | **superseded** | step 8 |
| 2 | Four-checkpoint pathway | **not started** | #14, #24 |
| 3 | Twenty-year annual stream | **not started** | depends on step 2 |
| 4 | SLCOE | **not started** | depends on step 3 |
| 5 | DER owner economics | **blocked** | #5, #15 |
| 6 | Transmission-deferral assessment | **not started** | #4 |
| 7 | Social + health cost | **not started** | step 3 |
| 8 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 9 | Whitepaper section | **not started** | step 4 |

**Least advanced, and #14 is the substantive blocker**: the distributed siting cap rests on a
per-capita basis that has been discredited and needs re-deriving on commercial and industrial floor
area. Every Scenario 3 capacity figure depends on it.

**Also the most expensive to run** — the distributed segment costs roughly 9× the solve time.

---

## The distributed profile — built, not yet wired

`lp_package/distributed_solar_profile.py`. Five sites averaged — Sterling, Arlington, King George,
Richmond, Chesapeake — at **45° due south, fixed**, on April–March hydro-year boundaries. Design
year CF **0.1526**; eight-year range 0.1420–0.1526, so the robustness run sees ~7% less than the
design-year solve assumes. No paired storage: the DER expansion text requires none.

Derivation and evidence in build log 135; tilt reasoning in `distributed_solar_profile.__doc__`.

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

**The merit-order stack is available to all four scenarios.** `build_problem` has carried it since
before this session; `build_scenario2_problem` gained it 2026-09-14. It is opt-in, so no published
result moves until a scenario enables it — but every scenario's fuel is understated until one does,
because a single-rung model burns at the best heat rate in the fleet in every hour.

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
