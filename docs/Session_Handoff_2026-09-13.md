# Session Handoff — 2026-09-13

24 commits. 906 tests passing. **Scenario 2 is complete and has an SLCOE.**

---

## The headline result

### Scenario 2 — the baseline — **$32.82/MWh**

Twenty annual solves, 2026–2045, levelised at WACC 4.5% from base year 2026. 1.3 minutes.

| | |
|---|---:|
| PV cost | $74.93B |
| PV demand | 1,977.9 TWh |
| PV terminal value | $10.01B (**13% of PV cost**) |
| **SLCOE without terminal value** | **$37.88/MWh** |
| **SLCOE with terminal value** | **$32.82/MWh** |

**Capex band $32.32–$33.53** — a 3.7% spread. Gas *capex* barely moves this scenario; most of its
cost is **fuel**. The gas *price* band is the axis that will matter.

### The annual resolution changed the story

The four checkpoints showed a straight decline. **It isn't one.** Clean share **rises** from 47.4%
(2026) to a peak near **2030–31** as the statutory solar builds out, then falls to **34.7%** (2045).

**The turning point is where the fixed 16,100 MW target stops keeping pace with demand.** That is a
sharper statement of the whitepaper's thesis than the endpoint alone.

| year | clean | gas peak MW | $B/yr | $/MWh |
|---|---:|---:|---:|---:|
| 2026 | 47.4% | 13,141 | 1.88 | 18.39 |
| 2030 | **49.4%** | 14,938 | 3.38 | 28.71 |
| 2035 | 47.3% | 18,456 | 5.94 | 39.95 |
| 2040 | 37.3% | 22,926 | 8.93 | 47.39 |
| 2045 | **34.7%** | 22,479 | 10.46 | 51.72 |

### Scenario 1 at 100%, for comparison

Solves in 179 s with reserve margin applied. **165,875 MW solar**, 54,153 MW / 372,544 MWh
sodium-ion, 3,805,143 MWh iron-air. **$25.38B/yr on an SLCOE basis, $125.52/MWh at 2045.**

**Curtailment is 161.5 TWh against 202.2 TWh of demand** — the system generates ~364 TWh to serve
202. That is the cost of reaching 100% with solar and storage alone.

*Not yet levelised, and its existing gas FOM is still missing, so the two figures are not fully
comparable.*

---

## Corrections to published figures

| | was | now | why |
|---|---:|---:|---|
| Scenario 2 clean share, 2045 | 39.2% | **34.7%** | post-VCEA solar double-counted |
| Scenario 2 clean share, 2030 | 59.2% | **49.4%** | full solar target built in 2030, 5 years early |
| DOM-zone gas nameplate | 10,503.6 MW | **13,639.4 MW** | CHP filter bug dropped every merchant IPP |
| Winter/summer uplift | 11.4% | **10.1%** | same |
| CCGT/CT crossover CF | ~41% (estimate) | **28.1%** | estimate used wrong capex and omitted FOM |

---

## Defects found and fixed

**CHP filter bug.** `~Sector.str.contains('CHP')` excluded `'IPP Non-CHP'` — every merchant
independent producer. **Doswell 1,313 MW, Tenaska 1,011, Potomac Energy Center 812 = 3,136 MW,
~30% of the DOM-zone fleet.** Undetected because the filter was self-consistently wrong.

**Export revenue in the Scenario 2 objective** — violating Appendix P.2 #8, a standing project-wide
rule, and the *second* occurrence of the same bug. No figure moved: the export bound was already
pinned to `(0,0)`, so **one correct guard was masking an incorrect term.**

**`solve_checkpoint.py` re-solved a different problem** — no `capacity_cap_mw`, no `prior_*`. Every
dual and hourly dispatch from it described an unlinked checkpoint. Found because a night-curtailment
diagnostic showed ~4,300 MW of supply against ~47,900 MW of sinks with zero unserved.

**`converge_frac` could not converge and did not say so.** Proportional rescale closed the gap ~40%
per iteration against `max_iter=3`; now bisection with `max_iter=8`, and results carry `converged`.

**`CCGT_CAPEX_KW` defined twice** — a superseded scalar in `lp_model` (re-aliased one line after
being renamed `_DO_NOT_USE_SUPERSEDED`) and a band I added in `gas_lifecycle_cost`.

