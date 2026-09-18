# Common Reference

**Cross-cutting facts and conventions that apply to every scenario.** Where a quantity, unit basis
or convention is shared across the model, it is defined here once rather than restated in each
scenario's working paper.

**And it is a WORKING document, not a reader-facing one.** Appendices are for the end reader and
hold the settled account of a subject; this holds cross-scenario decisions, conventions and measured
facts while they are still moving. Material migrates from here to an appendix when a subject is
finalised — rewritten for a reader who was not present for the reasoning, not copied. See
`appendices/APPENDIX_ORDER.md`.

**This is a reference, not a log.** LP issues and their solutions go to
`Internal_Debugging_Log.md`; recurring error patterns go to `Common_Mistake_Log.md`; scenario
findings go to that scenario's working document; where things stand goes to
`Scenario_Completion_Dashboard.md`; open problems go to GitHub issues.

---

## Index

| # | section | covers |
|---|---|---|
| 1 | Transmission and distribution | loss factor, load against generation basis, what "energy sold" means in statute |
| 2 | Resource adequacy metrics | what is measured, what is not, and why the probabilistic names are not claimed |
| 3 | Probabilistic adequacy | what LOLE and CVaR would require, and what the draw loop costs |
| 4 | LP builder restructuring | why it is happening, how it is verified, and where it stands |

*Sections are added as cross-cutting questions arise. A topic belongs here when a second scenario
would otherwise need the same answer.*

---

## 1. Transmission and distribution

### 1.1 The loss factor is 1.0925

Derived from two Dominion sources for the same year and scope, so the gap is losses and nothing
else:

| source | 2030 GWh | basis |
|---|---:|---|
| `DOMLSEHourlyLoadProjections2024through2048.csv` | 121,115 | losses **included** |
| 2025 IRP Update, Appendix 2B-1 | 110,864 | losses **excluded** |
| **ratio** | **1.0925** | ≈9.25% losses and station service |

Both figures are Virginia plus North Carolina, so this is **not** a scope difference. The IRP
itself distinguishes the two bases, describing values *"at the utility generator and adjusted for
line losses"* (Figures 2.1.11 and 2.1.12).

**This is Dominion's own figure for Dominion's own system**, which is preferable to any general
modelling assumption for T&D losses.

### 1.2 Two bases, and which applies where

● **Generation basis** — what must be produced at the generator, losses included. **121,115 GWh**
  in 2030 for Virginia plus North Carolina.
● **Meter basis** — what arrives at the customer and is sold. **110,864 GWh** for the same year and
  scope.

**Dispatch uses the generation basis.** The hourly file already carries the gross-up, so it is used
directly and needs none.

**Statutory obligations use the meter basis**, where the Code says so. Va. Code § 56-585.5(C): the
RPS Program requirement is *"a percentage of the total electric energy **sold** in the previous
calendar year."* Sold means metered, so the base is generation ÷ 1.0925.

**The same series is therefore divided for one purpose and not for the other**, sometimes within
the same function. That is correct, and it is the single most likely place in this model for a
plausible-looking error.

### 1.3 The class name says "load" and returns generation

`demand_basis.VirginiaOnlyLoad` returns the **generation-side** quantity. "Load" here follows the
utility-planning convention — what must be generated to serve load — rather than the ordinary
reading of load as the quantity at the meter.

**The name points the wrong way for statutory work**, and the docstring's warning is what makes the
basis clear rather than the name. A reader who takes "load" at face value and divides by the loss
factor for dispatch would understate generation need by 9.25%; the working notes flag exactly that.

### 1.4 What is not represented

● **Losses are a scalar gross-up, not modelled physically.** There is no distinction between
  transmission and distribution losses, no variation by hour or by load level, and no locational
  detail. Real losses rise with the square of current, so they are higher at peak than the flat
  9.25% implies.
