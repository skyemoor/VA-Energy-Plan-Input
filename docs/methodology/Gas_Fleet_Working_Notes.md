# Gas Fleet — Working Notes

> **Model-wide context: `docs/MODEL_WIDE_FINDINGS.md`.** The single-gas-price problem recorded
> here is one of three causes of a flat hourly energy price affecting all scenarios.

**Read this before using or changing any gas assumption.** Consolidates heat rates, the merit
order, capacity per rung, cost structure, retirement schedules, and the open problems. Supersedes
scattered treatment in `Gas_Merit_Order.md` (heat rates) and `VA_gas_capacity_schedules.md`
(retirements), both of which remain authoritative for their own narrower topics.

Last updated 2026-09-11.

---

## 0. Terms used here, defined once

Defined because several are used loosely in the literature and at least two have caused confusion
in this project.

**Heat rate** — fuel energy consumed per unit of electricity produced, in **MMBtu/MWh** here
(equivalently Btu/kWh × 1,000). Lower is more efficient. A 6.4 heat rate burns 6.4 MMBtu of gas to
make 1 MWh. Multiply by fuel price ($/MMBtu) to get fuel cost per MWh.

**VOM — Variable Operations and Maintenance.** The non-fuel cost that scales with generation:
consumables, water treatment, and the maintenance attributable to running rather than to existing.
In $/MWh. **Distinct from FOM** (Fixed O&M), which is incurred whether or not the plant runs and is
quoted in $/kW-year. Our `CCGT_VOM_MWH = 3.0`.

**Marginal cost** — fuel cost + VOM, for one more MWh from a unit already running. This is what
sets price in an economic dispatch. It excludes capital, FOM, and start-up costs.

**VOLL — Value of Lost Load.** What it costs society when demand cannot be served, in $/MWh. Used
in the LP as `UNSERVED_PENALTY = 100,000`. **This is a penalty, not a price** — it is set high
enough that the optimiser will do almost anything to avoid unserved energy, rather than being an
estimate of actual damages. Real scarcity prices in PJM top out two orders of magnitude lower
(see §5).

**Dual (shadow price)** — the marginal value of relaxing a constraint by one unit, produced by the
LP solver alongside the primal solution. For the hourly energy-balance constraint, the dual is the
marginal cost of serving one more MWh in that hour — **the LP's internal equivalent of an energy
price**. It is not an LMP: it has no congestion or loss components, and it reflects the LP's own
optimised dispatch rather than a market clearing.

**Merit order** — generating units ranked by marginal cost, dispatched cheapest-first. The price in
any hour is set by the most expensive unit running. **Without a merit order there is only one price
and the dual cannot vary** — which is the central problem recorded in §6.

**LMP — Locational Marginal Price.** PJM's nodal price = system energy component + congestion
component + marginal loss component. Our `distributed_exogenous_price_mwh` supplies only the
**latter two**; the energy component reaches the distributed segment through the LP's energy
balance instead.

**CC / CCGT — Combined Cycle (Gas Turbine).** Gas turbine plus heat-recovery steam generator and
steam turbine. Efficient, slower to start, serves base and intermediate load.

**CT — Combustion Turbine**, also *simple cycle* / *SCGT* / *peaker*. Gas turbine alone, exhaust
heat discarded. Less efficient, fast-starting, serves peaks. **Aeroderivative** CTs (jet-engine
derived) are more efficient and faster-starting than **frame** CTs; the distinction matters because
their heat rates differ by roughly 15%.

**EOH — Equivalent Operating Hours.** A maintenance-accounting measure combining running hours with
start-stop cycles, used to schedule overhauls. Appears in the retirement analysis.

---

## 1. Heat rate tiers — sourced

**EIA Electric Power Annual Table 8.2**, "Average Tested Heat Rates by Prime Mover and Energy
Source," Form EIA-860, capacity-weighted, 2024 natural gas:

| prime mover | Btu/kWh |
|---|---:|
| Combined Cycle | **7,548** |
| Gas Turbine | **10,999** |
| Steam Generator | 10,337 |
| Internal Combustion | 8,924 |

