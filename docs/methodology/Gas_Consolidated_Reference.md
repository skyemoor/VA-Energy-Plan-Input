# Gas — consolidated reference

**One file for every gas question.** Consolidated 2026-09-13 from seven separate documents, because
the fragmentation was costing real time: the CT capex figures this project needed were sitting in
`new_peaker_ccgt_costs_by_size.md` while `Gas_Technology_Selection_By_Scenario.md` recorded "no
simple-cycle capex exists in the code" as an open gap. Two files, opposite claims, neither aware of
the other.

## Where to look

| question | section |
|---|---|
| What do the terms mean? | **1. Definitions** |
| What does gas cost to run? | **2. Heat rates and the merit order** |
| How much gas capacity is there? | **3. Capacity, by rung and by plant** |
| When does each plant retire? | **4. Retirement schedules** |
| How fast can it ramp? What isn't modelled? | **5. Operating constraints** |
| What does new gas cost to build? | **6. New-build capex by size tier** |
| What does gas cost over its lifecycle? | **6A. Lifecycle costing** |
| How long do turbines last? | **7. Lifespans, EOH and overhaul** |
| Which technology does each scenario assume? | **8. Technology selection by scenario** |
| Which technology fits the actual gaps? | **8 → Gap-driven technology matching** |
| How is the gas fraction derived? | **9. Deriving gas_allowed_frac** |
| What is still open? | **10. Open items** |

## The three figures most often needed

| | |
|---|---:|
| DOM-zone gas, nameplate | **13,639.4 MW** |
| Marginal cost range at 2045 | **$47.32 – $81.17/MWh** |
| Scenario 2's implied gas peak at 2045 | **22,479 MW** |
| ...of which NEW build required | **10,262 MW** |
| CCGT/CT crossover capacity factor | **28.1%** (central) |
| Bath County, Dominion's dispatchable share | **1,808 MW / 14,464 MWh** |

---

## The fleet, as the model uses it

Every figure below is what the code applies, not a nearby source value. Sourcing follows each table.

### Existing fleet available — `driver.schedule_b_baseline_mw(year)`

| year | MW |
|---|---:|
| 2026–2044 | **9,362** |
| 2045 onward | **1,860** |

A step, not a ramp: VCEA-driven retirement at 2045 leaves Chesterfield, Doswell and Possum Point.

### Retain / overhaul pool — `driver.POOL`, 2,862 MW

**Gas capability**, Dominion 2024 Annual Report (SEC, `dei-ars-12312024.pdf`), *Virginia Power
Utility Generation*, Net Summer Capability. Listed youngest first, which is the order
`select_overhaul_retain()` draws from.

| plant | MW | commissioned | needs overhaul |
|---|---:|---|---|
| Marsh Run | 550 | 2004 | no |
| Louisa | 525 | 2003 | no |
| Wolf Hills | 285 | 2001 | no |
| Remington | 619 | 2000 | no |
| Gordonsville | 218 | 1994 | **yes** |
| Elizabeth River | 327 | 1992 | **yes** |
| Darbytown | 168 | 1990 | **yes** |
| Gravel Neck | 170 | 1989 | **yes** |
| **Total** | **2,862** | | |

The four flagged for overhaul are all at or beyond nominal 30–45 year CT life by 2045. Overhaul
costs $11.4M/yr against $77.0M/yr for equivalent new build.

**Gravel Neck and Darbytown look wrong against other sources and are not** — see §"The retain-pool
MW figures are GAS capability" below.

### Capacity cap by scenario — `apply_gas_cap()`

| year | Scenario 1 / 3 | Scenario 1B | RPS gas allowance |
|---|---:|---:|---:|
| 2026 | 12,224 | 12,224 | 71.0% |
| 2030 | 12,224 | 12,224 | 59.0% |
| 2035 | 12,224 | 12,224 | 41.0% |
| 2040 | 12,224 | 12,224 | 21.0% |
| 2044 | 12,224 | 12,224 | 5.0% |
| **2045** | **4,722** | **6,000** | 0.0% |

Cap = Schedule B baseline + the 2,862 MW pool. **Scenario 1B alone diverges at 2045**, adding
1,278 MW of new simple-cycle CT at $2,000/kW — the figure Appendix N.2's capacity sweep selected
and which `select_overhaul_retain()` independently reproduces.

For Scenario 1 the 2045 cap is immaterial: its gas target is 0%, so nothing dispatches.

### Heat rates, MMBtu/MWh

| | |
|---|---:|
| CCGT, existing and modern new-build | **6.4** |
| CT fleet | **10.999** |
| CT aeroderivative | 9.5 |

The aeroderivative rate is defined but **not applied to any Dominion unit** — the CT split was
settled as entirely frame.

### Fleet totals, DOM zone

| basis | MW |
|---|---:|
| nameplate | **13,639.4** |
| net summer | **12,414.1** |
| net winter | **13,673.4** |

EIA-860, after correcting a filter that had excluded every merchant IPP — see §"The 1,167 MW
discrepancy".

---

> **Model-wide context: `docs/MODEL_WIDE_FINDINGS.md`.** The single-gas-price problem recorded
> here is one of three causes of a flat hourly energy price affecting all scenarios.

**Read this before using or changing any gas assumption.** Consolidates heat rates, the merit
order, capacity per rung, cost structure, retirement schedules, and the open problems. Supersedes
scattered treatment in `Gas_Merit_Order.md` (heat rates) and `VA_gas_capacity_schedules.md`
(retirements), both of which remain authoritative for their own narrower topics.

Last updated 2026-09-11.

---

## Provenance of this file

Seven files cover gas. **This one is the entry point**; the others remain authoritative for their
own topics. Check all of them before adding new gas material — this note was itself written on
2026-09-11 without checking `docs/research/`, which already held two of them.

| file | authoritative for |
|---|---|
| **this file** | definitions, heat rates, merit order, capacity per rung, what sits above the stack |
| `VA_gas_capacity_schedules.md` | **retirement schedules A and B** |
| `Gas_Technology_Selection_By_Scenario.md` | **which gas technology each scenario assumes**; records an open gap — no simple-cycle capex in the code |
| `METHODOLOGY_gas_allowed_frac_derivation.md` | gas fraction derivation for the LP |
| `research/Gas_turbine_lifespans_reference.md` | **CCGT and CT lifespans, EOH thresholds, overhaul windows** |
| `research/new_peaker_ccgt_costs_by_size.md` | **new-build capex by size tier**, and the overhaul-vs-new-build rule |
| `Gas_Merit_Order.md` | heat rate tiers and EIA sourcing — largely subsumed here |

### The retain-pool MW figures are GAS capability, not plant total

**Resolved 2026-09-14** against Dominion's **2024 Annual Report** (SEC, `dei-ars-12312024.pdf`),
*Virginia Power Utility Generation*, Net Summer Capability. Every retain-pool figure matches that
table's **Gas** column exactly.

**Gravel Neck and Darbytown are dual-fuel and appear twice** — once under Gas, once under Oil:

| plant | our pool | AR gas | AR oil | total | EIA-860 net summer |
|---|---:|---:|---:|---:|---:|
| Gravel Neck | **170** | 170 | 198 | 368 | **368** |
| Darbytown | **168** | 168 | 168 | 336 | 340 |
| Elizabeth River | 327 | 327 | — | 327 | 325 |
| Gordonsville | 218 | 218 | — | 218 | 218 |
| Remington | 619 | 619 | — | 619 | — |

So EIA-860's net summer is **gas plus oil**, and Dominion's own Power Stations page quotes the same
combined figure. Gordonsville and Elizabeth River match directly because they are **not dual-fuel** —
which is exactly why they appeared inconsistent with the other two.

**The apparent 0.46 ratio was a fuel split, not a capacity discrepancy.** A change to `GAS_POOL_MW` —
a constant reaching every scenario's `apply_gas_cap()` — was nearly proposed on the strength of it.

### The "zero generation since Dec 2024" reading was too pessimistic

The EIA monthly series for these plants **ends** at December 2024; it does not fall to zero there.

| | Jul 2024 | Oct 2024 | Dec 2024 |
|---|---:|---:|---:|
| Gravel Neck | 40,380 | 19,780 | 1,999 |
| Darbytown | 42,561 | 18,562 | 13,916 |
| Elizabeth River | 4,145 | 1,915 | 561 |

Darbytown's 42,561 MWh on a 336 MW plant is a 17% capacity factor — ordinary peaker duty. The
near-zero months are seasonal and recur every February and December in prior years.

**EIA-860 (2025 vintage, postdating that cutoff) lists every Gravel Neck and Darbytown unit as `OP`.**
The third of the three hypotheses recorded in `VA_gas_capacity_schedules.md` — a reporting gap
specific to smaller plants — is the one the evidence supports.

**Elizabeth River is the genuine exception**: all three units are `SB` (standby), and output had
already fallen to a fraction of 2023 levels through 2024.

### Sources used, and what each is good for

| source | what it gives | what it does not |
|---|---|---|
| **Dominion 2024 Annual Report** (SEC, `dei-ars-12312024.pdf`), *Virginia Power Utility Generation* | Net summer capability **by plant and by fuel**; ownership footnotes | current availability |
| **Dominion 2025 IRP Update**, Appendix 3A(iv–v) | Unit-level nameplate, as directed by the SCC | net ratings; dual-fuel split |
| **Dominion 2025 IRP Update**, Figure 3.1.1.1 | Net summer by resource type, 2024 mix | plant detail |
| **EIA-860 (2025)** | Unit-level nameplate *and* summer, **operating status** | fuel split on dual-fuel units |
| **EIA monthly generation** | Actual output by plant | anything after Dec 2024 |
| **Dominion Power Stations pages** | Net generating capacity per station | fuel split; availability |
| gridinfo.com, Global Energy Monitor | — | **not independent**: both re-serve EIA data on the same Dec 2024 cutoff |

**The last row matters.** Both were cited as corroboration during this work before
`VA_gas_capacity_schedules.md` was re-read, which had already dismissed them in those terms.

### Bath County is 1,808 MW to Dominion, not 3,000

The same Annual Report table lists **Bath County — 1,808 MW**, footnote (3): the *"40% undivided
interest owned by Allegheny Generating Company."* The 2025 IRP Update's Figure 3.1.1.1 gives
Pumped Storage at the same **1,808 MW** net summer.

3,003 × 0.60 = 1,802.

