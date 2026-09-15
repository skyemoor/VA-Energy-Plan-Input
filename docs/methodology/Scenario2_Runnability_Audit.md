# Scenario 2 runnability audit — RESOLVED

**2026-09-13.** All three blockers cleared; the baseline runs and its compliance level is measured.

> ## The result
>
> **Scenario 2 reaches 34.7% clean generation share at 2045**, with an implied gas peak of
> **22,479 MW**.
>
> **Corrected 2026-09-13 from 39.2%.** The earlier figure double-counted post-VCEA solar — it
> passed the full 16,100 MW target alongside the existing fleet, treating the statutory target as
> entirely new build. It is a **total**, not an increment: only **645 MW** of the existing 5,300
> predates the VCEA, and the other **~4,655 MW** was approved under § 56-585.5 D.4's annual
> petition process, which is the mechanism the 16,100 MW is measured by. **New build required is
> ~11,445 MW, not 16,100.**
>
> **Demand has roughly doubled since the VCEA was written, while the statutory MW targets did not
> change.** The statutory build was sized against a much smaller system.
>
> **This falls far below the 75–100% sweep range.** The baseline cannot be plotted on that axis as
> designed — the sweep must extend downward, or the chart must show Scenario 2 as an off-scale
> reference. That is a structural consequence for the restructuring, not a detail.

**Original audit, 2026-09-13.** Scenario 2 is the whitepaper's **baseline** — Dominion's approach of building only
the solar and storage assets named in the Code. Before it can be plotted as the reference point on
the compliance sweep, it has to run. This records what was found tracing it.

---

## SLCOE — **$32.80/MWh**

Twenty annual solves, 2026–2045, levelised at WACC 4.5% from base year 2026. 1.2 minutes.

| | |
|---|---:|
| PV cost | $74.88B |
| PV demand | 1,977.9 TWh |
| PV terminal value | $10.01B |
| **SLCOE without terminal value** | **$37.86/MWh** |
| **SLCOE with terminal value** | **$32.80/MWh** |

**Capex band $32.30 – $33.51/MWh** with terminal value — a 3.7% spread. Gas capex uncertainty barely
moves this scenario, because most of its cost is **fuel, not capital**. The gas *price* band is the
axis that matters, and it is separate.

### Social and environmental cost

Across all twenty years per P.2 #9, on the same PV basis:

| tier | PV | $/MWh |
|---|---:|---:|
| **Virginia SCC** (CO₂ only, statutory) | $145.83B | **$73.73** |
| **Social cost of GHG** (CO₂+CH₄+N₂O) | $160.57B | **$81.18** |
| **Health impacts** (PM, SO₂, NOx) | $10.88B | **$5.50** |
| **TOTAL SOCIETAL SLCOE** | | **$119.48/MWh** |

**The climate externality is ~2.5× the direct cost.** Tier 1 is reported as two figures, never
combined, per Va. Code §56-598(2)(d).

### Clean share

**47.4% (2026) → 34.7% (2045)**, peaking near 2030–31 as the statutory solar builds out, then
falling as demand overtakes it. **The turning point is where the fixed 16,100 MW target stops
keeping pace.**

---

## Storage is built, paid for, and never operates

**Measured at 2045: zero charge, zero discharge, zero curtailment** — sodium-ion, iron-air and Bath
alike, in all 8,760 hours.

**There is nothing to store.** Solar delivers 41.3 TWh against 202.2 TWh of demand, and
solar-plus-nuclear exceeds demand in **14 hours of 8,760**. With 16,100 MW of solar against a
29,000 MW peak, every kilowatt-hour it produces is consumed as it is made. Charging would mean
burning gas at noon to discharge at 6pm and losing a tenth to round-trip efficiency — strictly worse
than burning the same gas at 6pm.

**The statutory mandates are mismatched.** § 56-585.5(E) requires 16,000 MW short-duration and
4,000 MW long-duration storage; the paired solar target is far too small to fill it. That storage
carries roughly **$3.4B/yr of annualised capital by 2045** and never cycles.

### Two model boundaries push the same way