**CCGT by vintage** (EIA *Today in Energy* #61444, #60984): 2014–2023 entry below 7,000;
2010–2022 at 6,960; 2000–2009 at 7,479; 1990–1999 around 9,010.

### The stack

| tier | heat rate | 2030 fuel | 2045 fuel |
|---|---:|---:|---:|
| `ccgt_modern` | 6.400 | $34.56 | $44.32 |
| `ccgt_fleet` | 7.548 | $40.76 | $52.27 |
| `ccgt_legacy` | 9.010 | $48.65 | $62.39 |
| `ct_aeroderivative` | 9.500 | $51.30 | $65.79 |
| `ct_fleet` | 10.999 | $59.39 | $76.17 |
| **spread** | | **1.72×** | **1.72×** |

**Our simple-cycle assumption is optimistic.** `SIMPLE_CYCLE_HEAT_RATE = 9.5` is 14% better than
EIA's gas-turbine fleet average of 11.0. It describes a modern aeroderivative unit, not the fleet.
Any result treating 9.5 as "the" peaker cost understates marginal peaking cost by about 14%. Both
are kept as separate tiers because they describe genuinely different machines.

---

## 2. Capacity per rung — Dominion-owned fleet

**Source: Dominion Energy Form ARS FY2023** (SEC filing), "Virginia Power Utility Generation," net
summer capability. This gives plant, CC/CT designation, and MW directly.

| plant | type | MW | COD | rung |
|---|---|---:|---|---|
| Greensville County | CC | 1,605 | 2018 | `ccgt_modern` |
| Brunswick County | CC | 1,376 | 2016 | `ccgt_modern` |
| Warren County | CC | 1,349 | 2014 | `ccgt_modern` |
| Ladysmith | CT | 782 | 2001 | `ct_*` — see caveat |
| Bear Garden | CC | 622 | 2011 | `ccgt_fleet` |
| Remington | CT | 619 | ~2000 | `ct_*` |
| Possum Point | CC | 573 | *unconfirmed* | `ccgt_legacy`? |
| Chesterfield | CC | 386 | *unconfirmed* | `ccgt_legacy`? |
| Elizabeth River | CT | 327 | *unconfirmed* | `ct_*` |
| Gordonsville Energy | CC | 218 | ~1990s | `ccgt_legacy` |
| Gravel Neck | CT | 170 | *unconfirmed* | `ct_*` |
| Darbytown | CT | 168 | *unconfirmed* | `ct_*` |
| **Total Dominion gas** | | **8,195** | | 43% of Dominion capacity |

### Rung totals, Dominion-owned

| rung | MW | confidence |
|---|---:|---|
| `ccgt_modern` | **4,330** | **high** — all three CODs confirmed, all 2014+ |
| `ccgt_fleet` | **622** | **high** — Bear Garden COD 2011 confirmed |
| `ccgt_legacy` | **1,177** | **low** — Possum Point, Chesterfield, Gordonsville vintages unconfirmed |
| CT (all) | **2,066** | **medium** on total, **none** on aero/frame split |

### Three caveats that matter

**The aeroderivative/frame split is entirely unresolved.** All 2,066 MW of CT capacity is assigned
to "CT" with no basis for allocating between `ct_aeroderivative` (9.5) and `ct_fleet` (11.0) — a
14% cost difference on the units that set peak prices. This is the single largest gap in the rung
mapping.

**This is Dominion-owned only.** It excludes independent power producers in the DOM zone — Doswell
(~1,313 MW), Tenaska Virginia (~975–1,011 MW), Panda Stonewall (~812 MW), Marsh Run (~709 MW),
Louisa (~509 MW), Hopewell (~399 MW). `VA_gas_capacity_schedules.md` Schedule A carries **9,362
MW** for 2026–2040, which is neither the 8,195 Dominion-owned figure nor the Dominion-plus-IPP
total. **That discrepancy is unreconciled** and should be resolved before the rungs are wired in.

**Capacity figures vary by source.** Dominion's own 10-K gives Brunswick 1,376 MW; a state
inventory gives 1,472 MW; press coverage says "1,300 MW." These are net summer capability, nameplate,
and rounded announcement figures respectively. **Use the 10-K column consistently** — it is the
filed, audited number and is internally consistent across plants.

---

## 3. Cost structure

`gas_cost_mwh(year, heat_rate)` — fuel only, Deloitte/MEDIUM gas price trajectory, piecewise-linear
interpolation. `gas_cost_mwh_eia(year)` is an alternative trajectory sharing the 2026 starting
point ($3.70/MMBtu); a HIGH case also exists.

`CCGT_VOM_MWH = 3.0`. **No separate CT VOM constant exists** — CT VOM is typically higher than
CCGT (more starts, more cycling wear), so using 3.0 for peakers understates their marginal cost on
top of the heat-rate optimism noted above.

`heat_rate` is a **required** argument with no default, corrected 2026-08-16 after a bug in which
it silently defaulted.

---

## 4. Retirement schedules

See `VA_gas_capacity_schedules.md` for the authoritative treatment. Two distinct schedules:

**Schedule A** (physical/data-driven): 9,362 MW 2026–2040; 8,740 after Bear Garden retires 2041;
7,391 after Warren County retires 2044.

**Schedule B** (VCEA-driven): same as A through 2044, then **1,860 MW** in 2045 (Chesterfield +
Doswell + Possum Point), with Brunswick + Potomac Energy Center + Greensville (3,774 MW) retiring
for lack of market.

**Unconfirmed:** eight of ten peaker/mixed plants show zero generation since Dec 2024. Cause
unknown — retirement, standby, or a reporting gap specific to smaller plants. Treated
conservatively as unavailable.

---

## 5. What sits above the merit order — unresolved

The stack currently terminates at the dearest gas tier and then jumps straight to
`UNSERVED_PENALTY = 100,000/MWh`. **There is no rung between "gas is running" and "the lights go
out."**

Two things are missing:

**Imports.** There is **no import variable in the model at all** (`export` exists, capped, earning
`export_price_mwh`; `import` has zero occurrences). Virginia is modelled as an island that can sell
into PJM but never buy. Dominion imports substantially in reality, so this likely **overbuilds** —
but unlimited imports would collapse the build, and the honest position is that imports are
available *except* during regionally correlated scarcity, which is exactly when they are needed.

**A scarcity price tier.** Real PJM scarcity tops out around **$1,000–2,000/MWh** under the offer
cap — the mechanism behind the $1,240/MWh real-time print at the Dominion Hub on 3 September 2026.
Between our dearest gas tier ($76.17 at 2045) and $100,000 there is nothing.

**Deferred by decision, to be taken up as its own work.**

---

## 6. Why this matters: the flat dual

The LP's hourly energy-balance dual at 2030 is **$54.70 in all 8,760 hours — one unique value,
zero variance** (measured 2026-09-11, `Scenario3_Technical_Notes.md`).

$54.70 = $51.30 simple-cycle fuel + $3.00 VOM. **The marginal resource is simple-cycle gas, priced
identically in every hour.** With one gas price, no operating reserve constraint active, and
unconstrained storage arbitrage, the dual has nothing to vary against.

Real Virginia nodes on the same month-hour averaging basis show **$211–316 daily spreads**; PJM
real time hit **$1,240** on 3 September 2026.

**The merit order is one of three fixes**, and not sufficient alone:

| gap | status |
|---|---|
| Single gas price → merit order | tiers sourced (§1), **capacity per rung partly sourced (§2)**, not wired in |
| No operating reserve | `all_hours_reserve.py` **exists and is documented as "current standard" but is not called by anything** |
| No scarcity/import tier above gas | **not started** (§5) |

---

## 7. Open items

1. **Aeroderivative/frame CT split** — 2,066 MW unallocated across a 14% cost difference, on the
   units that set peak prices. Largest gap in the mapping.
2. **Reconcile 8,195 (Dominion 10-K) against 9,362 (Schedule A)** — IPP inclusion is the likely
   explanation but is not documented.
3. **Vintages for Possum Point, Chesterfield, Elizabeth River, Gravel Neck, Darbytown.**
4. **A CT-specific VOM constant** — using CCGT's 3.0 understates peaker marginal cost.
5. **The Dominion IRP PDFs in the project folder are truncated and unreadable** — no `/Root`
   object, confirmed with both `pypdf` and `pdfplumber`. Other work may depend on them.
6. **Imports and scarcity pricing** (§5), deferred as its own work set.