● **Avoided losses from distributed generation are not credited.** Generation at the meter avoids
  the losses that serving the same load from a central station would incur — worth roughly 9% of
  the energy it displaces. Scenario 3's transmission-deferral assessment is where this would be
  quantified; it is not currently anywhere in the model.

**Both omissions run the same way: they understate the value of distributed generation.**

---

## 2. Resource adequacy metrics

**NERC's *Risk Mitigation for Emerging Large Loads* (2026)** asks resource planners for multiple
probabilistic metrics — *"loss of load hours, expected unserved energy, and conditional value at
risk"* — because these *"provide information on the duration, magnitude, and severity of potential
shortfall events."*

It is explicit that one aggregate figure is not enough: *"without expanded metrics, RPs risk being
surprised by rare, severe outages that **aggregate metrics like loss of load expectation cannot
detect**."*

### What this model reports

`lp_package/reliability_metrics.py`, computed from the hourly unserved-energy series every solve
already produces:

| metric | dimension |
|---|---|
| loss of load hours | duration |
| longest shortfall event | duration |
| unserved energy | magnitude |
| peak shortfall | magnitude |
| event count and mean event length | severity, as far as one realisation allows |

### What is not claimed, and why

**These are realisations, not expectations.** A proper expected unserved energy is an expectation
over many scenarios — NERC asks for *"thousands of integrated weather, load, and generation
scenarios"* — and this model solves one weather year at a time with no forced-outage draws.

So the functions are named `unserved_energy_mwh` and `loss_of_load_hours`, **not `eue`**. The
correspondence is stated; the term is not taken. Using the probabilistic name for a deterministic
quantity would invite comparison against a standard it cannot meet.

**Conditional value at risk is not offered.** CVaR at 95% needs at least 20 scenarios for a single
tail observation and several hundred for a stable estimate; eight weather years give 0.4. **What
closes that gap is forced-outage draws, not more weather years** — 8 weather years × 100 draws is
800 scenarios, which is in NERC's range. Scoped as its own work.

### Zero unserved is a correctness test; non-zero is a result

Different questions, and the distinction governs how these figures are read. A scenario built to
serve its load must show zero, and a non-zero value there is a defect — which is why the runners
raise. Scenario 2 bounded by its real gas fleet legitimately shows **30.05 TWh over 5,671 hours** at
2045, and that is a finding about the statutory minimum rather than a bug.

---

## 3. Probabilistic adequacy — what it would take

Section 2 covers the metrics this model produces today: realisations under one weather year with no
forced-outage draws. This section records what the probabilistic versions need, because the answer
turned out to be far cheaper than first estimated and that changes what is worth attempting.

### The scenario axis has to come from outages, not weather

NERC asks for *"thousands of integrated weather, load, and generation scenarios."* This project holds
**eight weather years** — the correlated axis, and the expensive one to produce. The second axis is
**forced-outage draws**, sampled per unit, which multiply against the first:

```
8 weather years  ×  375 draws  =  3,000 scenarios
```

**More weather years would not help.** Conditional value at risk at 95% needs roughly 20 scenarios
for a single tail observation and several hundred for a stable estimate; eight years give 0.4. Draws
are what close that gap, and they are cheap.

### What each metric needs

| metric | converges at | why |
|---|---|---|
| **loss of load hours** | ~30 draws | a bounded count, 0–8,760, so variance is limited |
| **unserved energy** | ~100 draws | unbounded above and heavy-tailed: one simultaneous outage in a cold snap can outweigh forty ordinary scenarios |
| **CVaR at 95%** | ~375 draws | needs the tail itself, not a mean over it — 150 observations above the 95th percentile |

**All three come from the same run.** An earlier staged plan — loss-of-load hours first, unserved
energy later — was designed around a cost estimate that proved wrong by a factor of five.

### What it costs, measured