### Ownership, and why the limit is contractual rather than physical

**Dominion operates the station but owns 60%.** The 40% minority share has moved through mergers and
now sits with **FirstEnergy's Allegheny Generating Company** and **LS Power / Bath County Energy** —
which is why the Annual Report footnote names only Allegheny while the current split is broader.

| | entitlement |
|---|---:|
| Dominion Energy (60%) | **~1,802 MW** |
| Minority owners (40%) | ~1,201 MW |

**The binding limit is an entitlement, not a transmission constraint**, and the distinction matters
for how the model's bound is justified. Bath is fully integrated into PJM, and its output is
dispatched against joint entitlements and regional reliability across several states — Dominion
cannot unilaterally route or monopolise the plant. But **nothing about that is imposed by AEP or any
transmission owner**: the limit is contractual.

So 1,808 MW is the correct bound for a DOM-zone LSE model for a reason that has nothing to do with
wires. A reader who assumed it was a transmission limit might expect it to relax with grid upgrades.
It would not.

**Sources:** Dominion 2024 Annual Report footnote (3); 2025 IRP Update Figure 3.1.1.1; Dominion's
Bath County Pumped Storage Station pages; FERC notice 2026-07124 naming Virginia Electric and Power
Company, Allegheny Generating Company and the LS Power entity together.

**Changed 2026-09-14.** This model serves the DOM zone, so what matters is what Dominion can
dispatch:

| | before | **now** |
|---|---:|---:|
| `BATH_MW` | 3,000 | **1,808** |
| `BATH_MWH` | 24,000 | **14,464** |
| duration | 8.0 h | 8.0 h |

`BATH_MWH` follows the same share rather than being measured separately: an undivided interest is a
share of the whole works — reservoir, penstocks and machines alike — so the energy rating scales
with the power rating. The unchanged duration is the check that the share was applied consistently.

**It reaches three problem builders and the reserve constraint** — `build_problem`,
`build_dispatch_problem`, `build_scenario2_problem`, and the reserve credit added the same day. So
**every scenario's dispatch moves, Scenario 2 included.** All published figures predate this.

*Nameplate reconciliation, retained for reference:* the 2025 IRP Appendix 3A(iv–v) directs 6 × 477 =
2,862 MW; EIA-860 lists 9 units totalling 3,109.3 MW; 3,000 is the commonly cited plant figure. The
model no longer uses any of these — it uses Dominion's share.

---

**Lead on the unresolved CT split:** `new_peaker_ccgt_costs_by_size.md` distinguishes a small tier
(20–50 MW) described as *fast-deployment, aeroderivative* from medium (100–250 MW) and larger
frame-scale tiers. Dominion's CT fleet — Ladysmith 782, Remington 619, Elizabeth River 327, Gravel
Neck 170, Darbytown 168 — sits mostly well above the aeroderivative size band, which **suggests the
2,066 MW is predominantly frame** and therefore closer to the 11.0 heat rate than 9.5. That is an
inference from size, not a sourced unit-type finding, and is recorded as a lead rather than a
resolution.

---

# 1. Definitions

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

# 2. Heat rates and the merit order

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

# 3. Capacity, by rung and by plant

**Source: EIA-860 2025, Schedule 3 (Generator Data)**, Virginia file, Operable sheet, filtered to
`Energy Source 1 = NG` and `Utility Name = Virginia Electric & Power Co`. Rungs assigned by
per-unit **Operating Year**.

| rung | nameplate MW | units | basis |
|---|---:|---:|---|
| `ccgt_modern` | **4,717.7** | 12 | operating year ≥ 2014 |
| `ccgt_fleet` | **1,172.0** | 6 | 2000–2013 |
| `ccgt_legacy` | **747.0** | 8 | pre-2000 |
| `ct_fleet` | **2,722.8** | 20 | all frame — see below |
| **total** | **9,359.5** | 46 | |

### The CT aero/frame split — settled, entirely frame

Established from per-unit nameplate rather than inferred:

| plant | units × MW | year |
|---|---|---|
| Ladysmith | 5 × 178.5 | 2001, 2008–09 |
| Remington | 4 × 170–178.5 | 2000 |
| Elizabeth River | 3 × 129.6 | 1992 |
| Gravel Neck | 4 × 91.9 | 1989 |
| Darbytown | 4 × 92.1 | 1990 |

**Aeroderivative machines are 36–54 MW** (GE LM6000: 44.5–53.8). **Not one Dominion unit is in
that class.** Statewide, 91.9% of Virginia simple-cycle capacity is frame — 4,426 of 4,814 MW —
with only 388 MW across eight units under 60 MW, none of it Dominion's.

**Use `GAS_HEAT_RATE_CT_FLEET` (10.999) for the existing fleet.** `GAS_HEAT_RATE_CT_AERODERIVATIVE`
(9.5) stays defined for **new-build** analysis where a specific machine is chosen, and must not be
applied to these units — doing so would understate their marginal cost by 14%.

### The 1,167 MW "discrepancy" was a units mismatch, not missing capacity

An earlier version of this note recorded an unreconciled gap between the Dominion 10-K's 8,195 MW
and Schedule A's 9,362 MW, and offered two explanations — IPP capacity, then ODEC capacity. **Both
were wrong.**

| basis | MW |
|---|---:|
| 10-K, **net summer capability** | 8,195 |
| EIA-860, **nameplate** | **9,359.5** |
| Schedule A (`VA_gas_capacity_schedules.md`) | 9,362 |

Schedule A agrees with nameplate to within **2.5 MW** — rounding. And 8,195 / 9,359.5 = **87.6%**,
a normal summer derate on gas turbines.

**Same fleet, two rating bases.** The lesson is procedural: the ratio was a plausible derate factor
all along, and checking the units before hypothesising would have saved two wrong answers. Both
figures are now retained as separately named constants so the mistake cannot repeat silently.

### What EIA-860 does *not* resolve

The **Schedule 2 (Plant Data)** file carries no capacity or prime mover, but it did correct two
ownership assumptions: `Gordonsville Energy LP` and `Hopewell Power Station` are **Virginia Electric
& Power Co** despite LP-style names, and `Marsh Run` and `Louisa` belong to **Old Dominion Electric
Cooperative** — a separate DOM-zone utility (1,142.4 MW of gas), not IPPs and not in Schedule A.

Genuine DOM-zone IPP gas: Doswell (1,313.0 MW), Tenaska Virginia (1,011.4), Potomac Energy Center
(812.0), Luminant/Hopewell Cogeneration (399.0).

## 2A. The dispatch stack — `lp_package/gas_merit_order.py`

Built 2026-09-12. `GasMeritOrder` owns cost per rung, capacity per rung, and capacity net of
retirements and availability in a given year.

**Why it is more than added realism.** The LP's hourly dual has zero variance at 2030 because gas
is on the margin in every hour and there is one gas price — so the marginal cost of one more MWh is
the same whether gas runs at 10% or 90%. Gas *output* already varies enormously across the day;
gas *marginal cost* does not, and the dual tracks the second. Every mechanism that should create
intraday price structure — less gas at midday, battery cycling cost, wind variation — is a
**quantity** effect without a stack and a **price** effect with one.

### Scope: all DOM-zone merchant gas

Expanded from Dominion-owned by decision. **Potomac Energy Center sits close to the Loudoun
data-center concentration and will be dispatched whenever prices allow** — and prices have been
high — so a Dominion-only stack would omit capacity that genuinely serves zonal load. Doswell,
Marsh Run (ODEC), Louisa (ODEC) and Gordonsville are in for the same reason.

**Two exclusions, both deliberate:**

- **APCo territory** — Clinch River, Wolf Hills, Buchanan and the southwest Virginia industrial
  units are in Appalachian Power's zone. Filtered by county, since EIA-860 carries no PJM zone field.
- **CHP** — Hopewell Cogeneration, Celanese, Radford Army Ammunition, Virginia Tech, Spruance and
  others run to serve **host steam loads, not economic dispatch**. Including them would imply a
  dispatch decision their operators do not make.

### Three rating bases, all retained

| basis | meaning | DOM-zone total |
|---|---|---:|
| nameplate | manufacturer rating at ISO conditions (59°F) | **13,639.4 MW** |
| net summer | sustained output at ~95°F, net of station service | **12,414.1 MW** |
| net winter | same at winter ambient | **13,673.4 MW** |

> **FIGURES REVISED 2026-09-13.** The CHP exclusion was written as
> `~Sector.str.contains('CHP')` — and **`'IPP Non-CHP'` contains the substring `'CHP'`**, so the
> filter removed every *non*-CHP independent producer: exactly the merchant plant it was meant to
> keep. **Doswell (1,313 MW), Tenaska Virginia (1,011) and Potomac Energy Center (812) were all
> dropped — 3,136 MW, about 30% of the DOM-zone fleet.** The correct test is
> `endswith('CHP') & ~contains('Non-CHP')`. Nineteen plants now, not fifteen.

`capacity_basis` is an explicit constructor argument defaulting to `net_summer`, and an invalid
value raises. **Mixing nameplate with net summer created a phantom 1,167 MW discrepancy on
2026-09-11 and produced two wrong hypotheses before the units were checked** — making the basis a
named choice prevents a repeat.

**Winter capability exceeds summer by 10.1%**, because cold dense air raises compressor mass flow.
That matters here: **the DOM zone now peaks in winter** — 25,413 MW (2025–26) against 23,905 MW
(summer 2025), with winter growing +45% since 2019–20 against +23%. If the binding hour is a winter
evening, which a high-solar system makes likely, **net summer is the wrong derate** and understates
gas at the hour that sizes the fleet.

**The counter-argument, recorded because it is not modelled:** winter *capability* is not winter
*deliverability*. Pipeline constraints and competition with heating load can make gas unavailable in
a cold snap whatever the turbine could produce. Using net winter uncaveated would overstate
cold-snap availability.

### The stack (net summer basis)

| rung | 2030 marginal | 2045 marginal | 2045 MW |
|---|---:|---:|---:|
| `ccgt_modern` | $37.56 | $47.32 | 2,742.5 |
| `ccgt_fleet` | $43.76 | $55.27 | 526.2 |
| `ccgt_legacy` | $51.65 | $65.39 | 555.7 |
| `ct_fleet` | **$64.39** | **$81.17** | 3,089.4 |
| **spread** | **$26.83** | **$33.85** | |

**$26.83/MWh of intraday spread at 2030 from gas alone**, before any scarcity pricing.

