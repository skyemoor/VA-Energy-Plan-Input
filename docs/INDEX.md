# Documentation Index — by domain

**Check this before starting any task.** Its purpose is to prevent work being redone or built in
parallel to what already exists. Two such collisions occurred on 2026-09-11 alone: a gas fleet note
was written without checking `docs/research/`, which already held a gas turbine lifespans
reference; and an extended discussion of wholesale market arbitrage proceeded without consulting
`DERA_VPP_WMA_Consolidated_Working_Notes.md`, which had already resolved several of the questions
being asked.

Files are listed under the domain they *belong* to, not the folder they happen to sit in.
`docs/research/`, `docs/methodology/` and `docs/` are all in scope.

Last updated 2026-09-11.

---

## Gas fleet & thermal generation — **7 files, fragmented**

| file | covers |
|---|---|
| **`methodology/Gas_Fleet_Working_Notes.md`** | **START HERE.** Definitions, heat rate tiers, capacity per rung, cost structure, what sits above the merit order |
| `methodology/Gas_Merit_Order.md` | Heat rate tiers, EIA sourcing (subsumed by the above) |
| `methodology/VA_gas_capacity_schedules.md` | Retirement schedules A and B — **authoritative for retirements** |
| `methodology/Gas_Technology_Selection_By_Scenario.md` | Which gas technology each scenario assumes |
| `methodology/METHODOLOGY_gas_allowed_frac_derivation.md` | Gas fraction derivation for the LP |
| `research/Gas_turbine_lifespans_reference.md` | Turbine lifespans, EOH thresholds, overhaul windows |
| `research/new_peaker_ccgt_costs_by_size.md` | Peaker and CCGT capex by plant size; Tenaska/Ladysmith overhaul analysis |

**Consolidation needed.** Seven files, overlapping. `Gas_Fleet_Working_Notes.md` was created as the
entry point but does not yet absorb the lifespans or capex material.

---

## DER / VPP / WMA / demand response — **6 files, fragmented**

| file | covers |
|---|---|
| **`research/DERA_VPP_WMA_Consolidated_Working_Notes.md`** | **START HERE.** NYISO vs PJM structural comparison, Order 2222 timelines, self-aggregation paths, value stacking |
| `research/Dominion_VPP_Pilot_Research.md` | Dominion's own VPP pilot filing |
| `research/ThirdParty_VPP_DERA_Compensation_Benchmarks.md` | Third-party DERA compensation |
| `research/Cross_Utility_VPP_Compensation_Comparison.md` | Cross-utility VPP comparison |
| `research/Dominion_DLC_Program_Parameters_2026-08-24.md` | Direct load control program terms |
| `research/Cross_State_Commercial_Curtailment_Incentive_Comparison.md` | C&I curtailment incentives by state |

**Three findings here that constrain Scenario 3 and are easy to miss:**

- **PJM's Order 2222 DER Aggregator model is not operational until Feb 2028** (energy/ancillary);
  2028/29 BRA for capacity. The legacy **CSP / Emergency Load Response** path *is* live today and
  self-registrable.
- **Energy-market aggregations must sit at a single PJM pricing node.** Capacity and ancillary
  services may aggregate across nodes; **energy may not.** A distributed fleet scattered across a
  county cannot bid as one block for energy arbitrage.
- **≤5 MW per Component DER** in PJM.

---

## Scenario 3 — **5 files, 381 KB, fragmented**

| file | covers |
|---|---|
| `methodology/Scenario3_Master_Index.md` | Scenario 3's own index |
| `methodology/Scenario3_Technical_Notes.md` | Technical decisions, foresight bracketing, flat-dual measurement |
| `methodology/Scenario3_Scope_and_Gaps.md` | 246 KB — scope and open gaps |
| `methodology/Scenario3_Model_Plain_Language_Guide.md` | Plain-language explanation |
| `research/Scenario3_Literature_Search_Citations_2026-08-23.md` | Literature citations |

---

## Statutes — 9 files

`docs/statutes/` — § 10.1-1197.5 (agrivoltaics definition), § 15.2-2288.8 (solar zoning),
§ 45.2-1701, § 45.2-1702, § 45.2-1706.1 (Clean Energy Policy — **no agrivoltaic definition**),
§ 45.2-1710, § 56-585.1-4, § 56-585.5 (RPS), plus a README.

---

## Agrivoltaics & rural economics — 4 files

| file | covers |
|---|---|
| **`methodology/Agrivoltaics_Evidence_Base.md`** | **START HERE.** Findings, crop compatibility, configurations, SLCOE, full citations |
| `appendices/Appendix_Agrivoltaics.md` | Narrative appendix: statutory context, regional practice |
| `methodology/Cover_Crops_and_Agrivoltaics.md` | Cover crops, double-counting correction, Virginia policy hooks |
| `methodology/NSPM_Rural_Economic_Development.md` | NSPM benefit channels, lease income, revenue share |

---

## Distributed solar siting — 2 files

| file | covers |
|---|---|
| `Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md` | Four-county siting assessment |
| `methodology/Parking_Reference_Basis_Working_Notes.md` | Parking canopy basis, data vintage limitation |

