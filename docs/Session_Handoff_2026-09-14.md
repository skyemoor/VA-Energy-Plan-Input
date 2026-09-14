# Session Handoff — 2026-09-13 / 14

36 commits. 997 tests passing. **All 9 audit checks pass for the first time since the audit was
written.**

---

## Results produced

### Scenario 2 — the baseline — **$32.82/MWh**

Twenty annual solves, 2026–2045, levelised at WACC 4.5% from base year 2026. 1.3 minutes.

| | |
|---|---:|
| PV cost | $74.93B |
| PV demand | 1,977.9 TWh |
| PV terminal value | $10.01B (13% of PV cost) |
| **SLCOE without terminal value** | **$37.88/MWh** |
| **SLCOE with terminal value** | **$32.82/MWh** |

Capex band **$32.32–$33.53** — 3.7%. Gas *capex* barely moves this scenario; most of its cost is
**fuel**. The gas *price* band is the axis that will matter.

**The annual resolution changed the story.** Four checkpoints showed a straight decline; it is not
one. Clean share **rises** from 47.4% (2026) to a peak near **2030–31** as the statutory solar
builds out, then falls to **34.7%** (2045). **The turning point is where the fixed 16,100 MW target
stops keeping pace with demand.**

### Scenario 2 — social and environmental cost

Across all twenty years per P.2 §9, on the same PV basis as the financial figure:

| tier | PV | $/MWh |
|---|---:|---:|
| **Virginia SCC** (CO₂ only, statutory) | $145.78B | **$73.71** |
| **Social cost of GHG** (CO₂+CH₄+N₂O) | $160.51B | **$81.15** |
| **Health impacts** (PM, SO₂, NOx) | $10.87B | **$5.50** |
| **TOTAL SOCIETAL SLCOE** | | **$119.47/MWh** |

**The climate externality is ~2.5× the direct cost.** Tier 1 reported as two figures, never
combined, per Va. Code §56-598(2)(d).

Against Appendix D's prior figures ours run **11.4% higher on both climate tiers** — an identical
proportion, which points at gas *volume* rather than emission factors or the SC-GHG schedule.

### Scenario 1 at 2045, 100% — superseded twice in one session

| | $5/MWh curtailment | **$25/MWh** |
|---|---:|---:|
| Solar | 165,875 MW | **156,737 MW** |
| Iron-air | 3.81 TWh | **4.77 TWh** |
| Curtailment | 161.5 TWh | **142.1 TWh** |
| Objective | $26.07B | **$29.10B** |

**Curtailment is 142.1 TWh against 202.2 TWh of demand** — the system generates ~344 TWh to serve
202. That is the cost of reaching 100% with solar and storage alone.

---

## Corrections to published figures

| | was | now | cause |
|---|---:|---:|---|
| S2 clean share, 2045 | 39.2% | **34.7%** | post-VCEA solar double-counted |
| S2 clean share, 2030 | 59.2% | **49.4%** | full solar target built 5 years early |
| DOM-zone gas nameplate | 10,503.6 MW | **13,639.4 MW** | CHP filter bug |
| Winter/summer uplift | 11.4% | **10.1%** | same |
| CCGT/CT crossover | ~41% | **28.1%** | wrong capex, FOM omitted |
| Curtailment cost | $5/MWh | **$25/MWh** | regression from $100, then capped by the resistor threshold |

---

## Defects found and fixed

**CHP filter bug.** `~Sector.str.contains('CHP')` excluded `'IPP Non-CHP'` — **3,136 MW, ~30% of the
DOM-zone fleet** (Doswell, Tenaska, Potomac Energy Center). Undetected because the filter was
self-consistently wrong.

**`solve_checkpoint.py` re-solved a different problem** — no `capacity_cap_mw`, no `prior_*`. Every
dual and dispatch from it described an unlinked checkpoint. Found because a diagnostic showed ~4,300
MW of supply against ~47,900 MW of sinks with zero unserved.

**`converge_frac` could not converge and did not say so.** Proportional rescale against `max_iter=3`;
now bisection at 8. **And the flag it sets never reached a caller** — four convergence paths all
discarded the result carrying it.

**Export revenue in the Scenario 2 objective**, violating P.2 §8 — the *second* occurrence. No
figure moved: the export bound was already `(0,0)`, so **one correct guard was masking an incorrect
term.**