### The new-build rung, and two gas limits that disagree

**Added 2026-09-13.** The stack covered only the existing EIA-860 fleet, so the **2,862 MW
new-build pool** that `apply_gas_cap()` has always included **had no rung and could not dispatch at
all.** Any scenario relying on new gas was silently denied capacity it was granted — most
consequentially **Scenario 1B, whose whole premise is 5% gas from 2045.**

`new_build_ccgt` uses `GAS_HEAT_RATE_CCGT_MODERN` (6.4) and prices **identically to
`ccgt_modern`** — they are the same technology, differing only in whether the plant exists. Two
rungs at one price is intentional: dispatch cannot distinguish them, but **capacity accounting
must**, since one counts against the existing-fleet schedule and the other against the pool.

*If a scenario instead assumes new **peakers**, use `GAS_HEAT_RATE_CT_AERODERIVATIVE` (9.5). That is
the one case where the aeroderivative figure is right — new build is where a specific machine is
actually chosen, unlike the existing fleet, which is 100% frame.*

### Two independent gas limits, and the direction flips

| year | scenario cap | stack available | binds |
|---|---:|---:|---|
| 2030–2040 | 12,224 | 14,054 | **cap** |
| 2045 | 4,722 | 12,216 | **cap** |

**The direction no longer flips.** Before the filter fix the stack bound at 2030–2040 and the cap
at 2045, and that flip was itself the finding. With the merchant IPPs restored the stack no longer
binds anywhere — **the scenario's own gas allowance governs throughout**, which is the more
comfortable outcome: how much gas can run is decided by the scenario definition rather than by an
incidental fleet-availability figure.

`apply_gas_cap()` returns `schedule_b_baseline_mw(year) + 2,862`, applied as a **per-hour** upper
bound on gas. The stack applies its own hourly availability. **Whichever binds first governs**, and before 2026-09-13 nobody
had decided which should.

**The cause is that they use different retirement schedules.** The stack applies **Schedule A**
(physical: Bear Garden 2041, Warren County 2044). `schedule_b_baseline_mw` applies **Schedule B**
(VCEA-driven: a drop to 1,860 MW in 2045). **One model, two retirement futures.**

**They are not, however, in conflict as concepts** — they constrain different quantities and both
should apply:

- **The cap limits how much gas capacity may EXIST.** Capacity is permitted, financed and retired
  in nameplate terms, which is the right basis for that constraint.
- **The stack limits how much can RUN in a given hour** — net summer capability × availability.

A fleet can be capped at 13,639 MW nameplate *and* only deliver 12,414 MW on a summer afternoon.
Consistent statements.

**Dispatch should use actual available energy.** Nameplate is a rating, not deliverable output. And
the flat availability factor is not merely a convenience: gas maintenance would naturally go into
low-demand shoulder seasons, but **the nuclear profile already dips there**. With no scheduling
freedom left to exploit, a flat derate is the honest representation.

**Doswell is now in the stack** (split `(CC)` 1991–92 → `ccgt_legacy` and `(CT)` 2001/2018 →
`ct_fleet`, since summing would put 1,313 MW on whichever rung was chosen). So Schedule B naming it
among the 2045 survivors is consistent.

**Still unresolved:** Tenaska and Potomac Energy Center appear in **neither** schedule — the
schedules are Dominion-owned documents and reconcile to VEPCO's 9,362 MW, while the stack is
DOM-zone merchant. Different scopes by construction, not by error. It is in the stack's DOM-zone scope but not in a Dominion-owned
schedule, so the two are not counting the same fleet. `reconcile_with_scenario_cap()` surfaces all
of this rather than letting it bind silently. See issue #18.

### CT VOM — sourced, and it was understated

`CT_VOM_MWH = 5.00`, from **NREL ATB** (2022: NGCT $5.00 vs NGCC $2.00; 2020: OCGT $4.49 vs CCGT
$1.61 — a 2.5–2.8× ratio reflecting more starts and cycling wear). Peakers previously used
`CCGT_VOM_MWH = 3.00`. **That compounded with the heat-rate finding** — frame at 11.0, not
aeroderivative at 9.5 — both understating the rung most likely to set price.

*Inconsistency recorded rather than reconciled:* our `CCGT_VOM_MWH = 3.00` sits above ATB's $2.00
for the same technology. The ATB absolute is used for CT because it is sourced; the CCGT constant's
provenance should be revisited.

# 4. Retirement schedules

Two DISTINCT schedules, for two genuinely different purposes. Do not use
interchangeably. This version adds Chesterfield's corrected, gas-only EOH
figure and walks back the "confirmed retired" language for seven plants
after independent verification came back inconclusive.

### ASSUMPTION UPDATE: Tenaska Virginia and Ladysmith retained past formula retirement (for Scenario 1/3/1B/3B/3C shortfall purposes)

Tested directly against Scenario 1's 2035 checkpoint shortfall and found
substantially cheaper than new-build (see `new_peaker_ccgt_costs_by_size.md`
for full detail and caveats). **This is an assumption, not a confirmed
plan** -- Tenaska Virginia's overhaul cost is a midpoint estimate, not a
plant-specific quote; Ladysmith's "no capital work needed" conclusion is
inferred from its low EOH, not a confirmed engineering assessment; and
Tenaska Virginia's third-party (Tenaska) ownership means retention would
require a negotiated agreement, not just a Dominion capital decision.

**Effect on the schedules below**: Tenaska Virginia (975 MW) and Ladysmith
(782 MW) are now assumed RETAINED past their formula-retirement dates
(2034 and 2031 respectively) for the specific purpose of addressing
identified capacity shortfalls in Scenario 1/3/1B/3B/3C -- NOT
automatically extended to their full physical life indefinitely. This
assumption should be re-examined if a shortfall large enough to require
their retention doesn't actually arise at a given checkpoint, or if a
shortfall at a LATER checkpoint would need them retained even longer than
currently assumed.

### Chesterfield's EOH, now correctly computed (gas-only data)

Coal Units 5&6 retired May 31, 2023 -- data from June 2023 onward is
confirmed gas-only (Units 7&8 only). Over this clean 36-month window
(Jun 2023-May 2026): **16,487 EOH**, at a 62.7% average capacity factor,
against the corrected 386 MW gas-only capacity.

Extrapolating this rate backward (implied ~5,496 EOH/year) suggests a
full-history cumulative EOH somewhere in the range of 137,000-198,000
depending on the assumed start year (2001 data-window limit vs. 1990 true
commissioning) -- both figures place Chesterfield well above the
48,000-100,000 mid-life window, consistent with the earlier (invalid)
calculation's conclusion even though the specific number has changed.
**This extrapolation should be treated as directional, not precise**: it
assumes the gas units' utilization rate has been roughly constant
throughout their history, which is unlikely -- Units 7&8 plausibly ran
less while the coal units still provided most of the site's baseload,
then increased utilization after coal retired to help compensate for the
lost capacity. The true historical average could be meaningfully lower
than 62.7%.

### Independent verification of the "seven plants, Dec 2024" pattern: INCONCLUSIVE

A working search for direct news/regulatory confirmation of retirement
for Gordonsville, Gravel Neck, Darbytown, Elizabeth River, Remington,
Marsh Run, and Louisa did NOT find clear confirmation. What it did find:
third-party databases (gridinfo.com, Global Energy Monitor) that draw on
the same underlying EIA data and share the identical Dec 2024 cutoff --
not independent confirmation. Global Energy Monitor's own Gordonsville
page (updated January 2026) still lists the plant's status as
"operating... with multiple units, some of which are not currently
operating" -- ambiguous, but does not say retired.

**Revised characterization**: these seven plants show generation data at
zero since Dec 2024, with the underlying cause UNCONFIRMED -- could be
retirement, reserve/standby status, or a data-reporting gap specific to
smaller plants (all seven larger CCGT-style plants continue reporting
cleanly through May 2026, which argues against a uniform reporting lag,
but does not rule out a lag specific to this plant class). Treated
CONSERVATIVELY as unavailable capacity in the schedule below (same
practical effect as retirement for our purposes), but this is now
explicitly flagged as an assumption under genuine uncertainty, not a
confirmed fact.

### CERC approval status, corrected again

Per Virginia Mercury (most recent, most direct source found): the SCC
approved CERC in November 2025; advocacy groups petitioned for
reconsideration (this appears to be the source of the earlier "suspended"
report); the SCC **declined to reconsider, reasserting its original
approval**. Advocacy groups are now pursuing a separate air-permit appeal.
**Current status: approved**, though still facing an ongoing legal
challenge on a different track. Also note: this more recent source cites
944 MW (not 1,000 MW) and states the plant is expected to run "about 33%
of the time." Still excluded from the capacity schedules below, since
commercial operation (~2029) falls partway through our analysis window
and hasn't been incorporated as a time-varying addition yet.

### Data collection status: COMPLETE

All 10 peaker/mixed-type plants now have direct generation-data
confirmation (Wolf Hills was the last, uploaded and processed most
recently). 8 of these 10 plants show the identical "zero output since
Dec 2024" pattern (cause unconfirmed, see note above) -- only Ladysmith
and Possum Point continue reporting cleanly through May 2026.

### Schedule A: Physical/data-driven retirement (for Scenario 3C specifically)

| Year | Total capacity (MW) | Notes |
|---|---|---|
| 2026-2040 | 9,362 | All confirmed/presumed-operating plants; Tenaska Virginia and Ladysmith now assumed RETAINED (see assumption note above) rather than retiring on their formula dates (2034, 2031) |
| 2041-2043 | 8,740 | Bear Garden retires (2041) |
| 2044-2045 | 7,391 | Warren County retires (2044) |

### Schedule B: VCEA-driven retirement (for Scenario 1/3's own 2045 checkpoint context)

| Year | Total capacity (MW), VCEA-consistent world | Notes |
|---|---|---|
| 2026-2044 | Same as Schedule A | VCEA doesn't bind until the 100% terminal year itself |
| 2045 | 1,860 (Chesterfield + Doswell + Possum Point) | Brunswick County + Potomac Energy Center + Greensville (3,774 MW combined) retire for lack of market |

### Important caveats

- 30-year CCGT / 30-45yr CT lifespan assumptions are user-selected
  starting points, not engineering certainties
- Chesterfield's full-history EOH is an extrapolation from a confirmed
  36-month gas-only window, not a direct historical measurement -- treat
  as directional (well above the mid-life window) rather than precise