---

## Reliability, reserves & firming — 2 files

| file | covers |
|---|---|
| `research/CA_NY_PJM_Reliability_Compliance_Comparison_2026-08-23.md` | **Check before any CAISO/NYISO reserve work** |
| `research/Dominion_FRR_RPM_Status.md` | **Which capacity construct Dominion operates under** — FRR terminated May 2024, currently RPM; what that means for self-supply assumptions |
| **`methodology/Reserves_Approach.md`** | **START HERE for reserves.** Reader-facing: what is modelled, what is not, and why |
| `research/CAISO_Net_Load_Treatment.md` | **How CAISO sizes reserves against net load** — two parallel requirements, flexible capacity, Flexible Ramping Product |
| `methodology/Six_Day_Lookahead_Firming_Documentation.md` | Six-day lookahead firming methodology |

Also: `Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md` documents three reserve
enforcement approaches and names **1c (all-hours, LP-integrated) as current standard** —
implemented in `lp_package/all_hours_reserve.py`, **which nothing calls.** See
`MODEL_WIDE_FINDINGS.md`.

---

## Pricing & LMP — 1 file

`research/Dominion_Zone_Load_Shape_and_LMP_Analysis.md` — load-duration analysis, real-time LMP,
location-timing split. **Check before any LMP or price-formation work.**

---

## Demand & RPS compliance — 1 file

`methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md` — demand basis, Virginia-only share,
RPS compliance accounting.

---

## Weather & climate — 2 files

`Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md`;
`methodology/Climate_Trends_and_Weather_Station_Methodology.md`.

---

## Data centers & efficiency — 2 files

`appendices/Appendix_DataCenter_DemandFlexibility_A7.md` (106 KB);
`appendices/Appendix_Efficiency_Stock_Turnover_Model.md`.

---

## Model-wide status — 4 files

| file | covers |
|---|---|
| **`MODEL_WIDE_FINDINGS.md`** | **Read before interpreting any result.** Flat energy dual, dormant reserve constraint, no imports, foresight asymmetry |
| `PIPELINE_COMPLETENESS.md` | What runs, what doesn't, deferred items |
| `SCENARIO_NAMES.md` | Scenario naming conventions |
| `README.md` | Documentation licence and partial file list |

---

## Work tracking & process

| file | covers |
|---|---|
| **`process/Work_Tracking_Migration_Plan.md`** | **Proposed move from the xlsx tracker to GitHub Issues** — label scheme, mapping of open items, sequence. Draft, nothing migrated |
| `scripts/audit_documented_fixes.py` | Hourly session check that documented fixes are still true of the code |

---

## Process & standards — **8 files, 689 KB, fragmented**

| file | covers |
|---|---|
| `Software_Engineering_Standards.md` | Standing code rules — **read before writing code** |
| `claude.md`, `claudeRationale.md` | Working process conventions |
| `Common_Mistake_Log.md` | Recurring errors and how to avoid them |
| `Internal_Debugging_Log.md` | 474 KB — numbered record of problems and resolutions |
| `Data_Sourcing_Log.md` | 177 KB — provenance log |
| `DATA_SOURCES.md` | External data provenance summary |
| `Acronym_List.md` | Acronyms |

---

## Deliverables

`appendices/Reorganized_Appendices_Draft_updated.md`; `deliverables/` holds the whitepaper outline
and summaries.

---

## Consolidation candidates, in priority order

1. **Gas fleet (7 files)** — absorb lifespans and capex material into `Gas_Fleet_Working_Notes.md`,
   leaving `VA_gas_capacity_schedules.md` authoritative for retirements only.
2. **DER/VPP/WMA (6 files)** — the consolidated note already exists and is good; the other five
   should be cross-referenced from it rather than merged, since each is a distinct research pass.
3. **Scenario 3 (381 KB)** — `Scope_and_Gaps.md` alone is 246 KB and likely holds resolved items
   that belong in the technical notes or can be retired.

---

## Task tracking — **GitHub Issues**

**Open work lives in GitHub Issues** as of 2026-09-12:
`github.com/skyemoor/VA-Energy-Plan-Input/issues`

Labels: `scenario:N` / `common` for scope (an issue can carry both), `domain:X` mirroring this
index, state (`decision-needed`, `blocked`, `needs-data`, `in-progress`) and kind (`finding`,
`defect`, `regression`, `research`, `deliverable`). Priority is a **milestone**, so it sorts.

`registers/Virginia_Grid_Analysis_Tracker_updated.xlsx` is now an **archive of closed items**.

The xlsx went un-updated through the whole of 2026-09-11 despite that session producing eight
trackable items, which is part of why open tracking moved: **commits can close issues** with
`Fixes #N`, so the work and the record stop being separate artifacts.

Current P1: **#1** flat hourly energy dual (2045 unmeasured); **#2** `all_hours_reserve.py` exists
but is never called.

---

## How to use this index

Before starting work in a domain, read the **START HERE** file for that domain if one is marked,
and scan the others for overlap. If a domain has no START HERE file and more than three entries,
that is itself a signal the domain needs consolidating before more is added to it.
