# Model-Wide Findings

**Read before interpreting any scenario result.** These affect **every** scenario, not one. They
were found while investigating Scenario 3 and were initially recorded in
`Scenario3_Technical_Notes.md`, which understated their scope — someone reading Scenario 1 or 2
would not have found them there.

Last updated 2026-09-11.

---

## 1. The hourly energy price has zero variance

**Measured 2026-09-11.** Solved 2030 with the distributed segment enabled and extracted
`res.eqlin.marginals` for the 8,760 hourly energy-balance rows:

| | |
|---|---|
| **unique values across 8,760 hours** | **1** |
| value | **$54.70/MWh, every hour** |

$54.70 = $51.30 simple-cycle fuel + $3.00 VOM. **The marginal resource is simple-cycle gas, priced
identically in every hour of the year.**

### For comparison, real Virginia prices

| | |
|---|---:|
| Ashburn 35 kV, July, month-hour averaged | **$38–354** ($316 spread) |
| Rural 115 kV south of Petersburg, July | **$31–242** ($211 spread) |
| Dominion Hub day-ahead, 3 Sep 2026 | peak **~$545** |
| Dominion Hub **real time**, 3 Sep 2026 | peak **~$1,240** |
| **Our LP dual** | **$54.70 flat** |

The node figures use the *same* month-hour averaging the model uses, so averaging is not the
explanation.

### RESOLVED 2026-09-12 — the merit order gives the dual structure

Wiring the gas stack into `build_problem` changes the 2030 dual from **one unique value to 40**:

| | before | after |
|---|---|---|
| unique values across 8,760 h | **1** | **40** |
| range | $54.70 flat | **$37.56 – $3,690.71** |
| std | 0 | 215.15 |

The minimum is **exactly `ccgt_modern`'s marginal cost** ($37.56) — the cheapest hours now clear at
the cheapest rung rather than at simple-cycle gas. Rungs dispatch in merit order: ccgt_modern runs
8,648 hours, ccgt_fleet 7,921, ccgt_legacy 6,396, ct_fleet 4,804.

**Design note:** the integration is additive. `IDX['g']` remains the hourly gas total, so the energy
balance, `gascum` and the gas-share constraint are untouched; per-rung variables are appended and
tied to the total by one equality per hour. Replacing `IDX['g']` outright would have meant editing
four build functions, with far more surface for a silent error and no way to test the 2045 solve here.

**Default is off.** `gas_merit_order=None` reproduces prior behaviour exactly, so existing baselines
stay valid.

**Wired through the solver path 2026-09-12.** It was initially reachable only by calling
`build_problem` directly — `Scenario3Solver.converge_and_solve()` overrides the parent, and neither
it nor `drv.run_solve()` / `drv.converge_frac()` accepted the parameter, so **no scenario could use
it.** Now threaded through all three layers, with `_gas_merit_order_kwargs()` on `CheckpointSolver`
so every scenario inherits it. Set `solver.gas_merit_order = GasMeritOrder(...)` before
`converge_and_solve()`.

**Note on solve cost:** a checkpoint is up to **four LP solves**, not one — `converge_frac` iterates
up to three times before the final solve. At 2030 those run 77–137s each. That is why the 2045
measurement has not completed in-session.

### CAUSATION CORRECTED 2026-09-11 — it is not storage arbitrage

An earlier version of this finding attributed the flat dual to **unconstrained storage arbitraging
prices to equilibrium**. That was wrong, and the correction came from a direct challenge: prices
should not flatten if storage has a cycling cost, and they should not be flat at all in hours with
solar curtailment.

**Both objections are correct.**

**Storage does carry a cycling cost** — `$5.43/MWh` sodium-ion, `$18.03/MWh` iron-air, applied to
every discharged MWh in the objective. Storage therefore *cannot* arbitrage prices closer together
than that spread plus round-trip losses. A perfectly flat dual is not an arbitrage equilibrium.