- The "seven plants, zero output since Dec 2024" finding is NOW EXPLICITLY
  UNCONFIRMED as to cause -- treated conservatively (excluded from
  capacity) but should not be cited elsewhere as "confirmed retired"
- CERC's approval status has been revised twice in this project (approved
  -> reported as suspended -> reasserted as approved) -- worth a final
  re-check before this is used in any downstream calculation, given the
  history of this specific status changing
- Wolf Hills has no generation data uploaded -- still relies on the
  30-year formula alone
- Marsh Run, Louisa (ODEC-owned), Potomac Energy Center (Blackstone-owned),
  Wolf Hills (Middle River Power II-owned), and Doswell (LS Power
  Group-owned) are included per the physical-grid-contribution principle
  where still applicable

---

# 5. Operating constraints

## Ramp constraints — added, and what is deliberately left out

**Added 2026-09-13.** Source: **arXiv 2311.04398 Table D.1** (NREL Annual Technology Baseline 2020
basis). Class-level parameters, which is standard practice — PLEXOS, GridView and PROMOD all use
technology-class defaults rather than per-unit specifications.

| technology | min stable output | **hourly ramp** | min up/down | startup fuel |
|---|---:|---:|---:|---:|
| OCGT | 30% | **100%** | 1 / 1 h | 350 MMBtu |
| CCGT | 20% | **64%** | 6 / 6 h | 1,000 MMBtu |

**Why it matters.** The LP sees only *marginal* cost, so without a ramp limit it uses
`ccgt_modern` ($47.32/MWh at 2045) for a one-hour evening spike as readily as for baseload, in
preference to `ct_fleet` ($81.17). Wrong twice over: a combined-cycle unit cannot start fast
enough, and running one at a 2% capacity factor is uneconomic on capital grounds the dispatch
objective never sees.

**Implementation.** `|rung[t] − rung[t−1]| ≤ limit`, two inequality rows per hour per binding rung.
Only the four CCGT rungs get rows — OCGT at 100%/hour can never bind at hourly resolution, and
adding 17,520 rows for it would cost solve time for no behavioural change.

**Measured at 2030: all four constrained rungs bind exactly at their limits.**

| rung | limit MW/h | observed max swing |
|---|---:|---:|
| `new_build_ccgt` | 1,685.1 | 1,685.1 |
| `ccgt_modern` | 3,012.9 | 3,012.9 |
| `ccgt_fleet` | 1,258.4 | 1,258.4 |
| `ccgt_legacy` | 768.7 | 768.7 |

Objective moved **+0.02%**, solve time **33.8 s → 41.2 s**.

**An honest note on effect size:** at 2030, CT usage barely moved (112,066 → 111,308 MWh). The
constraint binds, but it did not shift work toward CTs at this compliance level — because with 59%
gas allowed, gas runs steadily rather than spikily. The CCGT/CT substitution should matter more at
higher compliance levels, where gas is marginal and peaky. That is a prediction, not a measurement.

### What is NOT modelled, and which way it biases

**Minimum up/down times and start costs require binary commitment variables** — 43,800 of them at
five rungs × 8,760 hours. That is unit commitment, a MILP, and `scipy.optimize.linprog` cannot do
it at all (SciPy's `milp()` exists but means a second solve path).

**The omission flatters CCGT.** Without minimum run times the LP can start a combined-cycle unit
for a single hour and shut it down — physically impossible and uneconomic. Since CCGT is *also* the
cheapest gas on marginal cost, it gets selected for peaking duty a CT should serve. Ramp
constraints remove the worst of this; they do not remove all of it.

**Scoped as a separate deliverable**, to be run *after* the LP sweep so the difference unit
commitment makes is measurable rather than assumed. A rung is not one turbine — `ccgt_modern` is
12 units across three plants — so integer commitment of a whole rung would itself be an
approximation, and that needs deciding deliberately rather than at solve time.

### Availability — flat, by decision

`GAS_AVAILABILITY_FACTOR = 0.92`, applied uniformly. **Scheduled maintenance was considered and
rejected on evidence:** in a high-solar system the low-gas windows are the shoulder seasons, and
**the nuclear profile already dips there** — September 2,989 MW, October 2,946, March 3,008 against
a February peak of 3,695, a refuelling-shaped ~750 MW trough. Concentrating gas maintenance into the
same months would compound with nuclear refuelling.

### Retirements flow through per plant

Capacity sums from a **per-plant** table because retirements hit different rungs at different times:
**Bear Garden (`ccgt_fleet`) 2041**, **Warren County (`ccgt_modern`) 2044**. The stack *shape*
matters more than the total.

**Schedule B resolved 2026-09-12.** It is not inconsistent — it is **DOM-zone gas at net summer
capability**, and its own text (line 130) names Doswell, Potomac Energy Center, Marsh Run, Louisa
and Wolf Hills as non-Dominion. The retiring set reconciles at net summer (3,781 vs 3,774 claimed),
not nameplate (4,057.5). The earlier "discrepancy" was a scope-and-basis mismatch on this project's
side, now removed by expanding scope to DOM-zone and naming all three bases.

## Cost structure

`gas_cost_mwh(year, heat_rate)` — fuel only, Deloitte/MEDIUM gas price trajectory, piecewise-linear
interpolation. `gas_cost_mwh_eia(year)` is an alternative trajectory sharing the 2026 starting
point ($3.70/MMBtu); a HIGH case also exists.

`CCGT_VOM_MWH = 3.0`. **No separate CT VOM constant exists** — CT VOM is typically higher than
CCGT (more starts, more cycling wear), so using 3.0 for peakers understates their marginal cost on
top of the heat-rate optimism noted above.

`heat_rate` is a **required** argument with no default, corrected 2026-08-16 after a bug in which
it silently defaulted.

---

## Retirement schedules — see section 4 below

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

## What sits above the merit order — unresolved

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

## Why this matters: the flat dual

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

---

# 6. New-build capex by size tier

Compiled for scoping potential new turbine purchases if Schedule A/B's
existing-fleet capacity proves insufficient to meet gas dispatch needs in
Scenario 1/3/1B/3B/3C. Organized by size tier so specific figures can be
mixed and matched to whatever shortfall size is identified.

### LEADING ASSUMPTION for addressing identified shortfalls (overhaul/retain, not new-build)

**Before defaulting to new construction, first check whether any plant
already scheduled to retire before the shortfall year can instead be
overhauled or simply retained past its formula-predicted retirement.**
This was tested directly against Scenario 1's 2035 shortfall (~1,720-1,777
MW) and found substantially cheaper than new-build:

| Path | PV, full 2026-2045 window |
|---|---|
| No action (over-comply via extra solar/storage) | $92,742.7M |
| New-build (~1,777 MW simple-cycle, per the standing rule below) | $89,525.9M |
| **Overhaul/retain existing near-EOL plants** | **$88,048.8M** |

**Specific finding for the 2035 case**: Tenaska Virginia (975 MW, formula
retirement 2034) and Ladysmith (782 MW, formula retirement 2031) --
combined 1,757 MW, closely matching the shortfall -- retained instead of
retired on schedule:
- Tenaska Virginia: within its own mid-life overhaul window (EOH=87,028,
  in the 48,000-100,000 range) -- genuine overhaul candidate, estimated
  ~$22.5M (midpoint of the \$15-30M CCGT comprehensive-overhaul range)
- Ladysmith: EOH=16,718, well BELOW typical overhaul thresholds --
  working assumption is this plant needs NO capital work at all to keep
  running past 2031; its formula retirement is likely simply premature
  given how lightly it has actually been used, not a scheduled
  overhaul-or-retire decision point
- Combined capital cost: ~$22.5M (vs. $1,936.3M for equivalent new-build
  capacity) -- even recovered over the same accelerated 10-year stranded
  basis, the annual fixed-cost burden ($2.84M/year) is trivial compared
  to new-build ($268.3M/year)

**THIS IS AN ASSUMPTION, explicitly flagged as such, not a confirmed
plan**:
- The $22.5M Tenaska Virginia overhaul cost is a midpoint estimate, not a
  plant-specific quote -- real cost depends on turbine model and actual
  scope of work needed
- Ladysmith's "no capital work needed" conclusion is an inference from
  its low EOH figure, not a confirmed engineering assessment
- Tenaska Virginia is THIRD-PARTY OWNED (Tenaska, not Dominion) --
  retaining it past its expected retirement would require a negotiated
  agreement with its owner, a real practical complication the cost math
  alone doesn't capture
- This specific pairing (Tenaska Virginia + Ladysmith) was identified for
  the 2035 shortfall specifically -- if shortfalls are found at other
  checkpoints in other scenarios, the same overhaul-first check should be
  applied there too, using whichever plants happen to be near their own
  formula-retirement dates at that point, not assumed to be this same pair

**Practical rule going forward**: when a checkpoint re-solve reveals a
capacity shortfall, first check Schedule A/B for any plant with a
formula-retirement date at or before that checkpoint year. If retaining
it (with or without an overhaul, depending on its own EOH position)
covers all or part of the shortfall, prefer that path and use new-build
(below) only for whatever capacity gap remains.

### STANDING RULE for new-build, when overhaul/retain isn't sufficient (user decision)

For Scenario 1, 1B, 3, 3B, and 3C specifically (NOT Scenario 2, which
retains its own established CCGT-based new-build methodology): any new
gas capacity needed to fill a shortfall against Schedule A/B, beyond what
overhaul/retention of near-EOL plants can cover, is modeled as
SIMPLE-CYCLE COMBUSTION TURBINES ONLY, using one or a combination of
these three specific units:

| Unit | Rated capacity | Total cost | $/kW | Fixed O&M |
|---|---|---|---|---|
| Aeroderivative | 105 MW (rounds to 100 MW) | $123.5M | $1,175/kW | $16.30/kW-yr |
| F-Class | 237 MW (rounds to 250 MW) | $165.8M | $713/kW | $7.00/kW-yr |
| H-Class | 418 MW (rounds to 430 MW) | $453.2M | $1,084/kW | $13.10/kW-yr |

**Rationale**: existing CCGT capacity is already substantial across these
scenarios; most anticipated shortfalls are likely short-duration (a few
hours at a time) gap-filling needs, exactly the duty profile simple-cycle
peakers are designed for. Heavy cycling (frequent starts/stops) sharply
shortens CCGT lifespan specifically (see
`Gas_turbine_lifespans_reference.md`) -- using CCGT to fill small,
intermittent gaps would reproduce the same wear pattern this project has
spent considerable effort identifying and correcting for in the existing
fleet. Simple-cycle units are the physically and economically appropriate
choice for this role.

