# Scenario 2 — Statutory Minimums

**The working document for Scenario 2.** Build only the 16,100 MW of solar and 20,000 MW of storage
the Code names; meet the rest with gas. The reference case against which every other scenario is
read.

Status lives in `Scenario_Completion_Dashboard.md`; what was run lives in
`Internal_Debugging_Log.md`; open problems live in GitHub issues. Cross-cutting facts that apply to
every scenario live in `Common_Reference.md`.

---

## Index

| # | topic | covers |
|---|---|---|
| 1 | Result | SLCOE, capex band, social and health cost, clean-share trajectory |
| 2 | Storage | why it is insufficient rather than idle; the superseded finding and why it was wrong |
| 3 | Gas capacity | the measured 2045 gap, its shape, and the technology that fits it |
| 4 | Solve path | how Scenario 2's solver differs from the others and why |
| 5 | Resolved blockers | what stopped it running, and how each was settled |
| 6 | Bearing on the sweep | why this scenario sets the compliance axis's lower bound |

**Scenario-specific methodology that is not cross-cutting stays here.** Gas capacity method is
Appendix Q; the compliance definition is `Compliance_Definition_For_Sweep.md`.

---

## 1. Result — SLCOE $32.80/MWh

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

## 2. Storage — insufficient, not idle

**Corrected 2026-09-14**, superseding the section below. The earlier finding was measured on an
**unbounded gas** model, where the ceiling was 200,000 MW and gas could serve whatever the hour
needed.

With the merit-order stack bounding gas at the real fleet — **12,216 MW available at 2045** —
sodium-ion discharges **13.04 TWh over 2,666 hours**, and **17.96 TWh still goes unserved** across
3,294 hours, peaking at 10,263 MW.

**The mechanism is scarcity, not arbitrage.** With gas capped, the alternative to discharging is
unserved energy at the penalty price, so storage runs whenever it holds charge. It needs no price
spread to do so.

**So the mandate is not mismatched; it is insufficient.** That is a different claim from the one
below, and a stronger one: the statutory storage works hard and still cannot close the gap.

### What the gap requires

**1,233 separate blocks, median 2 hours, longest 27** — uniformly peaking duty, clearing no
combined-cycle minimum uptime at any level, with an implied capacity factor of **20.0%**.

Costed on the full four-term formulation, **combustion turbine beats combined cycle by $1,365M/yr**
— on capital, maintenance, capacity factor and duty shape alike. Only fuel favours combined cycle,
and at 20% capacity factor there are too few hours to earn it. Full working in **Appendix Q.3a**.

### And fuel was understated

A single gas variable at a 6.40 heat rate burns 132 TWh as though the best machine in the fleet ran
every hour. The stack gives an effective heat rate of **8.12** and **$56.22/MWh against $44.32** —
**$11.90/MWh** understated.

---

### 2.1 Superseded — "storage is built, paid for, and never operates"

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

## 3. Gas capacity — the measured 2045 gap

With the merit-order stack bounding gas at the real fleet, the gap is **10,263 MW of peaking duty**:
1,233 blocks, median 2 hours, longest 27, implied capacity factor 20.0%. Nothing clears a
combined-cycle minimum uptime at any level.

Costed on the full four-term formulation, **combustion turbine beats combined cycle by $1,365M/yr**
— on capital, maintenance, capacity factor and duty shape alike. Only fuel favours combined cycle,
and at 20% capacity factor there are too few hours to earn it.

**Full working, with formulas and citations, in Appendix Q.3a.** The method itself — brownfield
screening curve, Type 3 — is Appendix Q, and applies to every scenario rather than this one.

---

## 4. Solve path — different from every other scenario

`Scenario2Solver.solve()` calls **`lp.build_scenario2_problem()`**, not `build_problem()`. It does
not use `converge_frac`, `apply_gas_cap()` or `capacity_cap_mw`.

**Gas is unbounded, and that is correct for this scenario.** The build is pinned to the statutory
solar and storage; gas fills whatever remains. That *is* Dominion's approach, and the resulting gas
share is the output we want.

**Consequence worth stating:** the two-gas-limits problem recorded in `Gas_Fleet_Working_Notes.md`
does **not** apply to Scenario 2. That cap governs Scenarios 1, 1B and 3.

---

## 5. Resolved blockers

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

## 6. Bearing on the compliance sweep

The whole comparison rests on Scenario 2 being **genuinely** the statutory build. If any of its
three components is optimised rather than pinned, the reference point moves toward the curve and
the gap the whitepaper reports shrinks for the wrong reason.

**This is the next thing to trace**, and it gates step 3 of the sweep sequence.

---

### Related

- `Scenario_Restructuring_Compliance_Sweep.md` — why Scenario 2 is the reference
- `Gas_Fleet_Working_Notes.md` — the gas cap that does *not* apply here
- `SCENARIO_NAMES.md`, `Internal_Debugging_Log.md` #53 — prior Scenario 2 work