**The actual cause is simpler: one gas price, and no curtailment.** At 2030 the model has
**zero curtailment and zero unserved energy** (measured). Gas is marginal in every hour, and there
is only one gas cost, so the dual is that cost in every hour. Storage did not flatten anything —
there was never anything to arbitrage, which is why it sat idle.

The causation in the earlier version ran backwards.

### AND THE MEASUREMENT IS 2030-ONLY — not established for 2045

The measurement was taken at **2030**, where the build is small and there is no curtailment. It was
then documented as a model-wide finding. **The 2045 case has not been measured** — the solve
exceeds the available time limit and was not completed.

At 2045 the model has **~42% of hours in net surplus** (3,722 of 8,760, with net load reaching
−160 GW against a 22 GW peak). Those hours must price at or near the curtailment cost, not at the
gas price. **The dual at 2045 should therefore vary, and the flat-dual finding may not hold there
at all.**

This does not vacate the finding — a flat dual at 2030 is real, and the single-gas-price cause is
real in every year. But **"the LP's hourly energy price has zero variance" is established for 2030
and assumed for 2045**, and the distinction was not made when it was first written.

### Three causes, all fixable, none fixed

| cause | status |
|---|---|
| **One gas price** — no merit order, so nothing for the dual to climb | heat rate tiers and capacity per rung sourced (`Gas_Fleet_Working_Notes.md`); **not wired in** |
| **No operating reserve** — storage arbitrages to its floor in every hour | `all_hours_reserve.py` **exists and is dormant** — see §2 |
| **Nothing above gas** — stack jumps from $76/MWh to $100,000 VOLL | **not started**; no import variable exists at all |

### What this invalidates, and what it does not

**Invalidated:** any arbitrage-value figure, and any claim about price formation, scarcity rent, or
what a storage owner would earn. No part of this model sees a $470 hour.

**Not invalidated:** least-cost capacity expansion, SLCOE comparison between scenarios, and
transmission-deferral arguments. A flat energy price does not touch the physical congestion case.

**Probably explains** the 100% storage capacity accreditation on LP dispatch: storage that has
flattened all price variation is by construction available at every peak.

---

## 2. The all-hours reserve constraint exists, is documented as the standard, and is never called

`docs/Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md` describes three approaches to
reserve enforcement and names **1c as "current standard"**: an LP-integrated, all-hours reserve
constraint.

`lp_package/all_hours_reserve.py` implements it — itself rebuilt in a later session from that
documentation after the original `chained_dispatch_test.py` was lost.

**Nothing calls it.** The only reference outside the module is a comment in `driver.py` naming it
as an example of a module that *can* extend the LP.

**So every solve in the pipeline uses approach 1a** — the single-peak-hour constraint the same
document describes as the weakest of the three:

```
S × BUILD_SCALE × solar_cf[h] ≥ (1 + IRM) × demand[h]
    where h = hour_of_maximum_net_demand
```

One hour. It sizes the build so accredited capacity exceeds peak demand by 17.7%, and constrains
nothing else. **Storage is free to discharge to its floor in all 8,760 hours**, which is the
mechanism behind §1.

**This is the highest-value fix available**: the code exists, is documented, and was already
validated once.

### The net-load question — researched 2026-09-11

**CAISO uses two requirements in parallel, not one.** Resource Adequacy is sized against peak load
plus a planning reserve margin — our IRM equivalent, which we have. **Flexible Capacity** is sized
separately against the **largest 3-hour net-load ramps** plus contingency reserves — which we have
nothing equivalent to.

So net load is addressed **in addition to** peak, not instead of it. Replacing our gross-peak
constraint with a net-load one would lose what the peak constraint is for.

Scale, for calibration: CAISO net load swings ~25 GW over a day, dips **below zero at midday**, and
rises **6.5 GW in the 6pm hour**.

**`all_hours_reserve.py` likely subsumes both cases** — enforcing reserve in every hour covers the
peak hour and the ramp hours without a separate ramp requirement needing to be specified. That is
another reason to wire it in before building anything new.

Full treatment: `research/CAISO_Net_Load_Treatment.md`.

### A related question, unexamined