A Scenario 2 solve is 166,440 variables and 43,800 equality rows. On a 16-logical-core workstation
it takes **2.25–2.30 s serial**, and the outage draw changes only rung upper bounds, so the problem
can be rebuilt or mutated — the build is 0.4 s, so it barely matters which.

| draws per weather year | scenarios | hours, 4 checkpoints |
|---:|---:|---:|
| 30 | 240 | 0.2 |
| 100 | 800 | 0.7 |
| **375** | **3,000** | **2.5** |

**Checkpoint years only.** Capacity decisions are made at 2030, 2035, 2040 and 2045; intermediate
years inherit the fleet, so the draw loop does not need all twenty.

### Parallel scaling: concurrency sets the envelope, grouping fine-tunes at the peak

Measured on a 16-logical-core x86_64 workstation, 2026-09-14. A single pool across worker counts:

| workers | speedup | efficiency |
|---:|---:|---:|
| 4 | 2.4× | 60% |
| **8** | **3.1×** | 38% |
| 16 | 2.7× | 17% |

**Throughput peaks at eight and turns down.** Memory bandwidth saturates around eight concurrent
solves; past that, hyperthread contention costs about 12% while occupying the whole machine.
Efficiency falls monotonically, which is the bandwidth-bound signature.

Running several independent jobs at once, each with its own pool:

| total concurrent | best grouping | solves/s | spread across groupings |
|---:|---|---:|---:|
| **8** | **4 jobs × 2 workers** | **1.37** | **12%** |
| 12 | 4 × 3 | 1.28 | 5% |
| 16 | 1 × 16 | 1.18 | 10% |

**Two things follow, and both were got wrong before being measured.**

● **Total concurrency sets the envelope.** Eight beats twelve beats sixteen in every grouping. No
  arrangement of processes recovers what is lost past the bandwidth ceiling.
● **Grouping matters only AT the peak.** At eight concurrent, four jobs of two workers beats one job
  of eight by **12%** — likely pool coordination overhead, which shows when the last of the
  available bandwidth is being extracted. At twelve the three groupings sit within 5%, and the
  effect has gone.

**The recommended configuration is 4 jobs × 2 workers**: the best aggregate throughput measured, and
four scenarios progress together rather than in sequence. **4 × 3 is the honest alternative** — 7%
less aggregate, but each job runs 50% faster, so four scenarios *finish* sooner. For a single
scenario, one job on eight workers remains the best option.

**Two earlier models of this were wrong.** The first multiplied per-pool speedups and claimed 6.2×
aggregate for two jobs of eight. The second, correcting it, held that grouping was irrelevant and
only total concurrency mattered. Neither survived measurement, which is why
`scripts/time_concurrent_jobs.py` compares equal-concurrency groupings explicitly rather than
inferring them from the single-pool curve.

**These figures are machine-specific.** The finding that transfers is the method: measure the
single-pool peak, then measure groupings at and around it.

### What is still missing

**Per-unit forced outage rates.** NERC GADS publishes class-average equivalent forced outage rates
and EIA-860 gives unit vintages; neither is in this repository. That input, and a draw loop around
the existing solve, is the whole of the remaining work.

---

## 4. LP builder restructuring — in progress

### Why

**Rule 15 sets a cyclomatic complexity limit of 15.** Measured 2026-09-14:

| function | complexity | lines |
|---|---:|---:|
| `build_problem` | **67** | 830 |
| `build_scenario2_problem` | **26** | 323 |
| `build_dispatch_problem` | **19** | 169 |

The other 17 functions in `lp_model` sit at 6 or below, so this is concentrated in the builders.

**Complexity is a lower bound on the paths needed for branch coverage.** At 67, exhaustive coverage
is not achievable — which is how the merit-order stack ran unreached for a full session: no test
exercised that combination of flags. `build_problem` carries 30 `if` statements and 21 `for` loops,
with one scenario's logic scattered across five separate locations rather than sitting in one block.

**And `build_scenario2_problem` is evidence for the direction.** It exists because splitting was
easier than extending, and it is the more readable of the two — an expedient split that produced
the better structure.

