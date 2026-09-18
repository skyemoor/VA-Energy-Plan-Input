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

## Gas fleet & thermal generation — **consolidated**

| file | covers |
|---|---|
| **`methodology/Gas_Consolidated_Reference.md`** | **EVERYTHING GAS.** Definitions, heat rates and merit order, capacity by rung and plant, retirement schedules, operating constraints, new-build capex by size tier, lifespans and EOH, technology selection by scenario, deriving `gas_allowed_frac`, open items |

The seven previous gas documents were **merged 2026-09-13** and remain as stubs pointing at the
consolidated file, so existing links resolve:
`METHODOLOGY_gas_allowed_frac_derivation.md`, `research/Gas_turbine_lifespans_reference.md`,
`research/new_peaker_ccgt_costs_by_size.md`, `Gas_Fleet_Working_Notes.md`, `Gas_Merit_Order.md`,
`VA_gas_capacity_schedules.md`, `Gas_Technology_Selection_By_Scenario.md`.

**Why:** the CT capex figures the project needed ($713–1,175/kW by class) were sitting in
`new_peaker_ccgt_costs_by_size.md` while `Gas_Technology_Selection_By_Scenario.md` recorded *"no
simple-cycle capex exists in the code"* as an open gap. Two files, opposite claims, neither aware
of the other.

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