These three units can be combined as needed to approximate whatever
specific shortfall size a checkpoint re-solve reveals (e.g., one F-Class
unit for a ~240 MW gap; an Aeroderivative + F-Class pairing for a gap in
the 300-350 MW range).

### Important context: costs have risen sharply and recently

Per GridLab's September 2025 market survey (the most rigorous, recent
source found): combustion turbine (simple-cycle) costs for plants placed
in service in 2023 averaged **$562/kW**; by 2025, costs range
**$728-$1,544/kW** — roughly a 2-3x increase in just two years. CCGT
costs show the same pattern: plants completing 2026-2027 were reported at
$1,116-$1,427/kW, while the most recent CCGT projects are "routinely
reporting costs of $2,000/kW." **Any cost figure used in modeling should
be treated as reflecting this elevated, still-rising market, not
historical averages** — a project quoted at pre-2023 prices would
meaningfully understate current cost.

### Small tier (20-50 MW) — fast-deployment, aeroderivative

- **GE TM2500 mobile aeroderivative** (30 MW package): $950-1,250/kW EPC,
  commissioned in 120-180 days from deposit. Designed for fast-track
  captive/bridge power. (USP&E Global, 2026)
- **General small-project range (25-50 MW)**: $1,400-2,000/kW — smaller
  projects carry a real cost-per-kW premium versus larger ones due to
  reduced economies of scale. (USP&E Global, 2026)
- Illustrative project cost at 30 MW, midpoint ~$1,100/kW: **~$33M**

### Medium tier (100-250 MW) — the classic "single new peaker" scale

- **Aeroderivative 100 MW simple-cycle genset**: twin gas turbine unit
  rated 105 MW, 41.5% efficiency, **$123.5M total ($1,175/kW installed)**,
  $16.30/kW fixed O&M. (Gas Turbine World 2024 Handbook)
- **F-Class 240 MW simple-cycle genset**: single F-Class unit rated
  237 MW, 38.2% efficiency, **$165.8M total ($713/kW installed)**,
  $7.00/kW fixed O&M. (Gas Turbine World 2024 Handbook)
- Note the efficiency-of-scale effect here: the larger 237 MW unit has a
  LOWER per-kW cost ($713) than the smaller 105 MW unit ($1,175), despite
  being a newer technology class -- consistent with the broader "size
  matters" pattern found elsewhere in this research

### Large tier (400-600 MW) — combined-cycle territory

- **H-Class 430 MW single-shaft combined cycle**: rated 418 MW, 58.9%
  efficiency, **$453.2M total ($1,084/kW installed)**, $13.10/kW fixed
  O&M. (Gas Turbine World 2024 Handbook)
- **600 MW combined-cycle plant** (generic mid-range scenario): HRSGs,
  advanced turbines, moderate interconnection work. **$700-900M total
  ($1,170-1,500/kW)**. (LatestCost, 2026)
- **550 MW combined-cycle** (generic build-cost estimate): **$1.8M/MW,
  ~$990M total** — notably higher per-kW than the ranges above, likely
  reflecting the most recent, elevated 2026 cost environment described
  above. (Design Transition Studio, 2026)

### Very large tier (1,000+ MW)

- **H-Class 1,100 MW multi-shaft combined cycle**: rated 1,083 MW, 59.4%
  efficiency, **$958M total ($950/kW installed)**, $12.20/kW fixed O&M.
  (Gas Turbine World 2024 Handbook)
- **1,000+ MW ultra-efficient CCGT** (premium scenario): high-grade
  turbines, low-emission systems, complex site work. **$1.2-1.6B total
  ($1,200-1,600/kW)**. (LatestCost, 2026)