**`demand_shape_interpolation` could not load its own base shape** — hardcoded path to a file layout
that does not exist.

**Scenario 2 had never run through its solver class** — six arguments passed to a function requiring
thirteen.

---

## The recurring pattern, now automated

**Seven instances** of a component built, documented as the standard, and never wired in:
`all_hours_reserve`, the `t_peak` rename, the `CCGT_CAPEX_KW` re-alias, `demand_shape_interpolation`,
the distributed iron-air exclusion, `distributed_physical_bounds`, and Appendix P itself.

Each was found **by hand, months apart**. `scripts/audit_documented_fixes.py` now checks:

- **conflicting duplicate constants** (Rule 6) — 256 constants, no conflicts
- **orphaned modules** (Rule 1) — transitive from entry points
- **export revenue in objectives** (P.2 #8)
- plus the original three

**Two of my own checks passed vacuously before working** — a mangled regex matching nothing, and a
non-transitive walk. Both looked like clean bills of health.

---

## Appendix P is now in the repository

`docs/appendices/Appendix_P_Solve_Procedure.md` — 811 lines, **thirteen general solve requirements**
that no code had been checked against. #8 (export) is now enforced. **Twelve remain unaudited**,
including #11, *"Verification required before any solve is presented as final."*

**#7 settles the demand basis:** *"this project's Virginia-only demand total, adjusted for the
flattening effect of data-center load growth described in Appendix O."*

---

## What that settled about demand

Four competing series existed. **Ours is correct** — and needs no adjustment, because **Dominion's
own projections already flatten**:

| | load factor |
|---|---:|
| source 2024 | 0.652 |
| source 2045 | **0.794** |
| `demand_shape_interpolation` 2045 | 0.712 |

**Applying the module would make the shape *less* flat** — peak +11.8% at 2045. It was built to age
a single fixed shape forward; the demand stage no longer works that way. Marked **SUPERSEDED — do
not wire into a solve path**, retained for its sourced IRP series.

**And no interpolation is needed at all** — the source covers 2026–2045 with no gaps.

---

## Built this session

| module | purpose |
|---|---|
| `levelised_cost.py` | `PV(cost)/PV(demand)`, terminal value, gap detection |
| `scenario_lifecycle_cost.py` | annual cost; two constructors, because the two objectives differ |
| `gas_lifecycle_cost.py` | capital on new build only; CCGT/CT crossover |
| `supply_gap_analysis.py` | gap characterisation for technology matching |
| `scenario2_all_hours_reserve.py` | reserve test for Scenario 2's own problem shape |
| `pathway_comparison.py` | myopic chain vs target-first |
| `run_scenario2_slcoe.py` | the twenty-year runner |
| `compute_tier123_final.py` | **restored** — social costs were unavailable |

---

## Open at P1

| # | |
|---|---|
| **#20** | `distributed_physical_bounds` never wired — **every Scenario 3 result is unbounded** |
| **#19** | gas as a build variable — blocks the CCGT/CT split *and* the counterfactual |
| **#18** | merit order caps gas below the scenario; no new-build rung |
| **#17** | merit order costs 3.8× solve time |
| #2 | `all_hours_reserve` dormant |
| #1 | 2045 dual unmeasured |
| #14 | siting cap on a discredited per-capita basis |

---

## Next

**Build interpolation between checkpoints for Scenarios 1 and 3.** Scenario 2 needed none — its
build is statutory. Scenarios 1 and 3 optimise their builds, so intermediate years need the build
carried forward at annual granularity. **That is the last piece before the sweep.**

Then, per the agreed sequence: the sweep at MEDIUM gas from 100% down to ~35%, the gas-price band,
and overlays on the most interesting points.

### Known gaps carried forward

- **Appendix O is missing** and P.2 #7 cites it normatively — partly reconstructible from
  `demand_shape_interpolation`
- **Existing gas FOM** absent on the Scenario 1 side
- **Twelve P.2 requirements** unaudited
- **Residual value on a pathway** — a CT built 2035 and stranded 2045 is charged 10 years of a
  30-year annuity; late-built gas looks cheap when it is very expensive
- **`init_soc_frac=0.5`**, **`c[IDX['nd']] = 100.0`** (18× sourced cycling cost), and
  **`GAS_COST_MWH` evaluated at a hardcoded 2044.5** — all recorded, none fixed