**Curtailment cost regressed** from $100/MWh to $5. `build_dispatch_problem` carried a comment
claiming it matched `build_problem` — which had **no curtailment cost at all**.

**`CCGT_CAPEX_KW` defined twice** — a superseded scalar re-aliased one line after being renamed
`_DO_NOT_USE_SUPERSEDED`, and a band I added without checking `assumptions` first.

**Scenario 2 had never run** — six arguments passed to a function requiring thirteen.

**`demand_shape_interpolation` could not load its own base shape** — hardcoded path to a layout that
does not exist.

---

## The storage-resistor threshold

Restoring $100/MWh produced **4,710 hours of simultaneous Na-ion charge/discharge**. The mechanism is
economic: charge 100 MWh, discharge 90, absorb the 10 MWh round-trip loss at `cycling × RTE/(1−RTE)`
per MWh absorbed.

| storage | threshold at 2045 |
|---|---:|
| **Bath pumped hydro** | **$30.00** |
| sodium-ion | $48.06 |
| iron-air | $70.08 |

**Verified empirically:** $28 → 0 hours, $30 → 0, **$32 → 121 Bath hours** at 1,463 MW overlap. Only
Bath breaks, as derived.

**The conflict is disclosed, not tuned.** `CURTAILMENT_COST_MWH = 25.0` is **model-constrained, not
economically derived**; `CURTAILMENT_COST_ECONOMIC_MWH = 100.0` is retained so the gap stays visible.
The model cannot represent the higher figure without structural complementarity, which P.2 §13
records as proven correct but impractical.

**Storage carries no VOM** — only wear-based cycling costs. Issue **#21**. A plausible $0.50–$2.00
moves Bath's threshold to $32–$38; reaching $100 needs $17.50/MWh, implausible for pumped hydro.

---

## The build-document-never-wire pattern

**Nine instances**, each previously found by hand months apart:

`all_hours_reserve` · the `t_peak` rename · the `CCGT_CAPEX_KW` re-alias · `demand_shape_interpolation`
· the distributed iron-air exclusion · `distributed_physical_bounds` · Appendix P itself ·
`run_solve`'s `post_build_hook` · `compute_tier123_final`

**Now automated.** `scripts/audit_documented_fixes.py` runs 9 checks: conflicting duplicate
constants (Rule 6), orphaned modules (transitive from entry points), export revenue in objectives
(P.2 §8), curtailment cost presence *and* agreement, plus the original five.

**Two of my own checks passed vacuously before working** — a mangled regex matching nothing, and a
non-transitive walk. Both looked like clean bills of health.

---

## Documentation recovered

**The repo held a truncation.** `Reorganized_Appendices_Draft_updated.md` is 61 KB; the full draft is
275 KB.

| appendix | full | was in repo |
|---|---:|---:|
| C | 711 | 36 (stub) |
| D | 412 | 13 (stub) |
| M | 428 | **0** |
| N | 192 | **0** |
| **O** | **142** | **0** |
| **P** | **940** | **0** |

That explains everything reported as "lost" this session. **None were lost.**

**Appendix P** — 811 lines of solve requirements no code had been checked against. §8 now enforced;
**twelve remain unaudited**, including §11.

**Appendix O** answered the NC-load question: both source tables are **Virginia-only**. The gap is a
*vintage* difference, not geography.

---

## The demand question, settled

Four competing series existed. **Ours is correct and needs no adjustment** — Dominion's own
projections already flatten:

| | load factor |
|---|---:|
| source 2024 | 0.652 |
| source 2045 | **0.794** |
| `demand_shape_interpolation` 2045 | 0.712 |

Applying the module would make the shape **less** flat (peak +11.8%). It was built to age a single
fixed shape forward; the demand stage no longer works that way. Marked **SUPERSEDED — do not wire
into a solve path**.

**And no interpolation is needed anywhere** — the source covers 2026–2045 with no gaps.

---

## Built this session

