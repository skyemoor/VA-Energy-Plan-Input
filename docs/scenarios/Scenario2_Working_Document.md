# Scenario 2 — Statutory Minimums

**The working document for Scenario 2.** Build only the 16,100 MW of solar and 20,000 MW of storage
the Code names; meet the rest with gas. The reference case against which every other scenario is
read.

Status lives in `Scenario_Completion_Dashboard.md`, which carries the full routing table for every
kind of writing — what changed, LP issues, error patterns, source detail, citations and open
problems each have their own home.

---

## Index

| # | topic | covers |
|---|---|---|
| 1 | Result | annualised cost, levelised cost, social and health cost, clean-share trajectory |
| 2 | Storage | why it is insufficient rather than idle; the superseded finding and why it was wrong |
| 3 | Gas capacity | the measured 2045 gap, its shape, and the technology that fits it |
| 4 | Solve path | how Scenario 2's solver differs from the others and why |
| 5 | Resolved blockers | what stopped it running, and how each was settled |
| 6 | Bearing on the sweep | why this scenario sets the compliance axis's lower bound |
| 7 | Distributed carve-out | how the C.2 obligation is sized, and the solar cap assumption |
| 8 | Agrivoltaic siting | the overlay, its premium, and its land footprint |
| 9 | Adequacy and new gas | the measured shortfall, what closes it, and how the size was chosen |

**Scenario-specific methodology that is not cross-cutting stays here.** Gas capacity method is
Appendix Q; the compliance definition is `Compliance_Definition_For_Sweep.md`.

---

## 1. Result — annualised cost

Twenty annual solves, 2026–2045, levelised at a 4.5% weighted average cost of capital from a 2026
base year. **Run 2026-09-14** on the corrected specification: the C.2 distributed carve-out,
agrivoltaic siting, the merit-order stack, Schedule A retirement, and Bath County at Dominion's
1,808 MW share.

### Annualised system cost

| year | clean share | peak gas, MW | $B/yr | $/MWh |
|---|---:|---:|---:|---:|
| 2026 | 47.4% | 13,141 | 1.88 | 18.39 |
| 2030 | 48.6% | 14,948 | 3.27 | 27.73 |
| 2035 | 46.1% | 18,457 | 5.72 | 38.44 |
| 2040 | 35.7% | 22,926 | 8.58 | 45.53 |
| **2045** | **32.5%** | 22,480 | **9.98** | **49.38** |

**Annualised cost rises from $1.88B to $9.98B** across the window, and cost per megawatt-hour served
from $18.39 to $49.38 — a 2.7× increase while clean share falls.

### Levelised, as a secondary figure

| | |
|---|---:|
| PV cost | $72.00B |
| PV demand | 1,977.9 TWh |
| PV terminal value | $9.08B |
| SLCOE with terminal value | $31.81/MWh |
| SLCOE without | $36.41/MWh |

### Social and environmental cost