`docs/statutes/` — § 10.1-1197.5 (agrivoltaics definition), # 15.2-2288.8 (solar zoning),
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
| **`appendices/APPENDIX_ORDER.md`** | **PROPOSED APPENDIX SEQUENCE** — reader order, what each draws from, and what must be merged or assembled first |
| **`appendices/Appendix_Resource_Adequacy_Methodology.md`** | Accreditation and reserve-margin method — the fullest account; partly superseded by `Common_Reference.md` sections 2-3 |
| **`appendices/Appendix_Cost_Assumptions.md`** | Cost assumptions and levelisation |
| **`appendices/Appendix_Scenario2_Methodology.md`** | How Scenario 2 was constructed — METHOD current, FIGURES superseded |
| **`appendices/Appendix_DER_Owner_Economics.md`** | DER owner economics, for Scenario 3 |
| **`appendices/Appendix_Known_Limitations.md`** | Known limitations (stub) |
| **`appendices/Appendix_Q_Gas_Capacity_Method.md`** | **Gas capacity expansion** — brownfield screening curve method, LEEMA cost formulas, what the method does not support, and how results are presented |
| **`scenarios/Scenario1_Working_Document.md`** | **Scenario 1 working document** — result, build trajectory, curtailment, foresight comparison, solver structure |
| **`scenarios/Scenario1B_Working_Document.md`** | **Scenario 1B working document** — the 5% ceiling, gas capacity, checkpoint structure |
| **`scenarios/Scenario2_Working_Document.md`** | **Scenario 2 working document** — result, storage, gas capacity, solve path, resolved blockers |
| **`scenarios/Scenario3_Working_Document.md`** | **Scenario 3 working document** — siting, agrivoltaics, DER economics, transmission deferral |
| **`registers/Master_Citations.xlsx`** | **THE CITATION REGISTER** — 119 sourced citations, keyed C001 onward, with topics, evidence type, verification status and URLs. Every sourced finding goes here |
| **`Citation_Taxonomy_Proposal.md`** | The topic taxonomy the register's Primary/Secondary Topics columns use |
| **`build.log`** | **What changed, when** — chronological, one entry per file modified. Lightweight; the WHY lives in the debugging log |
| **`whitepaper/Executive_Summary_Draft.md`** | **EXEC SUMMARY DRAFT** — written against Scenario 2 alone to fix voice and register; compliance curve pending |
| **`whitepaper/Whitepaper_Outline.md`** | **THREE-LAYER STRUCTURE** — executive summary, technical summary, body. Scenario 2's results in place, everything else marked pending |
| **`Common_Reference.md`** | **CROSS-CUTTING FACTS AND CONVENTIONS** — quantities and unit bases shared across every scenario, defined once. Section 1: transmission and distribution |
| **`Scenario_Completion_Dashboard.md`** | **WHERE EACH SCENARIO STANDS** — every step, its status, and the issue numbers blocking it |
| **`whitepaper/Scenario2_Section_Draft.md`** | **Whitepaper draft section for Scenario 2** — modelled figures, with the conflicts against the existing draft text flagged |
| **`Session_Handoff_2026-09-14.md`** | **START HERE** — Scenario 2 complete at steps 1–11, the LP restructuring in flight, open items in blocking order |
| `Session_Handoff_2026-09-13.md` | Prior handoff — superseded |
| | |
| **Appendices state the END PRODUCT.** What changed and why belongs in `Internal_Debugging_Log.md`. An appendix carrying a correction narrative is telling the reader about the process instead of the result — a whitepaper reader wants the finding, not its history. Where a result is not yet re-measured, the appendix says so plainly and points at the runner; it does not narrate the defect. | |
| | |
| **`appendices/APPENDIX_ORDER.md`** | **THE AGREED SEQUENCE** — sixteen entries in reader order (methods, scenarios, topics, reference), what each draws from, and the appendices/working-documents division |
| **`appendices/Appendix_Resource_Adequacy_Methodology.md`** | 86 KB — the fullest account of accreditation and reserve margin. Extracted 2026-09-14; predates the capacity-planning vs resource-adequacy distinction |
| `appendices/Appendix_Cost_Assumptions.md` | Cost assumptions and levelisation. Extracted 2026-09-14 |
| `appendices/Appendix_Scenario2_Methodology.md` | How Scenario 2 was constructed — METHOD current, FIGURES awaiting migration from the working document |
| `appendices/Appendix_DER_Owner_Economics.md` | DER owner economics, for Scenario 3. Extracted 2026-09-14 |
| `appendices/Appendix_Known_Limitations.md` | Known limitations — stub, to be assembled |
| **`appendices/Appendix_Q_Gas_Capacity_Method.md`** | **Brownfield screening curve** — how new gas capacity is sized and costed on the four-term formulation |
| `appendices/Appendix_D_Tiered_Social_Cost.md` | Tier 1/2/3 framework — full methodology and sourcing (P.2 #9 points here) |
| `appendices/Appendix_M_Reference_Literature.md` | Reference literature |
| `appendices/Appendix_N_Scenario_1B.md` | Scenario 1B methodology |
| **`appendices/Appendix_O_Intermediate_Year_Demand_Shape.md`** | **Data-centre flattening methodology** — cited normatively by P.2 #7 |
| **`appendices/Appendix_P_Solve_Procedure.md`** | **THE SOLVE REQUIREMENTS.** Seventeen rules applying to every scenario and every solve, plus disclosed gaps |
| **`methodology/Scenario_Restructuring_Compliance_Sweep.md`** | **START HERE for the whitepaper's structure** — compliance as the axis, the counterfactual, what the sweep drops |
| `methodology/Scenario2_Runnability_Audit.md` | Why the baseline scenario is not currently runnable — three blockers |
| **`methodology/Compliance_Definition_For_Sweep.md`** | **What the sweep axis means** — clean generation share vs statutory RPS, and why they differ by ~38% |
| **`methodology/Experiment_Pathway_Foresight.md`** | **Myopic chain vs target-first** — the taxonomy, the literature (14–23% myopia penalty), and the open experiment |
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
| `Session_Journal.md` | Catalogue of the eleven working sessions since 2026-09-09. Snapshot of a container-side file; goes stale |
| `Internal_Debugging_Log.md` | 474 KB — numbered record of problems and resolutions |
| `Data_Sourcing_Log.md` | 177 KB — provenance log |
| `DATA_SOURCES.md` | External data provenance summary |
| `Acronym_List.md` | Acronyms |

---

## Deliverables

`deliverables/` holds the whitepaper outline
and summaries.

---

## Consolidation candidates, in priority order

**Done.** Gas — seven files merged into `methodology/Gas_Consolidated_Reference.md` (2026-09-13).
Appendices — two composite drafts removed and five draft-only appendices extracted to standalone
files (2026-09-14); `appendices/APPENDIX_ORDER.md` holds the agreed sequence.

**A caution from the gas merge**, worth carrying into the next one: it dropped a scope qualifier.
The standing simple-cycle rule opens *"For Scenario 1, 1B, 3, 3B, and 3C specifically (NOT Scenario
2…)"*, and the merged text starts after that parenthesis — leaving a rule that reads as universal
and is not. It produced a reported conflict that did not exist. **When merging, treat every "for X
specifically", "NOT Y" and "except where" as load-bearing and check it survives.**

1. **Scenario 3 (381 KB)** — `methodology/Scenario3_Scope_and_Gaps.md` alone is 246 KB and likely
   holds resolved items. Blocked behind issue #14 in any case.
2. **DER / VPP / WMA (6 files)** — becomes Appendix H, and the policy material outside the
   repository needs locating first.
3. **Process & standards (8 files, 689 KB)** — overlapping guidance on how the project works.

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