| module | purpose |
|---|---|
| `levelised_cost.py` | `PV(cost)/PV(demand)`, terminal value, gap detection |
| `scenario_lifecycle_cost.py` | annual cost; two constructors, because the two objectives differ |
| `gas_lifecycle_cost.py` | capital on new build only; CCGT/CT crossover |
| `storage_resistor_threshold.py` | the derivation, and the disclosure |
| `multi_period_problem.py` | **perfect-foresight assembler** — validated to 1.45e-14 |
| `supply_gap_analysis.py` | gap characterisation for technology matching |
| `scenario2_all_hours_reserve.py` | reserve test for Scenario 2's own problem shape |
| `pathway_comparison.py` | myopic chain vs target-first |
| `run_scenario2_slcoe.py` | the twenty-year runner |
| `run_foresight_comparison.py` | **the next thing to run** |
| `compute_tier123_final.py` | **restored** — social costs were unavailable |

---

## Foresight: the technique, corrected by citations

**"Solve 2045 first and work backwards" appears nowhere in the literature.** Perfect foresight is a
**single simultaneous solve** — *"optimizing all variables over the whole time frame in a single run,
thus determining the global optimum"* (PERSEUS-NET).

Our own `Experiment_Pathway_Foresight.md` already said this as Case 2. I proposed three alternatives
that were all inventions before reading it closely enough.

**The assembly is small** because `build_problem` puts build variables at fixed positions 0–7 in
every period: four periods stack block-diagonally with **24 linking rows**. 735,872 variables,
912,524 rows, 2.9M nonzeros.

**Salvage is mandatory** — *"Type 1 with salvage value"* (Brown) — and applied to **both** sides, so
the comparison measures foresight rather than salvage treatment.

**Validated unlinked against standalone solves: 1.45e-14 relative.** There is no other baseline,
because the linked result *is* what is being measured.

---

## Next

```bash
python3 run_foresight_comparison.py --scenario 1
```

Five solves; the foresight one is ~4× a checkpoint, so 30–60 minutes for it alone. Watch for a
**negative penalty**, which the runner flags rather than reports — it would mean the two sides are
not comparable.

Then the compliance sweep, per the agreed sequence: MEDIUM gas, 2045, **down to ~35%** so Scenario 2
sits on the axis; then the gas-price band; then overlays.

### Open at P1

| # | |
|---|---|
| **#19** | gas as a build variable — blocks the CCGT/CT split *and* the counterfactual |
| **#18** | merit order caps gas below the scenario; no new-build rung |
| **#17** | merit order costs 3.8× solve time |
| #1 | 2045 dual unmeasured |
| #14 | siting cap on a discredited per-capita basis |

### Known gaps carried forward

- **Twelve P.2 requirements unaudited**, including §11 on verification before a solve is final
- **Existing gas FOM** absent on the Scenario 1 side
- **Scenario 3 has never been run** with `distributed_physical_bounds` applied — every prior figure
  superseded
- **`init_soc_frac=0.5`** and **`c[IDX['nd']] = 100.0`** (18× the sourced cycling cost) both
  unsourced
- **Residual value on a pathway** — a CT built 2035 and stranded 2045 is charged 10 years of a
  30-year annuity

---

# Addendum — later on 2026-09-14

Eleven further commits. **1,062 tests, 14 audit checks** (was 9).

## Scenario 1B — two defects, found by auditing before building

**N.2 locked in 6,000 MW; N.4 solved at 4,722.** The capacity sweep selected 6,000 MW total
(1,278 MW new simple-cycle CT) after costing each capped capacity as LP objective *plus*
externally-priced capex. N.4 then solved at 4,722 MW — N.2's own *"existing only"* row, costing
**$10,065.2M against $9,469.3M**. It solved the configuration the sweep rejected, and the 1,278 MW
was never in the code at all.

**The arithmetic closes exactly:** 4,722 (existing + pool) + 1,278 (new CT) = 6,000.

**Invalidated:** N.4's **1.63%** gas share and its conclusion that *"the 5% statutory ceiling is
largely moot."* Both marked superseded in Appendix N, at the section *and* in the body.

**And 1B had no reserve-margin variant** — it solved with none while Scenarios 1 and 3 carried the
all-hours constraint.

**2044 is now a checkpoint.** Its RPS target is 5% gas, which *is* 1B's 2045 target, so 1B's 2045
build should equal its 2044 build. Linking 2045 back to 2040 is what produced the *"wildly oversized
2045 buildout"* N.4 records correcting.