Across all twenty years, on the same present-value basis (Appendix P.2 #9, Appendix D):

| tier | PV | $/MWh |
|---|---:|---:|
| Virginia social cost of carbon (CO₂ only, statutory) | $147.09B | **74.37** |
| Social cost of greenhouse gases (CO₂ + CH₄ + N₂O) | $161.95B | **81.88** |
| Health impacts (PM, SO₂, NOₓ) | $10.96B | **5.54** |
| **Total societal** | | **119.24** |

**The climate externality is roughly 2.4× the direct cost.** Virginia Code § 56-598(2)(d) requires
the social cost of carbon as a component of generation operating costs; the CO₂-only statutory
figure and the broader multi-gas total are reported separately because they are different
quantities, per § 56-585.1(A)(6).

### What moved, and why

| | before | after |
|---|---:|---:|
| SLCOE with terminal value | $32.80 | **$31.81** |
| clean share at 2045 | 34.7% | **32.5%** |
| societal total | $119.48 | **$119.24** |
| PV cost | $74.88B | **$72.00B** |

**The C.2 carve-out lowers both.** It shifts 6,862 MW at 2045 from utility tracking at a 0.2252
capacity factor to a fixed 45° array at 0.1526 — about 4.4 TWh less generation on the same
nameplate, and less capital per megawatt of a cheaper resource.

### Clean share

**47.4% (2026) → 32.5% (2045)**, peaking near 2030 as the statutory solar builds out, then falling
as demand overtakes it. The turning point is where the fixed 16,100 MW target stops keeping pace.

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

---

## 7. Distributed carve-out — Va. Code § 56-585.5(C)(2)

**Raised from 1% to 4.5% (2026–2030) and 5% (2031–2045) by the Distributed Generation Expansion Act,
HB 628 / SB 175 (2026).** Met with resources of 1 MW or less, at least 25% low-income qualifying and
the remainder on or adjacent to public schools.

### Sizing

The Code sets the RPS Program requirement as *"a percentage of the total electric energy **sold** in
the previous calendar year"*, and the carve-out as a percentage of that requirement:

```
energy sold (n−1)  =  VirginiaOnlyGeneration(n−1) ÷ 1.0925
RPS requirement    =  Phase II share × energy sold
carve-out MWh      =  carve-out share × RPS requirement
x (MW)             =  carve-out MWh ÷ (8,760 × 0.1526)
```

**Sold means metered**, so the generation series divides by the loss factor — the same series used
undivided for dispatch. See `Common_Reference.md` section 1.

**Dominion is a Phase II utility**, and the schedule is tabulated in the Code year by year rather
than interpolated between milestones.

| year | RPS share | carve-out | **distributed** | utility new build |
|---|---:|---:|---:|---:|
| 2026 | 29% | 1.16 TWh | 868 MW | — |
| 2030 | 41% | 1.91 | **1,432 MW** | 3,655 MW |
| 2035 | 59% | 3.82 | **2,856 MW** | 8,589 MW |
| 2040 | 79% | 6.58 | **4,924 MW** | 6,522 MW |
| **2045** | **100%** | 9.17 | **6,862 MW** | **4,583 MW** |

**By 2045 the carve-out is 60% of new build.**

### The solar cap is an assumption

**D.2 is a one-time capacity target of 16,100 MW due 31 December 2035. C.2 is an annual energy
obligation that keeps growing** — reaching roughly 6,862 MW of equivalent capacity by 2045 against
about 2,856 MW at the 2035 deadline. The Code does not say whether the excess is built on top of the
target or absorbed within it.

**This analysis assumes the cap holds**: Scenario 2 does not follow the RPS in any case, and
Dominion's preferred plan indicates 16,100 MW of solar, so the carve-out is met from within that
total and utility-scale is the remainder.

**The consequence, stated rather than buried:** utility-scale new build falls from 8,589 MW at 2035
to 4,583 MW at 2045. That is not a choice a utility would make voluntarily; it is what holding the
cap forces once the energy obligation outgrows the capacity target.

### The profile

Five NSRDB sites averaged — Sterling, Arlington, King George, Richmond, Chesapeake — at **45° due
south, fixed**, on April–March hydro-year boundaries. Design-year capacity factor **0.1526**, the
highest of eight hydro years ranging 0.1420–0.1526.

**45° is not a yield sacrifice.** Measured at Sterling 2016 against a 15° array: December **+31.5%**,
January +29.9%, June −17.5%, and the **year +1.3%**. The December-to-June ratio moves from 0.45 to
0.71 — a far more even year, with the gain landing where peaks, outages and price spreads are.

**No paired storage.** The DER expansion text sets none for distributed resources; the obligation
rests with the utility under § 56-585.5(E).

---

## 8. Agrivoltaic siting

**Applied to 85% of utility-scale solar installed after 2026**, on the same terms as every other
scenario. Carrying it in Scenario 3 alone would give that scenario a benefit stream the others were
denied by construction — and it is unphysical besides, since the same acres are involved either way.

**It changes cost and land, not generation.** A sheep-grazed tracking array generates exactly what a
conventional tracking array generates, because they are the same structures — NREL gives both
5.9 acres/MW.

| year | utility new build | agrivoltaic | capex premium | land |
|---|---:|---:|---:|---:|
| 2030 | 3,655 MW | 3,107 MW | $217M | 18,275–25,585 ac |
| 2035 | 8,589 | 7,301 | $511M | 42,945–60,123 ac |
| 2040 | 6,522 | 5,544 | $388M | 32,610–45,654 ac |
| 2045 | 4,583 | 3,896 | $273M | 22,915–32,081 ac |

**Premium: $0.07/W<sub>DC</sub>**, the low end of NREL's $0.07–0.80 dual-use range, because grazing
*"can use conventional PV structures and does not require as much site preparation or seeding."*
Several site-preparation costs *fall* relative to bare ground — clearing and grubbing −20%, soil
stripping −20%, compaction −30% — since the land was already pasture.

**Cattle are not modelled.** NREL states they cost more, needing elevation and reinforcement, and
gives 9.8 acres/MW against 5.9 — but no equivalent of the $0.07 figure. The code raises rather than
reusing the sheep premium, which would understate it.

**Full method, evidence and citations: `appendices/Appendix_Agrivoltaics.md`.** Capital cost by
configuration is Appendix Q.

---

## 9. Adequacy and new gas capacity

### The shortfall, measured

Gas bounded by the real fleet — **12,216 MW available at 2045** — rather than the unbounded ceiling
the published runner still uses:

| | 2045 |
|---|---:|
| loss of load hours | **5,671** |
| unserved energy | **30.05 TWh**, 14.9% of demand |
| peak shortfall | 10,265 MW |
| events | 1,015, longest 67 hours |

**Every rung runs at 100% capacity factor in all 8,760 hours.** There is no hour of the year where
the existing fleet has spare capacity, including the simple-cycle plant, which is not peaking duty
at all.

### The run-length structure, and why the average misleads

**Median run is 3 hours at every tranche** from 1 MW to 6,000 MW — 1,015 separate blocks. Nothing
clears a combined-cycle unit's six-hour minimum uptime anywhere.

But the gap's **implied capacity factor is 33.4%, above the 28.1% crossover**. So the average points
to combined cycle and the shape points to simple cycle, which is the case the gas reference warns
about: *an average cannot answer a marginal question.*

### The flat shape was an artifact of the existing turbines

Removing the 3,546 MW simple-cycle fleet from the stack entirely changes the picture: the gap grows
to 60.61 TWh and the run-length profile becomes a **staircase** — 12–16 hours at the base, falling to
2–4 hours above 10,000 MW.

**The existing turbines were filling the bottom of the gap**, leaving only its ragged surface
exposed. Both views are correct and neither alone is sufficient: with the fleet, what new plant must
do *given the fleet as it is*; without, what duty the system actually has.

**Roughly 9,000 MW of that duty is genuine combined-cycle work** — which is what the existing
turbines had been standing in for, at an 11.0 heat rate on load that wants 6.4.

### Sizing

Adding a combined-cycle candidate to the stack and re-solving:

| new CCGT | unserved | simple-cycle fleet CF | four-term cost |
|---:|---:|---:|---:|
| 5,000 MW | **zero** | 68.5% | — |
| **6,500 MW** | zero | 40.5% | **$8,307M** |
| 7,000 MW | zero | 29.5% | $8,323M |
| 7,500 MW | zero | 19.0% | $8,342M |
| 9,000 MW | zero | **0%** | — |

**Adequacy sets a floor at 5,000 MW; cost sets the optimum at 6,500.** The extra 1,500 MW is not
needed to serve load — it pays for itself in fuel saved.

**The cost curve is nearly flat**: $35M across a 1,000 MW range, 0.4%. Each 500 MW saves about
$280M of existing fuel and adds about $300M of new-build cost, and they nearly cancel.

**That flatness is itself a finding.** Scenario 2's cost is dominated by fuel on a fleet that must
run hard regardless, so the choice *between* combined and simple cycle moves it far less than the
*quantity* of gas the scenario forces.

**6,500 MW is adopted**, on cost. Two larger figures were considered and rejected: 7,000 and 7,500
MW rest on a criterion — *"keep the simple-cycle fleet at or below its 28.1% crossover"* — that has
no authority behind it. The crossover is a **new-build** decision about when a new combined-cycle
unit's fuel saving repays its capital; the existing turbines have sunk capital and a zero-intercept
screening curve, so the rule does not transfer to them.

**Adequacy testing may revise this upward.** Simple-cycle plant at 40.5% capacity factor has less
headroom for a forced outage than at 29.5%, and the loss-of-load metrics that would settle it need
the draw loop described in `Common_Reference.md` section 3.

### The units

**Six H-Class multi-shaft combined-cycle units, 1,083 MW each — 6,498 MW.** Gas Turbine World 2024
Handbook: 59.4% efficiency, $12.20/kW-yr fixed O&M.

**Two megawatts under the 6,500 MW optimum — 0.03%.** Solved at the discrete figure, the result is
identical: $8,307M/yr, simple-cycle fleet at 40.5%. Discreteness costs far less here than in
Scenario 1B, where 1,278 MW continuous becomes 1,422 MW as six F-Class units — an 11% overshoot.

**Capital is not taken from that source.** Gas Turbine World's $950/kW is equipment-era; this
analysis uses `ccgt_capex_kw` at **$3,000/kW**, Wood Mackenzie April 2026, as full installed project
cost. The $2,400/kW figure recorded in `new_peaker_ccgt_costs_by_size.md` as this project's own is
itself superseded.

**Scenario 2 is explicitly exempt from the simple-cycle-only new-build rule** that governs the other
scenarios. That rule's own text carves it out, and its rationale — written for *"short-duration (a
few hours at a time) gap-filling needs"* — does not describe a shortfall spanning 65% of the year.

### Not yet in the reported figure

The published annualised cost does **not** include this capacity. The runner still uses the
unbounded gas ceiling, so it reports zero unserved energy while the bounded run shows 30.05 TWh.
**Reconciling the two is the open work** — dashboard step 6, tracker activity 83.