### How it is verified

**`scripts/capture_lp_baseline.py` fingerprints the assembled problem** — `c`, `bounds`, `A_eq`,
`b_eq`, `A_ub`, `b_ub` — for a representative call of each builder configuration. Every extraction
step is checked against a baseline captured **before any change**.

**Sparse matrices hash on canonically sorted COO triplets**, so a reordering that does not change
the problem passes while a changed coefficient does not. Shape is hashed separately, because
gaining or losing variables is a different kind of event from perturbing one.

    python3 scripts/capture_lp_baseline.py --capture   # before
    python3 scripts/capture_lp_baseline.py             # after

**What it does not catch:** a change to the problem and the baseline together. The baseline must be
captured from unmodified code, which is why `capture_baseline` and `compare_to_baseline` are
separate entry points rather than one function that refreshes on mismatch.

### Returning to the checkpoint

**Tag `pre-lp-restructure`** marks the state immediately before this work: 1,370 tests, 18 audit
checks, 4 LP fingerprints identical to baseline, Scenario 2 steps 1–11 complete.

    git checkout pre-lp-restructure
    python3 scripts/capture_lp_baseline.py     # must report 4 problems IDENTICAL

**The fingerprint check is the meaningful one.** Tests confirm results are unchanged; fingerprints
confirm the *problem* is unchanged, which is stricter — a perturbed coefficient can still solve to a
similar objective and pass every test.

### Where it stands

| step | state |
|---|---|
| Fingerprint harness | **done** — 4 configurations |
| `emit_energy_balance_rows` | **done** — 3 call sites |
| `emit_bath_state_of_charge_rows` | **done** — 2 call sites |
| `LpSegmentSpec` + `apply_segment_spec` | **done** — complexity 7 and 10 |
| `CheckpointSolver.lp_segment_spec()` | **done** — base returns empty |
| Scenario 3's spec populated | pending |
| Five flag sites replaced by spec consumption | pending |
| Sodium-ion and iron-air state of charge | pending |
| Reserve margin rows | pending |
| Re-measure, then attack the remaining branching | pending |

### The specification, as built

**A frozen dataclass declaring what a scenario adds** — residual adjustments, extra columns with
their bounds and objective terms, extra rows, and a label. It validates that the three per-column
tuples line up, because the assembler zips them by position and a mismatch would silently attach a
bound to the wrong column.

**`apply_segment_spec` returns immediately on an empty spec.** Scenarios 1, 1B and 2 add nothing and
never execute any segment logic — which is what takes complexity *down* rather than moving it from
the builder into the assembler.

**The assembler owns indexing.** A spec's rows reference columns by *name*, resolved against that
segment's own columns, so a scenario never computes a column number. An index collision is the
failure mode this model is least able to detect: the matrices still solve, and the answer is simply
wrong.

**The base-class hook returns empty rather than raising.** Unlike `gas_retirement_schedule` and
`new_gas_technology`, where every scenario makes a real choice and silent inheritance is the failure
mode, adding nothing here is a meaningful and correct answer for most scenarios. Forcing each to
declare it would be ceremony that hides which one actually differs.

**After two extractions:** `build_dispatch_problem` 19 → 16, `build_scenario2_problem` 26 → 23,
`build_problem` unchanged at 67 — its share of those particular loops was small, and its complexity
is concentrated in the scenario branching rather than the row assembly.

### The decision behind it

**One builder per scenario, sharing a core** — rather than a segment protocol, or continuing to add
parameters. Measured before committing: **80% of `build_problem` is scenario-agnostic**, and the
merit order, which is another 12%, belongs in the core too. That leaves roughly 8% genuinely
scenario-specific, which is what a thin per-scenario builder would hold.

**The row extraction comes first** regardless, because splitting an 830-line body four ways before
making it readable would duplicate an untested structure rather than fix it.