The constraint selects its hour on **net demand** — `find_hour_of_maximum_net_demand()` maximises
`demand − nuclear − existing solar − wind − new solar`. **Corrected 2026-09-11:** earlier versions
of this note said it used *gross* demand, which was wrong. The hour selection is already net-load
based.

What it then writes is `(1 + IRM) × demand[hour]` — **gross** demand at that hour. Net load picks
the hour; gross demand sets the requirement. Deliberate and defensible, but the two differ.

**What is genuinely missing** is narrower than previously stated: no *ramp* requirement, and only
one hour constrained out of 8,760.

---

## 2A. A documented rename regressed — and the error it was meant to prevent recurred

`Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md` §5 records that on **2026-08-23**
`t_peak` was renamed to `t_peak_net_load` across `checkpoint_solver.py` and `driver.py`, giving this
reason:

> *"The ambiguous name directly caused a real analysis error mid-session (checking `argmax(demand)`
> instead of the actual saved peak-**net-load** hour)."*

**The rename did not survive.** The code on 2026-09-11 carried `t_peak` again, and **the same class
of error recurred** — four documents were written stating the reserve constraint used *gross*
demand, when the hour selection has always been net-load based.

Renamed again, to `hour_of_maximum_net_demand`, which is harder to abbreviate back.

**This is the second instance of a documented fix regressing**, alongside `all_hours_reserve.py`
(§2) — built, documented as the project standard, and never called. Both were found only by reading
the code rather than the documentation. **Documentation recording that something was fixed is not
evidence that it is still fixed.**

---

## 3. No import capability

`export` exists (capped at `EXPORT_CAP_MW`, earning `export_price_mwh`). **`import` has zero
occurrences in the model.**

Virginia is modelled as an island that can sell into PJM but never buy. Dominion imports
substantially in reality, so this **likely overbuilds** — which inflates capacity in every
scenario, including the Utility Preferred Plan comparison.

The honest middle is that imports are available *except* during regionally correlated scarcity —
which is exactly the dunkelflaute hours that drive the build. A Virginia dunkelflaute is usually a
PJM-wide one.

**Open statutory question:** if the model imports PJM energy during scarcity, that energy is
largely fossil. Whether imported fossil power counts against § 56-585.5 — or whether the statute's
REC-and-retail-sales accounting makes imports invisible to it — has real consequences for how much
must be built.

---

## 4. Foresight asymmetry between model segments

| | lookahead |
|---|---|
| Utility-scale storage, dispatched inside the LP | **perfect** — knows the year |
| Distributed storage, via `distributed_exogenous_price_mwh` | **effectively none** |

Established independently: own-data accreditation read **100.0%** on LP dispatch against **31.8%**
from a no-foresight heuristic on the same fleet; and the exogenous price series' scarcity component
is near-constant (CV 3.99%, minimum 84% of mean).

This **systematically favours utility-scale storage** in precisely the comparison Scenario 3 exists
to make. Addressed for arbitrage value by the bracketing in `foresight_bracket.py`; **not**
addressed for capacity accreditation, where Shen et al. (arXiv 2607.27021) show perfect foresight
may not even be an upper bound, because uncertainty induces precautionary hedging.

---

## 5. Truncated source PDFs

The Dominion IRP PDFs in the project folder are **unreadable** — no `/Root` object, confirmed with
both `pypdf` and `pdfplumber`:

- `2025_Integrated_Resource_Plan_Update.pdf`
- `2025_Dominion_VA_NC_Plan_Update.pdf`
- `_2018_RD249-...2018_Integrated_Resource_Plan...pdf`

Any prior finding citing them should be treated as unverifiable from the current files.

---

## Priority order

1. **Wire in `all_hours_reserve`** — exists, documented, validated once. Re-extract duals after.
2. **Reserve sizing against net load rather than gross peak** — CAISO comparison.
3. **Wire in the gas merit order** — blocked on the CT aero/frame split and the 8,195-vs-9,362
   capacity reconciliation.
4. **Imports and scarcity pricing** — deferred by decision as its own work set.