### An independent cross-check

`select_overhaul_retain()` — written for another purpose, never called — reproduces N.2's figure:

```
6,000 target − 1,860 Schedule B survivors − 2,862 POOL = 1,278 MW
N.2's capacity sweep, separately:                        1,278 MW
```

**And surfaces what the sweep couldn't see:** F-Class units are 237 MW, so 1,278 takes **six —
1,422 MW**, overshooting by 144. Both now reported: 1,278 for cost, 1,422 for procurement.

## The foresight solve failed, and the cause was a parallel construction

**41,718 MWh unserved at 2030**, where the myopic solve had none on the same inputs.

`run_perfect_foresight` called `build_problem` directly, skipping every post-build step `run_solve`
performs — the capacity cap, the VCEA storage floors, and **`min_na_duration_hr=6.0`**. Without the
duration floor the LP builds cheap power-only storage that can't sustain an evening, and accepts
unserved at $100,000/MWh rather than build usable capacity.

**Fixed by not reimplementing it.** `run_solve` gains `build_only=True`. Parallel construction is
what caused the drift.

## Convergence: measured, not projected

The bracketed secant halved it. **23 iterations → 13, ~30 min → ~19 min.**

| checkpoint | before | after |
|---|---:|---:|
| 2030 | 8 | **4** |
| 2035 | 7 | **3** |
| 2040 | 7 | 5 |

*Root-finding on a monotone function, not gradient descent — one crossing, no local minima. That is
what makes a secant step safe and the bracket a sufficient net.*

## Salvage: two basis errors, both caught before publication

**Capital versus annuity.** `build_problem` charges build variables as `CRF × capex × 1000` — an
*annual* cost. Crediting raw capital made salvage **$6.50B against a $4.13B objective**. On the
annuity basis it is **$0.32B**.

**Different asset sets per runner.** `run_scenario1` credited solar only; the foresight runner
credited four. At 2030 that is **$0.326B against $0.779B — 2.4×**, and the whole difference would
have landed in the myopia penalty. One implementation now.

## Dead code, and the pattern of creating it

| removed | why |
|---|---|
| `run_solve_multi_duration` | no caller; lacked every `prior_*`, so it could not chain across checkpoints |
| `build_problem_multi_duration` + 2 helpers | **orphaned by that deletion** — 178 lines |
| `_build_value` | **orphaned by the salvage extraction** |
| three demand-existence guards | checked for a file no longer read |

**Twice in two days I removed a caller without checking what it uniquely reached.** Now audited.

## One demand source

Four runners read `VirginiaOnlyLoad`; four read the cached intermediate. **Byte-identical** where
both exist — but **the cache only covers checkpoint years**, so those runners were silently
checkpoint-only. All now read the source; `run_all` alone writes the cache.

*Consequence worth deciding: the cached intermediates are now written and never read.*

## Scenario 3's gas split

`SocialCostRGGIMixin` refuses to default `get_existing_new_mw`, because *"reusing another scenario's
own split is worse than an explicit failure."* **That guard cannot fire through inheritance** —
`Scenario3Solver` inherits from `Scenario1Solver` and picked up Scenario 1's implementation silently.

**Verified genuinely identical** (Scenario 3 doesn't override `apply_gas_cap`), now stated
explicitly. **A formal ABC would not have caught it** — `abstractmethod` is satisfied by an
inherited implementation.

## Audit checks added this session

| check | catches |
|---|---|
| modules import what they reference | `driver` used `assumptions` without importing it — **every solve raised** |
| no undocumented dormant driver functions | four public functions with no caller |
| no dead functions in the runners | orphans left by removing a caller |
| one demand source in the runners | checkpoint-only runners |
| scenarios state their own gas split | inheritance bypassing the mixin's guard |

**Five of these needed narrowing before they were trustworthy** — false positives from docstring
prose, from bare-name function references, from locally-bound parameter names. A check that cries
wolf trains the reader to skip it.

## Next

```bash
python3 run_scenario1.py                                          # ~19 min
python3 run_foresight_comparison.py --myopic-from results/scenario1.json
python3 run_scenario1b.py
```

**Watch on 1B:** the 2044 → 2045 solar increment should be **zero**, and the gas share should move
off 1.63% now that the capacity is right.
