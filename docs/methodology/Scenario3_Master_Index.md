# Scenario 3 — Master Index of Technical Working Files

Compiled 2026-08-25, direct user request, following the discovery that several actively-edited
files this session had never actually been shared. **Every file listed below has now been
presented and is accessible to you directly** — this index doesn't merge them, per your own
decision, but should make it possible to find the right one without opening several to search.

**A standing commitment going forward**: any file substantially edited in a session will be
re-presented at the end of that session (or sooner, on request), so this problem doesn't recur.

---

## 1. Primary tracking documents — start here for "what's the current state of X"

| File | What it is |
|---|---|
| **Scenario3_Scope_and_Gaps.md** | The main, actively-maintained tracker — full A/B/C/D taxonomy, every demand-side feature's status (quantified vs. open), the school-bus V2G comparison table, structural/methodological open questions (low-demand scenario, climate-demand translation). The single best starting point for "what do we know about X." |
| **Internal_Debugging_Log.md** | Chronological engineering journal, 100 numbered entries this session alone. Not a reference document — a record of what was done, in what order, including mistakes caught and corrected. Read this for *how* a finding was reached or *why* an earlier figure changed; read the Scope doc for the current answer itself. |
| **Scenario3_Technical_Notes.md** | An earlier working-notes file (predates tonight's session) — factual findings with clear provenance, compiled while the user was offline at the time. |
| **Technical_Official_Summary.md** / **Executive_Legislative_Summary.md** | Drafted deliverables — a technical cost-analysis summary (for VDOE/utility-modeler audiences) and an executive summary (for legislative audiences), both marked as working drafts, not final. |

## 2. A.2 / A.2-extended — demand response, DLC, and large C&I curtailment

| File | What it is |
|---|---|
| **Dominion_DLC_Program_Parameters_2026-08-24.md** | Real Dominion program details (Smart Thermostat Rewards, EV Charger Rewards, Water Energy Rewards) sourced directly from Dominion's own program pages — the factual basis for this project's A.2 modeling. |
| **Cross_Utility_VPP_Compensation_Comparison.md** | Residential battery/solar DR-VPP compensation compared across other utilities — direct follow-up to a concern that Dominion under-incentivizes DR relative to peers. |
| **Cross_State_Commercial_Curtailment_Incentive_Comparison.md** | The large-C&I equivalent — NY/CA/MA/NJ/WA/HI compared directly, plus a 19-state tracker (from CESA's own list) for future comparison work, plus the school-bus V2G program comparison table (Dominion, National Grid, Con Edison, GMP, SDG&E, La Plata). |
| **Dominion_VPP_Pilot_Research.md** | Dominion's own filed VPP pilot (HB2346/SB1100) — program design, timeline, the electric-school-bus-expansion component. |
| *(A.2-extended's own code module)* | `large_ci_curtailment_analysis/` in the LP package — the actual assumptions module + test suite (10 tests), including the avoided-cost cross-check against this project's own peaker-cost benchmarks. Not a markdown file; lives in the code package, not this outputs folder. |

## 3. A.3/A.4 — efficiency (PHIUS, HVAC, heat pump water heaters)

| File | What it is |
|---|---|
| **Appendix_Efficiency_Stock_Turnover_Model.md** | The full stock-turnover model — PHIUS Core envelope conservation + phased HVAC efficiency standards (SEER2/HSPF2/IEER), residential and school, 2026 onward. |

## 4. A.7 — data center demand flexibility

| File | What it is |
|---|---|
| **Appendix_DataCenter_DemandFlexibility_A7.md** | The full A.7 research — Dominion/PJM existing practice, PJM's proposed IRAS mechanism, Dominion's own LLDF program, the SCC/DCC joint working group, industry counter-proposals, GS-5 rate findings, phantom/speculative load, public opposition (Gallup/Texas), and broader AI-risk sentiment (MIT/Pew). 10 sections. |

## 5. Climate trends and weather-station methodology

| File | What it is |
|---|---|
| **Climate_Trends_and_Weather_Station_Methodology.md** | The full climate research thread — VCA findings, the wet-bulb/dry-bulb clarification, winter/polar-vortex nuance, the four-category weather-station framework (Sterling/Pennington Gap/Richmond/Norfolk/Suffolk Lake Kilby), the time-of-observation bias finding and its correction, and the direct connection to Dominion's own load-forecast methodology (the fixed-weather-template finding). 8 sections. |
| **Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md** | A related but distinct thread — three approaches to weather-year robustness for the LP model itself, built specifically to survive conversation compression. |

## 6. Dominion zone load-shape and LMP analysis

| File | What it is |
|---|---|
| **Dominion_Zone_Load_Shape_and_LMP_Analysis.md** | The peak/avg-ratio reversal finding, the real-time LMP avoided-energy-cost analysis (Loudoun/Tysons/Richmond/VA Beach/Southill), and the location-timing split (Northern VA summer peaks vs. Richmond/VA Beach winter peaks). |

## 7. Gas fleet / dispatch methodology (LP model internals, not demand-side)

| File | What it is |
|---|---|
| **new_peaker_ccgt_costs_by_size.md** | New gas peaker/CCGT cost benchmarks by size tier — used directly in the A.2-extended avoided-cost cross-check. |
| **Gas_turbine_lifespans_reference.md** | Estimated useful lifespans for CT peaker and CCGT assets — used for capital-recovery annualization. |
| **VA_gas_capacity_schedules.md** | Virginia's existing gas fleet, time-varying capacity schedules — two distinct schedules for two different purposes, not interchangeable. |
| **METHODOLOGY_gas_allowed_frac_derivation.md** | How `gas_allowed_frac` is derived for any checkpoint year in the LP model. |
| **Solve_Procedure_and_Requirements.md** | Standing checklist of what a competed solve needs to satisfy, built after repeatedly discovering issues after the fact. |
| **Software_Engineering_Standards.md** | Standing coding rules for this project's own codebase. |

## 8. Broader whitepaper structure / appendices

| File | What it is |
|---|---|
| **Reorganized_Appendices_Draft_updated.md** | The structural first draft of the full appendix organization for the whitepaper itself. |
| **Reorganized_Appendices_Draft.md** | An earlier version of the same — kept for reference; the "_updated" version supersedes it. |
| **Appendix_P_Working_Draft.md** | A separate, editable working copy of Appendix P (Solve Procedure and Requirements), pulled out for direct editing. |
| **Appendix_Agrivoltaics.md** | Agrivoltaics as a complementary benefit to Virginia's farming communities — supports Scenario 3's own Part D.c design. |

## 9. Reference / methodology / meta

| File | What it is |
|---|---|
| **Acronym_List.md** | Comprehensive acronym reference across all of this project's own documentation. |
| **Scenario3_Literature_Search_Citations_2026-08-23.md** | Full citation list for a specific day's research passes (NY/CA/MA/MD/WA/HI/Germany/IL lessons-learned search). |
| **CA_NY_PJM_Reliability_Compliance_Comparison_2026-08-23.md** | How California, New York, and PJM/Virginia separate reliability planning from clean-energy compliance — every claim verified against a primary source. |

---

## A note on completeness

This index covers every `.md` working file found in this project's own session-local directory as
of 2026-08-25, cross-checked against what had already been shared in prior sessions. One file was
deliberately excluded: an older `session_handoff_summary.md` (dated Aug. 14), confirmed earlier
this session to be from an unrelated prior thread about LP model mechanics, not part of this
project's own current Scenario 3 documentation.

If a future session creates new working files, they should be added here directly, and the file
itself presented at the same time — not just edited and left in the session-local directory the
way tonight's files were before this correction.