**No imports** (P.2 #15) and **a flat annual gas price** (P.2 #16). Real MID-ATL/APS prices show a
**$45.92 night-to-evening spread** — $41.75 at 00–05 against $87.67 at 16–20 — against a sodium-ion
cycling cost of $5.43/MWh. On that spread storage is comfortably economic **with no surplus at all**.

**So the idle storage is partly an artifact of the model offering it nothing to do.** The
mandate-mismatch finding stands on the energy balance, which no price shape changes. The
**$3.4B/yr of stranded capital does not stand alone** — it needs the caveat, because a model with
unit commitment would have that storage earning against the spread.

---

## It uses a different solve path entirely

`Scenario2Solver.solve()` calls **`lp.build_scenario2_problem()`**, not `build_problem()`. It does
not use `converge_frac`, `apply_gas_cap()` or `capacity_cap_mw`.

**Gas is unbounded, and that is correct for this scenario.** The build is pinned to the statutory
solar and storage; gas fills whatever remains. That *is* Dominion's approach, and the resulting gas
share is the output we want.

**Consequence worth stating:** the two-gas-limits problem recorded in `Gas_Fleet_Working_Notes.md`
does **not** apply to Scenario 2. That cap governs Scenarios 1, 1B and 3.

---

## Three blockers

### 1. `peak_gas_mw` comes from a lost temp file — RESOLVED by making gas unbounded

`get_existing_new_mw()` back-computes new build from `self.peak_gas_mw`, documented as coming from
*"Scenario 2's own already-solved 20-year gas capex schedule"* at
**`/tmp/scenario2_20yr_gas_capex.npz`**.

**That is a temp file.** It does not exist in any clone and did not survive any session. Whatever
was solved for is gone.

Scoped: this path is needed **only** for the social-cost/RGGI mixin. A plain cost run may not touch
it, and the constructor raises a clear error if it is called without the value rather than
substituting a default.

### 2. `compute_scenario2_gas_replacement` is not restored — still true, but not blocking

Needed only by `get_existing_new_mw()` for the social-cost/RGGI mixin, which the cost run does not
touch.

### 2a. The original blocker was worse than either of these

`get_existing_new_mw()` imports it for `existing_fleet_mw_by_type()`. It is on the outstanding
restore list from earlier sessions, alongside `compute_tier123_final.py` and
`compute_scenario2_costs.py`.

### 3. Whether storage is pinned — RESOLVED: everything is pinned

`build_scenario2_problem()` takes `vcea_solar_mw`. The baseline definition requires **16,100 MW
solar, 16 GW short-duration storage, 4 GW long-duration** — all three pinned.

**Verified: all three are hard bounds.** `build_scenario2_problem` is **dispatch-only** — `NVAR =
14 × T`, no build block at all. `vcea_solar_mw`, `na_power_mw`, `na_duration_hr`, `fe_power_mw` and
`fe_duration_hr` are fixed inputs applied directly as variable bounds.

**The real blocker was different and larger:** `Scenario2Solver.solve()` passed **six** arguments to
a function requiring **thirteen**. Every call raised `TypeError`. The baseline scenario had never
run through the solver class.

**Two interpretations were needed to wire it:**

- **Sodium-ion duration: 4 hours**, by decision. The Code names MW, not MWh, so duration is an
  *interpretation* rather than a requirement — and it is the single largest discretionary number in
  the baseline. 16,000 MW × 4 h = 64 GWh.
- **Gas effectively unbounded**, by decision. The external CCGT sizing the docstring describes lived
  in `/tmp/scenario2_20yr_gas_capex.npz`, which did not survive. Rather than invent a replacement,
  gas runs against a ceiling high enough never to bind and **the peak is an output** — how much gas
  the statutory build implies. That is a better question than whether Dominion's gas fits a number
  we made up.

**What this cannot tell you** is the CCGT/CT split within that 22,478 MW. This function has one gas
variable and one gas price — no merit order — so everything is CCGT by construction.

---

## Why this matters for the sweep

The whole comparison rests on Scenario 2 being **genuinely** the statutory build. If any of its
three components is optimised rather than pinned, the reference point moves toward the curve and
the gap the whitepaper reports shrinks for the wrong reason.

**This is the next thing to trace**, and it gates step 3 of the sweep sequence.

---

## Related

- `Scenario_Restructuring_Compliance_Sweep.md` — why Scenario 2 is the reference
- `Gas_Fleet_Working_Notes.md` — the gas cap that does *not* apply here
- `SCENARIO_NAMES.md`, `Internal_Debugging_Log.md` #53 — prior Scenario 2 work