- For direct comparison: this project's own established figure for CCGT
  is **$2,400/kW** (used throughout Scenario 2's CCGT sizing) --
  meaningfully higher than most figures in this table, consistent with
  reflecting the most current, elevated market rather than 2023-2024
  price levels.

### Simple-cycle (300 MW) — filling the gap between medium and large

- **300 MW simple-cycle plant** (basic scenario): standard emissions
  controls, standard interconnection. **$310-360M total
  ($1,033-1,200/kW)**. (LatestCost, 2026)

### General O&M reference (across sizes)

Typical ongoing O&M for an installed gas plant: **$25-50/kW-year**, plus
fuel — broadly consistent with (though somewhat higher than) the specific
fixed-O&M figures listed per genset above.

### Quick-reference summary table

| Size | Technology | Total cost | $/kW | Source |
|---|---|---|---|---|
| 30 MW | Aeroderivative, mobile | ~$33M (est.) | $950-1,250 | USP&E, 2026 |
| 105 MW | Aeroderivative, simple-cycle | $123.5M | $1,175 | Gas Turbine World |
| 237 MW | F-Class, simple-cycle | $165.8M | $713 | Gas Turbine World |
| 300 MW | Simple-cycle | $310-360M | $1,033-1,200 | LatestCost |
| 418 MW | H-Class, combined-cycle | $453.2M | $1,084 | Gas Turbine World |
| 550 MW | Combined-cycle | ~$990M | $1,800 | Design Transition Studio |
| 600 MW | Combined-cycle | $700-900M | $1,170-1,500 | LatestCost |
| 1,083 MW | H-Class, combined-cycle | $958M | $950 | Gas Turbine World |
| 1,000+ MW | Premium CCGT | $1.2-1.6B | $1,200-1,600 | LatestCost |

### Caveats

- Costs vary regionally by roughly ±15-30% versus national benchmarks;
  Virginia-specific figures were not separately sourced here
- "Prime mover" equipment typically represents only 30-50% of total
  installed cost — balance of plant (transformers, switchgear,
  interconnection, fuel infrastructure, civil works) accounts for the
  rest; buyers benchmarking on equipment price alone can underestimate
  installed cost by 40-80%
- Given the sharp, recent cost escalation noted above, figures toward the
  higher end of each range (or this project's own $2,400/kW CCGT figure)
  are likely more representative of actual, current procurement
  conditions than the lower ends of these ranges
- These are overnight capital costs (excluding financing/inflation during
  construction) — actual project costs including financing would be
  higher

---

# 6A. Lifecycle costing — capital on new build only

**Added 2026-09-13**, `lp_package/gas_lifecycle_cost.py`.

## The problem it fixes

Scenario 2 — the whitepaper's baseline — dispatched gas against a ceiling high enough never to
bind, and carried **fuel and VOM only, no capital at all**. Its 22,478 MW peak at 2045 appeared for
free.

That flatters the baseline, in the direction a reviewer will attack. **But the naive correction is
wrong the other way:** charging capital on all 22,478 MW would bill Dominion for plant that already
exists and is already paid for.

| | charged |
|---|---|
| **existing fleet** | FOM + fuel + VOM — capital is **sunk** |
| **new build** | capex + FOM + fuel + VOM — capital is **incurred** |

## Scenario 2 at 2045

| | MW |
|---|---:|
| peak gas | 22,478 |
| existing fleet available *(net summer × 0.92, post-retirement)* | **12,216** |
| **new gas implied** | **10,262** |

**Dominion's statutory build implies roughly 10 GW of new gas**, which the scenario's cost did not
previously show at all.

| capex case | capital | annual gas cost | capital share |
|---|---:|---:|---:|
| low ($2,000/kW) | $20.5B | $7.60B | 18.2% |
| **central ($2,500/kW)** | **$25.7B** | **$7.94B** | **21.8%** |
| high ($3,200/kW) | $32.8B | $8.43B | 26.3% |

**Capital is a fifth to a quarter of the annual gas bill** — large enough that omitting it
materially understated the baseline.

## CCGT capex: a band, not a number

**$2,500/kW central**, with $2,000 low and $3,200 high.

A single point figure is not defensible here. §6 below records simple-cycle plant entering service
in 2023 averaging **$562/kW** against 2025 costs of **$728–1,544/kW** — a 2–3× move in two years —
and notes recent CCGT projects *"routinely reporting costs of $2,000/kW"* against an earlier
$1,116–1,427/kW range.

**What a reviewer will ask is not "why $2,500" but "why one number in a market that moved 3× in two
years."** The band is the answer. The prior constant was $3,000/kW, above even the recent
"routinely $2,000" reports.

## The CCGT/CT crossover

The capacity factor at which the two have equal total cost per MWh. **Above it build CCGT** — lower
fuel repays higher capital. **Below it build CT.**

| both bases | crossover CF |
|---|---:|
| low | **23.7%** |
| **central** | **28.1%** |
| high | **33.2%** |

**Bases must match.** Pairing CCGT *high* with CT *low* gives **51.0%**; the reverse gives **5.9%**.
A crossover quoted without stating both bases is uninterpretable, which is why both are explicit
arguments.

*This corrects an earlier estimate of 41%, which used $3,000/kW CCGT against a guessed $1,200/kW CT
and omitted FOM entirely.*

**Scenario 2's fleet-average CF is 62.4%** — comfortably above even the high-case crossover, so
CCGT is right *on average* for its gas. That says nothing about the **marginal** units serving
evening peaks, which run far below the average and would be better served by CT. **An average
cannot answer a marginal question**, which is why the LP must eventually make the choice
endogenously.

## Why post-solve rather than in the LP

`build_scenario2_problem` has **one gas variable and one gas price** — no merit order, so no
existing/new distinction is available inside it. Wiring the merit order into that function is a
model change; computing the increment from the reported peak is an accounting layer that gets the
baseline's SLCOE right today without touching dispatch.

**What it cannot do** is split the new build between CCGT and CT. That is a capital-versus-fuel
trade the LP must make endogenously, and it is the reason to eventually wire the merit order in.

---

# 7. Lifespans, EOH and overhaul

## Contents {#contents .TOC-Heading}

[Gas turbine lifespans
[1](#gas-turbine-lifespans)](#gas-turbine-lifespans)

[CCGT [1](#ccgt)](#ccgt)

[Combustion Turbines [3](#combustion-turbines)](#combustion-turbines)

### CCGT

Estimated useful lifespans for Combined Cycle Gas Turbine (CCGT) plants
built in the US since 2000 typically range from **25 to 30 years** of
nominal design life. However, with major overhauls and retrofits,
physical and technical lifespans often stretch to **40 or 45 years**.
\[[1](https://www.epri.com/research/products/000000003002016837),
[2](https://rmi.org/resources/you-might-be-paying-for-a-worthless-gas-plant/)\]

**Design vs. Extended Lifespans**

-   **Nominal Design Life:** Generally 25 to 30 years for base
    components like gas turbines, heat recovery steam generators (HRSG),
    and steam turbines. \[,
    [2](https://rmi.org/resources/you-might-be-paying-for-a-worthless-gas-plant/)\]

-   **Extended Operational Life:** Can reach 40 to 45 years if asset
    owners perform thorough mid-life evaluations, major component
    replacements, and operational upgrades.
    \[[1](https://www.eia.gov/todayinenergy/detail.php?id=65464),
    [2](https://www.epri.com/research/products/000000003002016837)\]

**Factors Influencing CCGT Lifespans Post-2000**

-   **Cycling and Duty Ramps:** Plants built after 2000 (especially the
    massive wave of F-class turbines installed early in the decade) face
    varying grid demands. Frequent starting, stopping, and ramping to
    balance intermittent renewables accelerate wear on critical
    hot-gas-path components.
    \[[1](https://alliedpg.com/latest-articles/aging-infrastructure-impacts-turbine-reliability/),
    [2](https://www.eia.gov/todayinenergy/detail.php?id=60984),
    [3](https://naturalgasintel.com/news/technology-low-prices-boosting-us-natural-gas-fired-power-plant-efficiency/),
    [4](https://www.dallasfed.org/research/economics/2023/1017),
    [5](https://www.sciencedirect.com/science/article/pii/S1876610218310348/pdf?md5=cfc022c3040962d4b8f89354b2af4753&pid=1-s2.0-S1876610218310348-main.pdf)\]

-   **Maintenance Regimes:** Timely replacement of turbine blades,
    combustors, and rotor refurbishments determine whether a plant
    retires at year 25 or pushes past year 40.
    \[[1](https://www.eia.gov/todayinenergy/detail.php?id=65464),
    [2](https://www.epri.com/research/products/000000003002016837)\]

-   **Economic and Policy Pressures:** Even if a plant remains
    mechanically viable, changing environmental regulations, corporate
    net-zero targets, and competition from cheaper renewable
    alternatives can render older CCGT units economically obsolete
    before their physical life ends.
    \[[1](https://rmi.org/resources/you-might-be-paying-for-a-worthless-gas-plant/)\]

Common mid-life upgrade requirements for F-class gas turbines (such as
the GE 7F series or Siemens SGT6-5000F) focus on reversing component
degradation, adapting to modern grid stress, and expanding efficiency.
These comprehensive upgrades generally occur around **48,000 to 100,000
Equivalent Operating Hours (EOH)**.
\[[1](https://oxmaint.com/industries/power-plant/gas-turbine-maintenance-combined-cycle-guide),
[2](https://www.caiso.com/documents/nexantpresentation-variableoperations-maintenancecostreview-jan8-2018.pdf),
[3](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/),
[4](https://www.psm.com/products),
[5](https://oxmaint.com/industries/power-plant/gas-turbine-maintenance-cmms-software-hot-section-inspection-guide)\]

The primary technical requirements and their associated costs are broken
down below:

**Common Mid-Life Upgrade Requirements**

-   **Rotor Life Extension (RLE) or Replacement:** Legacy F-class rotors
    have strict operational limits due to low-cycle fatigue and thermal
    stress. Upgrades include full rotor disassembly, non-destructive
    ultrasonic testing, or replacing the rotor with high-strength
    alloys.
    \[[1](https://oxmaint.com/industries/power-plant/gas-turbine-maintenance-combined-cycle-guide),
    [2](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/)\]

-   **Advanced Gas Path (AGP) Retrofits:** Replacing standard turbine
    buckets (blades), nozzles, and shrouds with components made of
    advanced superalloys and thermal barrier coatings. This allows the
    turbine to handle higher firing temperatures for increased output.
    \[[1](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/),
    [2](https://alliedpg.com/frames/ge-frame-7f/),
    [3](https://www.psm.com/products),
    [4](https://kianturbotec.com/solar-mars-gas-turbine-upgrades/)\]

-   **Combustor Modernization:** Upgrading legacy systems to modern Dry
    Low NOx (DLN) platforms (like the DLN 2.6+). This expands
    operational turndown capability down to \~25% of baseload and
    prepares the plant for hydrogen co-firing blends.
    \[[1](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/)\]

-   **Compressor and Actuation Redesigns:** Replacing older hydraulic
    variable guide vane mechanisms with electric actuation systems to
    eliminate oil leak points and accelerate grid ramping speeds.
    \[[1](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/)\]

-   **Turbine Control Panel (TCP) Upgrades:** Replacing obsolete
    physical control hardware and migrating to modern digital software
    frameworks (e.g., Mark VIe systems) to improve diagnostics.
    \[[1](https://www.ccj-online.com/while-new-capacity-waits-in-line-7f-upgrades-deliver-flexibility-and-output-now/),
    [2](https://www.powermag.com/comparing-gas-turbine-life-to-turbine-control-life-what-you-need-to-know/)\]

**Mid-Life Upgrade and Overhaul Cost Breakdown**

According to power plant asset data compiled by
[OxMaint](https://oxmaint.com/industries/power-plant/gas-turbine-major-overhaul-planning-execution-guide)
and industrial tracking from
[SecondWatt](https://secondwatt.com/equipment/gas-turbines), the
financial layout varies based on the level of optimization required:

  -------------------------------------------------------------------------
  **Upgrade/Maintenance    **Estimated Cost **Key Components Included**
  Category**               Range (Per       
                           Unit)**          
  ------------------------ ---------------- -------------------------------
  **Turbine Control Panel  **\$1,000,000 -- Modern control panels, updated
  (TCP) Upgrade**          \$1,500,000**    digital diagnostic software,
                                            and BOP integration.

  **Standard Tier 3 Major  **\$4,000,000 -- Flange-to-flange inspection,
  Overhaul**               \$10,000,000**   bearing replacements, and
                                            standard blade refurbishments.

  **Advanced Gas Path      **\$5,000,000 -- Full replacement set of
  (AGP) hardware kit**     \$15,000,000**   specialized premium superalloy
                                            hot-section buckets and
                                            nozzles.

  **Comprehensive          **\$15,000,000   Total asset overhaul combining
  Flange-to-Flange Frame   --               core rotor replacement,
  Upgrade**                \$30,000,000**   compressor staging, AGP kit,
                                            and digital controls.
  -------------------------------------------------------------------------

*Note: For mid-life power plants, executing these comprehensive
component upgrades is estimated to be **40% more cost-effective** than
full plant decommissioning and new turbine installations.*
\[[1](https://www.intelmarketresearch.com/remanufactured-gas-turbine-market-30317)\]

### Combustion Turbines

Estimated useful lifespans for combustion turbine (CT) peaker plants
built in the US since 2000 range from **30 to 45 years**. Because
peakers run infrequently but experience high thermal stress from rapid
starts, their lifespans are measured differently than baseload plants.

The structural and economic lifespan breakdown for post-2000 US peaker
assets includes the following key factors:

**Operating Profiles and Lifespan Metrics**

-   **Hours vs. Starts:** Baseload plants measure life in operating
    hours, but peakers measure life in **starts and thermal cycles**.

-   **Physical Longevity:** The actual physical machinery can easily
    last **45+ years** because low run-times (typically a 2% to 10%
    capacity factor) limit mechanical wear.

The cost to overhaul or extend the life of a combustion turbine peaker
plant varies significantly by machine type. Because peakers experience
intense thermal stress from cyclic starting, maintenance is dictated by
**start counts rather than total operating hours**.
\[[1](https://www.greengasturbines.com/blog/aeroderivative-vs-heavy-duty-gts-start-times-ramp-rates-use-cases),
[2](https://alliedpg.com/latest-articles/when-and-why-to-overhaul-a-turbine/)\]

Asset owners face a critical decision framework: invest in standard
hot-section overhauls (**\$3M to \$7M**) or complete
engine/flange-to-flange replacements (**\$10M to \$25M**).
\[[1](https://www.gevernova.com/gas-power/services/gas-turbines/aeroderivative/repair-maintenance)\]

The capital costs, strategies, and technical options for extending
peaker asset longevity are detailed below:

**1. Cost Breakdown by Peaker Technology**

The market split is between high-performance aero-derivative turbines
(repurposed jet engines) and heavy-duty frame machines.
\[[1](https://www.greengasturbines.com/blog/aeroderivative-vs-heavy-duty-gts-start-times-ramp-rates-use-cases)\]

**Aero-derivative Peakers *(e.g., GE LM6000 series, Pratt & Whitney
FT8)***

Aero-derivative units are optimized for rapid, sub-10-minute grid
starts. Instead of on-site rebuilding, they rely on a
**\"swap-and-ship\" maintenance model** where the engine core is removed
and sent to a specialized depot.
\[[1](https://www.gevernova.com/gas-power/services/gas-turbines/aeroderivative/repair-maintenance),
[2](https://www.greengasturbines.com/blog/aeroderivative-vs-heavy-duty-gts-start-times-ramp-rates-use-cases)\]

-   **Standard Hot-Section Overhaul (Every 250--500 starts):**
    **\$3,000,000 -- \$5,500,000**. This involves replacing the
    combustor liner, high-pressure turbine blades, and primary nozzles.
    \[[1](https://www.reddit.com/r/aviationmaintenance/comments/1ofc55b/so_any_thoughts_on_cross_training/)\]

-   **Full Flange-to-Flange Engine Replacement:** **\$10,000,000 --
    \$15,000,000**. Replacing the entire engine block resets the asset
    to zero hours/starts and can boost output up to 60 MW with modern
    fuel efficiencies.
    \[[1](https://www.sgenergysolutions.com/blog/the-cost-of-replacing-a-gas-turbine-in-power-plants-what-you-need-to-know/),
    [2](https://www.gevernova.com/gas-power/services/gas-turbines/upgrades/lm6000-flange-to-flange-replacement)\]

**Heavy-Duty Frame Peakers *(e.g., GE 7E, Siemens SGT6-5000F)***

Frame units are large, heavy industrial turbines. Maintenance must be
conducted entirely on-site, effectively turning the plant into a
temporary construction zone.
\[[1](https://www.greengasturbines.com/blog/aeroderivative-vs-heavy-duty-gts-start-times-ramp-rates-use-cases)\]

-   **Major Inspect & Overhaul (Every 900--1,200 starts):**
    **\$6,000,000 -- \$12,000,000**. Includes full casing disassembly,
    non-destructive rotor inspection, and a completely fresh set of
    advanced hot-gas path components.
    \[[1](https://www.sgenergysolutions.com/blog/the-cost-of-replacing-a-gas-turbine-in-power-plants-what-you-need-to-know/)\]

-   **Rotor Life Extension (RLE):** **\$4,000,000 -- \$8,000,000**.
    Because rapid starting warps thick steel rotors due to uneven
    thermal expansion, frame rotors must undergo ultra-precise localized
    machining or individual disc replacements to extend life past 30
    years.

**2. Critical Balancing Costs & Capital Upgrades**

Extending a peaker\'s life requires upgrading the balance of the plant
to meet evolving grid requirements:
\[[1](https://uspeglobal.com/articles/power-plant-cost-per-mw-2026-epc-guide/),
[2](https://www.sandia.gov/app/uploads/sites/163/2022/04/Issue-Brief-2020-11-Peaker-Plants.pdf)\]

-   **Emissions Reduction Systems (SCR/CO Catalysts):** **\$2,000,000 --
    \$5,000,000**. Older peakers face intense regulatory scrutiny over
    startup emissions. Retrofitting Selective Catalytic Reduction (SCR)
    units allows the plant to stay legally compliant with strict
    regional air rules.

-   **Fast-Start / Ramping Upgrades:** **\$1,000,000 -- \$2,500,000**.
    Upgrading to electronic fuel valves, high-capacity starting motors,
    and purged lubrication systems allows heavy-duty frames to decrease
    their startup times from 30 minutes down to 10--15 minutes,
    preserving market relevance.

-   **Control System Modernization:** **\$800,000 -- \$1,500,000**.
    Migrating outdated analog architectures to advanced digital control
    systems allows operators to monitor cyclic fatigue remotely and
    integrate seamlessly with regional transmission networks.
    \[[1](https://stanwichenergy.com/insights/the-peaker-rule-shaping-current-and-future-capacity-costs-in-new-york)\]

**3. Life Extension vs. Replacement Cost Framework**

Due to a massive global supply crunch in hot-section manufacturing, raw
gas turbine components have spiked significantly. This shift alters the
standard asset management strategy:
\[[1](https://www.utilitydive.com/news/gas-turbine-supply-crunch-set-to-raise-prices-195-by-2027-woodmac/816904/)\]

  -------------------------------------------------------------------------
  **Metric**    **Life Extension /    **Building a New  **Standalone 4-Hour
                Overhaul**            Peaker Plant**    Battery (BESS)**
  ------------- --------------------- ----------------- -------------------
  **Capital     **\$5M -- \$20M       **\$1,200 --      **\$500 -- \$690
  Cost**        total**               \$1,800 per kW**  per kWh**

  **Project     **\$5M -- \$20M**     **\$60M --        **\$100M --
  Example                             \$90M**           \$138M**
  (50MW)**                                              

  **Time to     **1 -- 3 months**     **3 -- 5 years**  **1 -- 2 years**
  Complete**                                            

  **Key         Avoids expensive grid Maximum           Zero localized
  Advantage**   interconnection       efficiency and    emissions; instant
                queues.               full OEM          grid response.
                                      warranty.         
  -------------------------------------------------------------------------

*Strategic Note: Because existing peakers already possess valuable
utility grid interconnections and physical land assets, executing a \$15
million overhauling project is routinely chosen over building a
brand-new \$75 million gas peaker asset.*
\[[1](https://uspeglobal.com/articles/power-plant-cost-per-mw-2026-epc-guide/),
[2](https://pgjonline.com/news/2026/july/natural-gas-plants-selling-at-half-the-cost-of-new-construction-report-finds)\]

If you are interested, we can look deeper into:

-   **Equivalent Operating Hours (EOH):** A single rapid start can equal
    20 to 50 hours of continuous steady-state operation in terms of
    thermal fatigue on hot-gas-path components.

**Technology Eras (Post-2000)**

-   **Aero-derivative Units (e.g., GE LM6000):** Built for rapid
    10-minute starts. These smaller units have highly modular
    components, allowing quick swap-outs that extend physical plant life
    past **40 years**.

-   **Heavy-Duty Frame Units (e.g., GE 7E/7F):** Larger peakers that
    take slightly longer to ramp. They require strict maintenance
    intervals based on start counts, typically hitting major mid-life
    overhauls at **900 to 1,200 starts**.

**Primary Drivers of Peaker Retirement**

-   **Battery Energy Storage (BESS) Competition:** Battery storage is
    rapidly replacing 4-hour gas peakers due to faster response times
    and falling capital costs, often forcing early economic retirements.
    \[[1](https://nextgpower.com/bess-vs-gas-peaker-plants-why-2026-is-the-economic-technical-tipping-point-for-grid-storage/)\]

-   **Environmental Regulations:** Peakers emit higher startup emissions
    per megawatt-hour than continuous plants. Local air quality permits
    and carbon caps frequently limit their allowable run-hours as they
    age.
    \[[1](https://www.psehealthyenergy.org/work/energy-storage-peaker-plant-replacement-project/)\]

-   **Fuel Availability:** Older peakers running on fuel oil face
    stricter environmental scrutiny and higher compliance costs than
    those utilizing natural gas.

### Modeler note

It may be possible to obtain a rough estimate number of starts for CT
plants by assuming they are operated during peak hours (3-4 hours each
time) using the monthly energy data.

---

# 8. Technology selection by scenario

*2026-09-10. Licensed [CC BY 4.0](../../LICENSE-DOCS).*

Which gas technology a scenario should build is **scenario-dependent**, because the marginal unit
does completely different work depending on how much clean generation surrounds it. Applying one
project-wide default produces the wrong capital cost in one direction or the other.

### The rule

| Scenario | Gas role | Technology | Capex basis |
|---|---|---|---|
| **Statutory Floor** (`S2`) | Bulk energy supply | **CCGT** | `lp_model.ccgt_capex_kw()`, $3,000/kW |
| **Build to Zero** (`S1`), **2045 Gas Exception** (`S1B`), **Distributed Build** (`S3`) | Residual gap-filling | **Simple-cycle peaker** | **MISSING — see gap below** |

### Evidence for the Statutory Floor being CCGT

Measured from the no-foresight dispatch across eight weather years
(`scripts/` gas capacity-factor analysis, Virginia-only load basis):

| Year | Gas MW | Fleet capacity factor | Hours running |
|---|---:|---:|---:|
| 2030 | 14,923 | 42.5% | 92.8% |
| 2035 | 18,861 | 42.3% | 82.3% |
| 2040 | 23,331 | 53.4% | 96.3% |
| 2045 | 24,382 | **57.6%** | **98.8%** |

At 42–58% capacity factor and online 82–99% of hours, this is baseload-adjacent duty. CCGT is
correct: lower heat rate and lower fuel cost per MWh, and the cycling-wear concern that motivates
the peaker rule does not apply to a unit that essentially never stops.

#### A superficially contrary result, and why it is wrong

Computing the capacity factor of the *top 2,503 MW slice* of the output stack gives 0.03–0.07% —
roughly thirty hours a year, which looks like pure peaking duty and suggests simple-cycle.

**That reading is an artifact of the calculation.** Taking the top slice of the output stack
implicitly assumes the incremental unit dispatches last. A new CCGT does not enter the merit order
at the bottom: at roughly 6,400 Btu/kWh against older simple-cycle units above 10,000, it enters
near the top and runs baseload, displacing *existing* less-efficient units into the peaking role.
An operations team adding capacity to a fleet already running 98.8% of hours builds the unit that
runs hard, not one sized for thirty hours a year.

So the incremental capacity for the Statutory Floor is CCGT, and the 2,503 MW eight-weather-year
uplift at 2045 costs approximately **$7.5 billion** at $3,000/kW.

### Why the VCEA scenarios differ

In Build to Zero and Distributed Build, gas is a small residual covering short gaps in a mostly
clean system. There the fleet genuinely is not running continuously, cycling wear is the binding
constraint on lifespan (see `Gas_turbine_lifespans_reference.md`), and simple-cycle is correct —
which is the rationale the standing rule in `new_peaker_ccgt_costs_by_size.md` already gives.

### Open gap: no simple-cycle capex exists in the code

A 2026-09-10 audit found:

- `lp_model.ccgt_capex_kw()` — $3,000/kW, cross-verified against Wood Mackenzie, EPRI and GridLab.
  Correct and current. **Note it is full installed project cost, not turbine equipment only** —
  the two differ by roughly 4x and are easy to conflate.
- `lp_model.CCGT_CAPEX_KW` — the stale $1,775/kW Lazard midpoint that Internal Debugging Log #49
  found in use while the correct function sat unused beside it. **Nothing references it now**;
  renamed 2026-09-10 to `CCGT_CAPEX_KW_DO_NOT_USE_SUPERSEDED` so misuse is self-evident (Rule 12.3).
- **No simple-cycle / peaker capex constant or function exists anywhere in the package.**

The unit costs in `new_peaker_ccgt_costs_by_size.md` ($713/kW F-Class, $1,175/kW aeroderivative,
$1,084/kW H-Class) predate the 2025–2026 price surge that moved the CCGT figure from $1,775 to
$3,000/kW. That same document cites GridLab's September 2025 survey showing simple-cycle costs
rising from $562/kW (2023) to $728–1,544/kW (2025). Using the older per-unit figures would
understate VCEA-scenario gas capital cost substantially.

**A current simple-cycle installed cost, sourced the way `ccgt_capex_kw()` was, is required before
the VCEA scenarios' gas capital cost can be considered defensible.** Flagged rather than
interpolated.

### Second gap: the cost pipeline is not in the repository

`compute_scenario2_costs.py` — the caller of `ccgt_capex_kw()` — is not present. The Statutory
Floor's cost side therefore cannot be run from a clean clone, only its dispatch side.

---

## Gap-driven technology matching — the method

**Proposed 2026-09-13.** Supersedes choosing CCGT-versus-CT by assumption, and is cheaper than
the MILP alternative.

### The idea

Rather than committing the technology split inside the LP, **let the LP find the gaps** — the hours
and MW where clean resources cannot meet demand — and then **characterise those gaps** by the
attributes that determine which machine fits.

| gap attribute | what it implies |
|---|---|
| **Duration**, hours per event | short → CT; sustained → CCGT |
| **Ramp needed**, MW/hour into and out of the event | steep → CT; gradual → CCGT tolerable |
| **Frequency**, events per year | drives capacity factor, hence the 28.1% crossover above |
| **Interval between events** | below 6 h a CCGT cannot cycle off and back — it must idle at minimum stable output |
| **Predictability** | whether cold-start time (CCGT 4–12 h, CT 10–30 min) matters |

### Why this beats putting capex in the LP

**No MILP required.** Minimum up/down time and start cost become **post-hoc tests against the gap
shape** rather than integer constraints in the optimisation. That avoids 43,800 binary variables.

**It answers a question the LP cannot.** An LP with capex returns a single MW split. This returns
the **distribution** — and the distribution is what says whether 7 GW should be CT, or whether it is
really 3 GW of CT plus 4 GW of something else.

**It can find gaps no gas technology fits.** If the analysis surfaces 60-hour events with 15 GW
ramps, that is a finding about **storage duration**, not gas, and the framing shifts entirely.

### The source — corrected, and it needs no new solve

**The gas dispatch column of an existing solve IS the gap profile.** Where gas is the only
dispatchable resource,

```
gas[t] = demand − nuclear − solar − wind − storage_discharge + storage_charge
```

which is the residual after clean supply and optimal storage cycling. That is the gap, by
definition.

| source series | valid? |
|---|---|
| **gas dispatch**, gas-inclusive solve | **yes — and preferred** |
| unserved, clean-only solve | yes, same residual under another name |
| unserved, gas-inclusive solve | **no — a double residual**, what gas *failed* to cover |

**Gas dispatch is preferred over a purpose-built clean-only solve**, not merely equivalent: with
unserved penalised at $100,000/MWh a clean-only solve has enormous incentive to build storage
rather than leave gaps, distorting the shape being measured. Gas at ~$47/MWh creates no such
distortion. It also means **every sweep point yields a gap profile with no extra solve.**

*An earlier version of this method required a clean-only solve and refused gas-inclusive input
entirely. That was aimed at the wrong failure.*

### Measured on Scenario 2, 2045 — and the finding is not what the method was built to find

| | |
|---|---:|
| gap events | 37 |
| gas runs | **8,632 of 8,760 hours — 98.5%** |
| longest single event | **4,200 hours** |
| events over 72 h | 13 events carrying **114.6 of 122.9 TWh** |
| annual CF | **62.4%** against a 28.1% crossover |

**At 34.7% clean, gas is not filling gaps — it is the system.** The CCGT/CT question is answered
decisively here (CCGT), but only because there is nothing peaky to serve.

**The method becomes informative at higher compliance levels**, where gas genuinely peaks. That is
what makes running it across the sweep worthwhile: watching the gap structure shift from baseload
to peaking *is* the answer to which technology fits.

Note that even at 98.5% utilisation the attributes disagree — 2 events fall below CCGT minimum up
time, 26 fall within 6 hours of the previous one, and 1 needs a steeper ramp than a CCGT delivers.
**Cost and operating constraints do not have to agree**, and the disagreement is a finding rather
than something to resolve by majority.

### The trap, and the run that avoids it

**Gap shape depends on what was already built.** A solve with 10 GW of gas dispatching freely shows
a different gap profile than one with none, because gas smooths its own gaps. Characterising gaps
from a gas-inclusive solve measures the residual *after* gas filled it — which says nothing about
what gas was needed for.

**So the gaps must come from a clean-only solve**: clean resources, no gas, **unserved energy
allowed**. The unserved profile *is* the gap profile.

### What to extract, per event

Start hour, duration, peak MW, total MWh, ramp in, ramp out, hours since the previous event, and
season. Then cluster. Two or three natural families are expected — short evening peaks, multi-day
winter events, and possibly a shoulder-season dunkelflaute — and **each family is matched against
the technology parameters in §5 and §7. The match, or the failure to match, is the finding.**

### Relationship to the other gas work

| | |
|---|---|
| §6A lifecycle costing | gives the **crossover CF** a matched family is tested against |
| §5 operating constraints | gives ramp, minimum up/down and start parameters to test against |
| issue #19 (gas as a build variable) | this method may show whether that is asking the right question at all |

**Residual value is a known gap in both.** Annualised capital assumes an asset earns over its full
life. A CT built in 2035 and stranded at 2045 under 100% compliance has been charged 10 years of a
30-year annuity, implicitly assuming the remaining 20 have value. **At 100% they do not.** Capital
must either be amortised over the years it actually runs — roughly 3× the annual charge — or the
stranding recognised as a write-off. This makes late-built gas look cheap when it is very expensive,
and argues against building in the 2035–2040 window.

---

# 9. Deriving gas_allowed_frac

**Update note:** Since this document was first written, export has been
removed from `build_problem()` entirely (see the appendix's A.9 for full
detail), and a data-verified existing gas fleet capacity cap (Schedule A/B)
is now applied alongside `gas_allowed_frac` at every checkpoint -- both
change the mechanics described below. The core numerical-search approach
still applies, but two things are materially different: (1) with export
gone, one of the three sources of demand-side/generation-side divergence
this document originally cited no longer applies, though storage
round-trip loss and curtailment still do, so a clean closed-form derivation
still isn't available; (2) with the capacity cap now also active, the
capacity constraint can become the binding limit on gas dispatch instead
of `gas_allowed_frac` itself -- when this happens, changing `frac` further
has no effect on the resulting share at all (confirmed directly: two
different frac values, 0.2915 and 0.3642, produced the identical resulting
share once capacity was the true binding constraint) -- worth checking for
this condition before continuing to iterate on frac if refinement seems to
stop responding.

### Why this can't be computed algebraically in one step

`gas_allowed_frac` is a generation-side LP input (the code's constraint bounds
gas as a share of nuclear+exist_solar+wind+new_solar, EXCLUDING storage
discharge). The actual RPS requirement is a demand-side target (clean share
of non-nuclear DEMAND). These only coincide exactly with zero storage
round-trip loss and zero curtailment -- neither of which holds here (export
itself is no longer a factor, per the update note above, but the other two
still create the same basic circularity).
The relationship between the two also depends on the LP's own solved output,
creating circularity that rules out a clean closed-form derivation.

### The working method: numerical search via linear extrapolation

1. Compute the target: `target = 1 - rps_clean_pct` (e.g., 0.41 clean at
   2030 -> target = 0.59 demand-side gas share of non-nuclear demand)
2. Get a smart starting guess: use the ratio (converged_frac/target) from
   the nearest already-solved checkpoint as a multiplier against the new
   target. This has consistently landed within ~10-15 percentage points of
   the true answer across all three checkpoints solved so far.
3. Solve once, check the actual resulting demand-side share (sum hourly `g`
   dispatch / non-nuclear demand -- NOT the `gascum` variable directly,
   watch units: `gascum` accumulates in GWh via a /1000 factor per hour,
   while raw `g[t]` is in MWh).
4. Get a second point (adjust the guess based on gap direction and rough
   local slope, ~1.7-2.9 has been typical -- wider range than before now
   that the capacity cap also interacts with this slope).
5. Linear-interpolate between the two closest, bracketing points -- this has
   converged to within 0.0001-0.0005 of the target on the first or second
   refinement in most cases, though slightly less tight than before the
   capacity cap was added (occasional 0.002-0.004 residual gaps now seen).
6. **NEW: if step 4/5 shows the resulting share unchanged across two
   different frac values, stop iterating on frac** -- this means the
   existing-fleet capacity cap, not the RPS percentage, is now the true
   binding constraint at this checkpoint, and no frac adjustment will
   change the outcome. This is itself an important finding (a genuine
   capacity shortfall), not just a converged answer -- see A.8.6 in the
   appendix for the standard response (overhaul/retain existing near-EOL
   plants, then new simple-cycle build if needed).

### Known convergence points (see derived_values_scenario1_checkpoints.csv)

**Superseded, export-enabled, uncapped values (pre-A.8/A.9):** Ratio
(converged_frac/target) was NOT stable across checkpoints -- 0.6149 (2030),
0.7100 (2035), 0.7738 (2040). These values no longer apply as starting
points now that export is removed and the capacity cap is active --
re-derive from scratch, or use the most recent post-A.9 converged values
as starting points instead once available.

### Timing

**Updated:** each solve now takes roughly 260-290 seconds (up from the
earlier 100-150 seconds), following the addition of curtailment/unserved-
energy variables (see A.11 in the appendix). Investigated and ruled out
cost-coefficient conditioning as the primary cause; the added
variables/constraints themselves are the more likely driver. Budget
accordingly -- 2-3 solves per checkpoint now means roughly 13-15 minutes
total when deriving a new gas_allowed_frac value, not 5-8.

---

# 10. Open items

1. ~~Aeroderivative/frame CT split~~ — **RESOLVED 2026-09-12** from EIA-860 per-unit nameplate.
   Entirely frame.
2. ~~Reconcile 8,195 against 9,362~~ — **RESOLVED 2026-09-12.** Not a gap: net summer capability
   versus nameplate, same fleet.
3. ~~Vintages for Possum Point, Chesterfield, Elizabeth River, Gravel Neck, Darbytown~~ —
   **RESOLVED**; EIA-860 carries per-unit Operating Year, and rungs are now assigned from it.
4. **A CT-specific VOM constant** — still open. `CCGT_VOM_MWH = 3.0` is used for peakers, which
   understates their marginal cost on top of the heat-rate question.
5. **The Dominion IRP PDFs in the project folder are truncated and unreadable** — no `/Root`
   object, confirmed with `pypdf` and `pdfplumber`. **No longer blocking**, since EIA-860 supplied
   what they would have, but other work may depend on them.
6. **Imports and scarcity pricing** (§5) — deferred as its own work set. Note the simplification
   established 2026-09-12: under LMP, an importer pays **its own node's price**, so modelling
   imports needs a DOM-node price rather than PJM's whole supply stack. That makes the import
   question and the scarcity-pricing question **the same question**, and a smaller one than first
   scoped. The remaining independent constraint is the **transfer limit** into the zone.
7. **Wire the merit order into the LP** — no longer blocked on data. This is now the next
   substantive step.
