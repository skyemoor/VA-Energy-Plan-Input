# Common Reference

**Cross-cutting facts and conventions that apply to every scenario.** Where a quantity, unit basis
or convention is shared across the model, it is defined here once rather than restated in each
scenario's working paper.

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

### Parallel scaling peaks below the core count

| workers | speedup | efficiency |
|---:|---:|---:|
| 4 | 2.4× | 60% |
| **8** | **3.1×** | 38% |
| 16 | 2.7× | 17% |

**Eight beats sixteen.** Memory bandwidth saturates around eight concurrent solves; past that,
hyperthread contention costs about 12% of throughput while occupying the whole machine.

**The numbers above are for TOTAL CONCURRENT SOLVES, however they are grouped.** Memory bandwidth
does not care how processes are divided into jobs: two jobs on eight workers each is sixteen
concurrent solves, which is the 2.7× row, not twice the 3.1× one. An earlier version of this
section multiplied per-pool speedups and claimed 6.2× aggregate; that was wrong, and the error is
recorded because it is an easy one to repeat.

**So throughput is maximised at about eight concurrent solves in total.** One job on eight workers
and two jobs on four workers each should deliver the same aggregate — the second being preferable
when two scenarios are wanted at once, since they progress together rather than in sequence.

`scripts/time_solve_benchmark.py` measures single-job scaling and
`scripts/time_concurrent_jobs.py` measures the multi-job case directly. The peak is
machine-specific and going past it makes things worse, so both should be measured rather than
assumed.

### What is still missing

**Per-unit forced outage rates.** NERC GADS publishes class-average equivalent forced outage rates
and EIA-860 gives unit vintages; neither is in this repository. That input, and a draw loop around
the existing solve, is the whole of the remaining work.
